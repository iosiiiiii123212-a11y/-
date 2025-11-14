# IMPORTANT: eventlet monkey_patch must be called BEFORE importing other modules
import eventlet
eventlet.monkey_patch()

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_socketio import SocketIO, emit, join_room, leave_room
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import json
import os
import base64
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-change-this-in-production')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
socketio = SocketIO(app, cors_allowed_origins="*", max_http_buffer_size=16 * 1024 * 1024)

# Database files
USERS_FILE = 'users.json'
MESSAGES_FILE = 'messages.json'
GROUPS_FILE = 'threads.json'

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

def load_messages():
    if os.path.exists(MESSAGES_FILE):
        with open(MESSAGES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_messages(messages):
    with open(MESSAGES_FILE, 'w', encoding='utf-8') as f:
        json.dump(messages, f, ensure_ascii=False, indent=2)

def cleanup_orphaned_messages():
    """Remove messages from deleted threads"""
    messages = load_messages()
    threads = load_groups()
    thread_ids = {t['id'] for t in threads}
    
    # Keep only messages that belong to existing threads
    cleaned_messages = [msg for msg in messages if msg.get('group_id') in thread_ids]
    
    if len(cleaned_messages) != len(messages):
        save_messages(cleaned_messages)
        print(f"Cleaned up {len(messages) - len(cleaned_messages)} orphaned messages")

def load_groups():
    if os.path.exists(GROUPS_FILE):
        with open(GROUPS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def get_thread_stats(thread_id):
    """Get statistics for a thread"""
    messages = load_messages()
    
    # Count messages in this thread
    message_count = sum(1 for msg in messages if msg.get('group_id') == thread_id)
    
    # Get view count (if exists)
    threads = load_groups()
    thread = next((t for t in threads if t['id'] == thread_id), None)
    view_count = thread.get('view_count', 0) if thread else 0
    
    return {
        'message_count': message_count,
        'view_count': view_count
    }

def save_groups(groups):
    with open(GROUPS_FILE, 'w', encoding='utf-8') as f:
        json.dump(groups, f, ensure_ascii=False, indent=2)

def init_admin():
    """Initialize admin user if not exists"""
    users = load_users()
    if 'מנהל' not in users:
        users['מנהל'] = {
            'password': generate_password_hash('IOSEP@@123212'),
            'phone': 'מנהל מערכת',
            'status': 'מנהל',
            'profile_pic': '👑',
            'profile_color': '#ff0000',
            'created_at': datetime.now().isoformat(),
            'followers': [],
            'following': [],
            'is_admin': True,
            'blocked': False,
            'blocked_ips': []
        }
        save_users(users)

def is_admin():
    """Check if current user is admin"""
    if 'username' not in session:
        return False
    users = load_users()
    return users.get(session['username'], {}).get('is_admin', False)

def is_ip_blocked(ip):
    """Check if IP is blocked"""
    users = load_users()
    for user_data in users.values():
        if ip in user_data.get('blocked_ips', []):
            return True
    return False

@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('chat'))
    return redirect(url_for('login'))

@app.route('/health')
def health_check():
    """Health check endpoint for keep-alive pings"""
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now().isoformat(),
        'message': 'Server is alive! 🚀'
    }), 200

@app.route('/ping')
def ping():
    """Simple ping endpoint"""
    return 'pong', 200

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Check if IP is blocked
        ip = request.remote_addr
        if is_ip_blocked(ip):
            return jsonify({'success': False, 'message': 'כתובת ה-IP שלך חסומה'})
        
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        phone = data.get('phone', '')
        
        users = load_users()
        
        if username in users:
            return jsonify({'success': False, 'message': 'שם המשתמש כבר קיים'})
        
        # Generate profile color based on username
        colors = ['#e91e63', '#9c27b0', '#673ab7', '#3f51b5', '#2196f3', 
                  '#00bcd4', '#009688', '#4caf50', '#ff9800', '#ff5722']
        color_index = sum(ord(c) for c in username) % len(colors)
        
        users[username] = {
            'password': generate_password_hash(password),
            'phone': phone,
            'status': 'Available',
            'profile_pic': '👤',
            'profile_color': colors[color_index],
            'created_at': datetime.now().isoformat(),
            'followers': [],
            'following': [],
            'blocked': False
        }
        
        save_users(users)
        return jsonify({'success': True, 'message': 'נרשמת בהצלחה!'})
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        users = load_users()
        
        if username not in users:
            return jsonify({'success': False, 'message': 'שם משתמש או סיסמה שגויים'})
        
        if check_password_hash(users[username]['password'], password):
            session['username'] = username
            return jsonify({'success': True})
        
        return jsonify({'success': False, 'message': 'שם משתמש או סיסמה שגויים'})
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/chat')
def chat():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    users = load_users()
    user_data = users.get(session['username'], {})
    user_is_admin = user_data.get('is_admin', False)
    user_is_blocked = user_data.get('blocked', False)
    
    return render_template('chat.html', 
                         username=session['username'], 
                         is_admin=user_is_admin,
                         is_blocked=user_is_blocked)

@app.route('/api/unread-counts')
def get_unread_counts():
    """Get unread message counts for all threads"""
    if 'username' not in session:
        return jsonify({'success': False}), 401
    
    username = session['username']
    messages = load_messages()
    threads = load_groups()
    
    unread_counts = {}
    for thread in threads:
        thread_id = thread['id']
        unread_count = 0
        
        for msg in messages:
            if msg.get('group_id') == thread_id:
                # Count messages not from this user and not read by this user
                if msg.get('from') != username:
                    read_by = msg.get('read_by', [])
                    if username not in read_by:
                        unread_count += 1
        
        unread_counts[thread_id] = unread_count
    
    return jsonify({'success': True, 'unread_counts': unread_counts})

@app.route('/api/threads', methods=['GET', 'POST'])
def handle_threads():
    if 'username' not in session:
        print("❌ User not logged in trying to access threads")
        return jsonify({'success': False, 'message': 'לא מחובר'}), 401
    
    username = session['username']
    
    if request.method == 'POST':
        print(f"📝 User '{username}' creating new thread")
        data = request.get_json()
        thread_title = data.get('title', '').strip()
        thread_content = data.get('content', '').strip()
        
        if not thread_title:
            return jsonify({'success': False, 'message': 'נושא השיחה לא יכול להיות ריק'})
        
        if not thread_content:
            return jsonify({'success': False, 'message': 'תוכן השיחה לא יכול להיות ריק'})
        
        groups = load_groups()
        thread_id = f"thread_{len(groups) + 1}_{datetime.now().timestamp()}"
        
        new_thread = {
            'id': thread_id,
            'title': thread_title,
            'content': thread_content,
            'created_by': session['username'],
            'created_at': datetime.now().isoformat()
        }
        
        groups.append(new_thread)
        save_groups(groups)
        
        # Create initial message with thread content
        messages = load_messages()
        users = load_users()
        profile_color = users.get(session['username'], {}).get('profile_color', '#00a884')
        
        initial_message = {
            'id': f"{session['username']}_{datetime.now().timestamp()}",
            'from': session['username'],
            'group_id': thread_id,
            'message': thread_content,
            'type': 'text',
            'image': None,
            'timestamp': datetime.now().isoformat(),
            'read': False,
            'likes': [],
            'dislikes': [],
            'is_thread_post': True,
            'profile_color': profile_color
        }
        messages.append(initial_message)
        save_messages(messages)
        
        # Broadcast new thread to all users
        socketio.emit('thread_created', {
            'thread': new_thread,
            'initial_message': initial_message
        })
        
        return jsonify({'success': True, 'thread': new_thread})
    
    # GET request
    print(f"📋 User '{username}' requesting threads list")
    threads = load_groups()
    users = load_users()
    thread_list = []
    for thread in threads:
        creator = thread.get('created_by', 'Unknown')
        # Ensure user exists and has profile_color
        if creator in users:
            profile_color = users[creator].get('profile_color', '#00a884')
        else:
            profile_color = '#00a884'
        
        thread_list.append({
            'id': thread['id'],
            'title': thread['title'],
            'created_by': creator,
            'profile_color': profile_color,
            'view_count': thread.get('view_count', 0)
        })
    
    print(f"✅ Returning {len(thread_list)} threads to user '{username}'")
    return jsonify({'success': True, 'threads': thread_list})

@app.route('/api/messages/<group_id>')
def get_messages(group_id):
    if 'username' not in session:
        print(f"❌ User not logged in trying to access messages for {group_id}")
        return jsonify({'success': False, 'message': 'לא מחובר'}), 401
    
    username = session['username']
    print(f"📨 User '{username}' requesting messages for thread '{group_id}'")
    
    # Verify thread exists
    threads = load_groups()
    thread_exists = any(t['id'] == group_id for t in threads)
    
    if not thread_exists:
        print(f"❌ Thread '{group_id}' does not exist")
        return jsonify({'success': False, 'message': 'השיחה לא קיימת'}), 404
    
    messages = load_messages()
    users = load_users()
    
    group_messages = []
    for msg in messages:
        if msg.get('group_id') == group_id:
            # Add user profile info to message
            msg_username = msg.get('from')
            if msg_username in users:
                msg['profile_color'] = users[msg_username].get('profile_color', '#00a884')
            else:
                msg['profile_color'] = '#00a884'
            
            # Mark message as read by this user
            if 'read_by' not in msg:
                msg['read_by'] = []
            if username not in msg['read_by'] and msg_username != username:
                msg['read_by'].append(username)
            
            group_messages.append(msg)
    
    # Save updated read status
    save_messages(messages)
    
    print(f"✅ Returning {len(group_messages)} messages for thread '{group_id}'")
    return jsonify({'success': True, 'messages': group_messages})

# Track users viewing each thread
active_viewers = {}  # {thread_id: {username: timestamp}}

@socketio.on('connect')
def handle_connect():
    if 'username' in session:
        join_room(session['username'])
        emit('connected', {'username': session['username']})

@socketio.on('join_thread')
def handle_join_thread(data):
    """User joined a thread - notify others"""
    if 'username' not in session:
        return
    
    thread_id = data.get('thread_id')
    username = session['username']
    
    if thread_id:
        # Add user to viewers
        if thread_id not in active_viewers:
            active_viewers[thread_id] = {}
        active_viewers[thread_id][username] = datetime.now().isoformat()
        
        # Increment view count for this thread
        threads = load_groups()
        for thread in threads:
            if thread['id'] == thread_id:
                if 'view_count' not in thread:
                    thread['view_count'] = 0
                thread['view_count'] += 1
                save_groups(threads)
                break
        
        # Get thread stats
        stats = get_thread_stats(thread_id)
        
        # Broadcast to all users in this thread
        emit('viewers_update', {
            'thread_id': thread_id,
            'viewers': list(active_viewers[thread_id].keys()),
            'stats': stats
        }, broadcast=True)

@socketio.on('leave_thread')
def handle_leave_thread(data):
    """User left a thread - notify others"""
    if 'username' not in session:
        return
    
    thread_id = data.get('thread_id')
    username = session['username']
    
    if thread_id and thread_id in active_viewers:
        # Remove user from viewers
        if username in active_viewers[thread_id]:
            del active_viewers[thread_id][username]
        
        # Clean up empty threads
        if not active_viewers[thread_id]:
            del active_viewers[thread_id]
        
        # Broadcast to all users
        viewers = list(active_viewers[thread_id].keys()) if thread_id in active_viewers else []
        emit('viewers_update', {
            'thread_id': thread_id,
            'viewers': viewers
        }, broadcast=True)

@socketio.on('send_message')
def handle_message(data):
    if 'username' not in session:
        return
    
    # Verify thread exists
    threads = load_groups()
    thread_id = data.get('to')
    thread_exists = any(t['id'] == thread_id for t in threads)
    
    if not thread_exists:
        emit('message_error', {'message': 'השיחה לא קיימת יותר'})
        return
    
    users = load_users()
    user_data = users.get(session['username'], {})
    
    # Check if user is blocked
    if user_data.get('blocked', False):
        emit('message_error', {'message': 'אתה חסום ולא יכול לשלוח הודעות'})
        return
    
    profile_color = user_data.get('profile_color', '#00a884')
    user_is_admin = user_data.get('is_admin', False)
    
    message = {
        'id': f"{session['username']}_{datetime.now().timestamp()}",
        'from': session['username'],
        'group_id': data['to'],
        'message': data['message'],
        'type': data.get('type', 'text'),  # text, image, link
        'image': data.get('image'),
        'timestamp': datetime.now().isoformat(),
        'read': False,
        'likes': [],
        'dislikes': [],
        'profile_color': profile_color,
        'is_admin': user_is_admin
    }
    
    messages = load_messages()
    messages.append(message)
    save_messages(messages)
    
    # Broadcast to all users in the group
    emit('receive_message', message, broadcast=True)

@socketio.on('react_message')
def handle_reaction(data):
    if 'username' not in session:
        return
    
    # Verify user exists
    users = load_users()
    if session['username'] not in users:
        emit('message_error', {'message': 'משתמש לא נמצא'})
        return
    
    # Check if user is blocked
    if users[session['username']].get('blocked', False):
        emit('message_error', {'message': 'אתה חסום ולא יכול להגיב'})
        return
    
    message_id = data['message_id']
    reaction = data['reaction']  # 'like' or 'dislike'
    user_is_admin = data.get('is_admin', False)
    
    messages = load_messages()
    
    for msg in messages:
        if msg.get('id') == message_id:
            username = session['username']
            
            # Regular users can't like their own messages
            if not user_is_admin and msg.get('from') == username:
                emit('reaction_error', {'message': 'לא ניתן לתת לייק להודעה שלך'})
                return
            
            # Initialize lists if needed
            if 'likes' not in msg:
                msg['likes'] = []
            if 'dislikes' not in msg:
                msg['dislikes'] = []
            
            # For admins: like = +1, dislike = -1 (remove from opposite side)
            if user_is_admin:
                if reaction == 'like':
                    # Check if there are dislikes to remove
                    admin_dislikes = [d for d in msg['dislikes'] if d.startswith(username)]
                    if admin_dislikes:
                        # Remove one dislike (convert -1 to 0)
                        msg['dislikes'].remove(admin_dislikes[0])
                    else:
                        # No dislikes, add a like (+1)
                        existing_admin_likes = [l for l in msg['likes'] if l.startswith(username)]
                        msg['likes'].append(f"{username}_admin_{len(existing_admin_likes)}")
                        
                elif reaction == 'dislike':
                    # Check if there are likes to remove
                    admin_likes = [l for l in msg['likes'] if l.startswith(username)]
                    if admin_likes:
                        # Remove one like (convert +1 to 0)
                        msg['likes'].remove(admin_likes[0])
                    else:
                        # No likes, add a dislike (-1)
                        existing_admin_dislikes = [d for d in msg['dislikes'] if d.startswith(username)]
                        msg['dislikes'].append(f"{username}_admin_{len(existing_admin_dislikes)}")
            
            # For regular users: toggle behavior
            else:
                if username in msg['likes']:
                    msg['likes'].remove(username)
                if username in msg['dislikes']:
                    msg['dislikes'].remove(username)
                
                # Add to appropriate list
                if reaction == 'like':
                    msg['likes'].append(username)
                elif reaction == 'dislike':
                    msg['dislikes'].append(username)
            
            save_messages(messages)
            
            # Broadcast to all users
            emit('message_reacted', {
                'message_id': message_id,
                'likes': msg.get('likes', []),
                'dislikes': msg.get('dislikes', [])
            }, broadcast=True)
            break

@socketio.on('reply_message')
def handle_reply(data):
    if 'username' not in session:
        return
    
    # Verify thread exists
    threads = load_groups()
    thread_id = data.get('group_id')
    thread_exists = any(t['id'] == thread_id for t in threads)
    
    if not thread_exists:
        emit('message_error', {'message': 'השיחה לא קיימת יותר'})
        return
    
    users = load_users()
    user_data = users.get(session['username'], {})
    
    # Check if user is blocked
    if user_data.get('blocked', False):
        emit('message_error', {'message': 'אתה חסום ולא יכול לשלוח הודעות'})
        return
    
    profile_color = user_data.get('profile_color', '#00a884')
    user_is_admin = user_data.get('is_admin', False)
    
    reply_message = {
        'id': f"{session['username']}_{datetime.now().timestamp()}",
        'from': session['username'],
        'group_id': data['group_id'],
        'message': data['message'],
        'type': data.get('type', 'text'),
        'image': data.get('image'),
        'timestamp': datetime.now().isoformat(),
        'read': False,
        'likes': [],
        'dislikes': [],
        'profile_color': profile_color,
        'is_admin': user_is_admin,
        'reply_to': data.get('reply_to'),  # ID of message being replied to
        'reply_to_user': data.get('reply_to_user'),  # Username of original message
        'reply_to_text': data.get('reply_to_text')  # Preview of original message
    }
    
    messages = load_messages()
    messages.append(reply_message)
    save_messages(messages)
    
    # Broadcast to all users
    emit('receive_message', reply_message, broadcast=True)

@socketio.on('delete_message')
def handle_delete_message(data):
    if 'username' not in session:
        return
    
    # Verify user exists
    users = load_users()
    if session['username'] not in users:
        emit('message_error', {'message': 'משתמש לא נמצא'})
        return
    
    message_id = data['message_id']
    messages = load_messages()
    
    # Find and delete the message if it belongs to the user OR if user is admin
    for i, msg in enumerate(messages):
        if msg.get('id') == message_id and (msg['from'] == session['username'] or is_admin()):
            messages.pop(i)
            save_messages(messages)
            
            # Broadcast to all users
            emit('message_deleted', {'message_id': message_id}, broadcast=True)
            break

@socketio.on('edit_message')
def handle_edit_message(data):
    if 'username' not in session:
        return
    
    # Verify user exists
    users = load_users()
    if session['username'] not in users:
        emit('message_error', {'message': 'משתמש לא נמצא'})
        return
    
    # Check if user is blocked
    if users[session['username']].get('blocked', False):
        emit('message_error', {'message': 'אתה חסום ולא יכול לערוך הודעות'})
        return
    
    message_id = data['message_id']
    new_text = data.get('new_text', '').strip()
    
    if not new_text:
        emit('message_error', {'message': 'ההודעה לא יכולה להיות ריקה'})
        return
    
    messages = load_messages()
    
    # Find and edit the message if it belongs to the user OR if user is admin
    for msg in messages:
        if msg.get('id') == message_id and (msg['from'] == session['username'] or is_admin()):
            msg['message'] = new_text
            msg['edited'] = True
            msg['edited_at'] = datetime.now().isoformat()
            save_messages(messages)
            
            # Broadcast to all users
            emit('message_edited', {
                'message_id': message_id,
                'new_text': new_text,
                'edited': True
            }, broadcast=True)
            break

@app.route('/api/user/<username>')
def get_user_profile(username):
    if 'username' not in session:
        return jsonify({'success': False, 'message': 'לא מחובר'}), 401
    
    users = load_users()
    
    if username not in users:
        return jsonify({'success': False, 'message': 'משתמש לא נמצא'}), 404
    
    user_data = users[username]
    messages = load_messages()
    
    # Count total likes and dislikes on user's messages
    total_likes = 0
    total_dislikes = 0
    for msg in messages:
        if msg.get('from') == username:
            total_likes += len(msg.get('likes', []))
            total_dislikes += len(msg.get('dislikes', []))
    
    # Calculate net likes (likes - dislikes)
    net_likes = max(0, total_likes - total_dislikes)
    
    # Check if current user follows this user
    current_user = session['username']
    is_following = current_user in user_data.get('followers', [])
    
    # Check if user is blocked
    is_blocked = user_data.get('blocked', False)
    
    profile = {
        'username': username,
        'phone': user_data.get('phone', 'לא צוין'),
        'profile_color': user_data.get('profile_color', '#00a884'),
        'total_likes': net_likes,
        'followers': len(user_data.get('followers', [])),
        'following': len(user_data.get('following', [])),
        'is_following': is_following,
        'is_own_profile': username == current_user,
        'is_blocked': is_blocked,
        'is_admin': user_data.get('is_admin', False)
    }
    
    return jsonify({'success': True, 'profile': profile})

@app.route('/api/follow/<username>', methods=['POST'])
def toggle_follow(username):
    if 'username' not in session:
        return jsonify({'success': False, 'message': 'לא מחובר'}), 401
    
    current_user = session['username']
    
    if current_user == username:
        return jsonify({'success': False, 'message': 'לא ניתן לעקוב אחרי עצמך'})
    
    users = load_users()
    
    if username not in users:
        return jsonify({'success': False, 'message': 'משתמש לא נמצא'}), 404
    
    if current_user not in users:
        return jsonify({'success': False, 'message': 'משתמש נוכחי לא נמצא'}), 404
    
    # Initialize followers/following lists if missing
    if 'followers' not in users[username]:
        users[username]['followers'] = []
    if 'following' not in users[current_user]:
        users[current_user]['following'] = []
    
    # Toggle follow
    if current_user in users[username]['followers']:
        # Unfollow
        users[username]['followers'].remove(current_user)
        if username in users[current_user]['following']:
            users[current_user]['following'].remove(username)
        is_following = False
    else:
        # Follow
        users[username]['followers'].append(current_user)
        users[current_user]['following'].append(username)
        is_following = True
    
    save_users(users)
    
    # Broadcast profile update
    socketio.emit('profile_updated', {'username': username})
    
    return jsonify({
        'success': True,
        'is_following': is_following,
        'followers': len(users[username]['followers'])
    })

@app.route('/api/admin/users')
def get_all_users():
    if not is_admin():
        return jsonify({'success': False, 'message': 'אין הרשאה'}), 403
    
    users = load_users()
    user_list = []
    for username, data in users.items():
        user_list.append({
            'username': username,
            'phone': data.get('phone', ''),
            'is_admin': data.get('is_admin', False),
            'blocked': data.get('blocked', False),
            'created_at': data.get('created_at', '')
        })
    
    return jsonify({'success': True, 'users': user_list})

@app.route('/api/admin/block-user', methods=['POST'])
def block_user():
    if not is_admin():
        return jsonify({'success': False, 'message': 'אין הרשאה'}), 403
    
    data = request.get_json()
    username = data.get('username')
    
    if not username:
        return jsonify({'success': False, 'message': 'שם משתמש חסר'})
    
    # Prevent blocking self
    if username == session['username']:
        return jsonify({'success': False, 'message': 'לא ניתן לחסום את עצמך'})
    
    users = load_users()
    
    if username not in users:
        return jsonify({'success': False, 'message': 'משתמש לא נמצא'})
    
    # Prevent blocking other admins
    if users[username].get('is_admin', False):
        return jsonify({'success': False, 'message': 'לא ניתן לחסום מנהל אחר'})
    
    users[username]['blocked'] = True
    save_users(users)
    
    # Notify the blocked user
    socketio.emit('user_blocked', {'username': username})
    
    return jsonify({'success': True})

@app.route('/api/admin/unblock-user', methods=['POST'])
def unblock_user():
    if not is_admin():
        return jsonify({'success': False, 'message': 'אין הרשאה'}), 403
    
    data = request.get_json()
    username = data.get('username')
    
    if not username:
        return jsonify({'success': False, 'message': 'שם משתמש חסר'})
    
    users = load_users()
    
    if username not in users:
        return jsonify({'success': False, 'message': 'משתמש לא נמצא'})
    
    users[username]['blocked'] = False
    save_users(users)
    
    # Notify the unblocked user
    socketio.emit('user_unblocked', {'username': username})
    
    return jsonify({'success': True})

@app.route('/api/admin/make-admin', methods=['POST'])
def make_admin():
    if not is_admin():
        return jsonify({'success': False, 'message': 'אין הרשאה'}), 403
    
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'success': False, 'message': 'נתונים חסרים'})
    
    # Verify admin password
    if password != 'IOSEP@@123212':
        return jsonify({'success': False, 'message': 'סיסמה שגויה'})
    
    users = load_users()
    
    if username not in users:
        return jsonify({'success': False, 'message': 'משתמש לא נמצא'})
    
    if users[username].get('is_admin', False):
        return jsonify({'success': False, 'message': 'המשתמש כבר מנהל'})
    
    users[username]['is_admin'] = True
    users[username]['profile_color'] = '#ff0000'
    users[username]['blocked'] = False  # Unblock if blocked
    save_users(users)
    
    return jsonify({'success': True})

@app.route('/api/admin/delete-thread/<thread_id>', methods=['DELETE'])
def delete_thread(thread_id):
    if not is_admin():
        return jsonify({'success': False, 'message': 'אין הרשאה'}), 403
    
    groups = load_groups()
    groups = [g for g in groups if g['id'] != thread_id]
    save_groups(groups)
    
    # Delete all messages in thread
    messages = load_messages()
    messages = [m for m in messages if m.get('group_id') != thread_id]
    save_messages(messages)
    
    # Broadcast thread deletion to all users
    socketio.emit('thread_deleted', {'thread_id': thread_id})
    
    return jsonify({'success': True})

@app.route('/api/admin/add-reactions', methods=['POST'])
def add_admin_reactions():
    if not is_admin():
        return jsonify({'success': False, 'message': 'אין הרשאה'}), 403
    
    data = request.get_json()
    message_id = data.get('message_id')
    reaction_type = data.get('reaction_type')  # 'like' or 'dislike'
    count = data.get('count', 1)
    
    if not message_id or not reaction_type:
        return jsonify({'success': False, 'message': 'נתונים חסרים'})
    
    messages = load_messages()
    message_found = False
    
    for msg in messages:
        if msg.get('id') == message_id:
            message_found = True
            admin_username = session['username']
            
            # Initialize lists if needed
            if 'likes' not in msg:
                msg['likes'] = []
            if 'dislikes' not in msg:
                msg['dislikes'] = []
            
            # Like = +1, Dislike = -1 logic
            if reaction_type == 'like':
                # First, remove dislikes if exist (convert negative to zero)
                admin_dislikes = [d for d in msg['dislikes'] if d.startswith(admin_username)]
                removed_count = 0
                
                for i in range(min(count, len(admin_dislikes))):
                    if admin_dislikes:
                        msg['dislikes'].remove(admin_dislikes[i])
                        removed_count += 1
                
                # Then add remaining as likes (add positive)
                remaining = count - removed_count
                if remaining > 0:
                    existing_admin_likes = [l for l in msg['likes'] if l.startswith(admin_username)]
                    start_index = len(existing_admin_likes)
                    for i in range(remaining):
                        msg['likes'].append(f"{admin_username}_admin_{start_index + i}")
                        
            elif reaction_type == 'dislike':
                # First, remove likes if exist (convert positive to zero)
                admin_likes = [l for l in msg['likes'] if l.startswith(admin_username)]
                removed_count = 0
                
                for i in range(min(count, len(admin_likes))):
                    if admin_likes:
                        msg['likes'].remove(admin_likes[i])
                        removed_count += 1
                
                # Then add remaining as dislikes (add negative)
                remaining = count - removed_count
                if remaining > 0:
                    existing_admin_dislikes = [d for d in msg['dislikes'] if d.startswith(admin_username)]
                    start_index = len(existing_admin_dislikes)
                    for i in range(remaining):
                        msg['dislikes'].append(f"{admin_username}_admin_{start_index + i}")
            
            save_messages(messages)
            
            # Broadcast update to all users
            socketio.emit('message_reacted', {
                'message_id': message_id,
                'likes': msg.get('likes', []),
                'dislikes': msg.get('dislikes', [])
            })
            
            break
    
    if not message_found:
        return jsonify({'success': False, 'message': 'הודעה לא נמצאה'})
    
    return jsonify({'success': True})

if __name__ == '__main__':
    init_admin()  # Initialize admin user
    cleanup_orphaned_messages()  # Clean up messages from deleted threads
    
    # Get port from environment variable (for Render/Heroku) or use 5000
    port = int(os.environ.get('PORT', 5000))
    
    # Check if running in production (Render sets this)
    is_production = os.environ.get('RENDER') is not None
    
    if is_production:
        print("🚀 Starting server in PRODUCTION mode...")
        # In production, gunicorn handles the server
        # This code won't run, but we keep it for compatibility
        socketio.run(app, host='0.0.0.0', port=port)
    else:
        # Local development
        cert_file = 'cert.pem'
        key_file = 'key.pem'
        
        if os.path.exists(cert_file) and os.path.exists(key_file):
            print("🔒 Starting server with HTTPS...")
            socketio.run(app, debug=True, host='0.0.0.0', port=port, 
                        certfile=cert_file, keyfile=key_file)
        else:
            print("⚠️  Starting server with HTTP (microphone may not work on remote connections)")
            print("💡 To enable HTTPS, run: python generate_cert.py")
            socketio.run(app, debug=True, host='0.0.0.0', port=port)

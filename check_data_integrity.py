#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
סקריפט לבדיקת תקינות נתוני המערכת
"""

import json
import os

def load_json(filename):
    """טען קובץ JSON"""
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def check_users():
    """בדוק תקינות משתמשים"""
    print("🔍 בודק משתמשים...")
    users = load_json('users.json')
    
    if not users:
        print("❌ קובץ users.json לא נמצא!")
        return False
    
    issues = []
    required_fields = ['password', 'phone', 'status', 'profile_pic', 'profile_color', 
                      'created_at', 'followers', 'following', 'blocked']
    
    for username, data in users.items():
        missing = [field for field in required_fields if field not in data]
        if missing:
            issues.append(f"  ⚠️  משתמש '{username}' חסר שדות: {', '.join(missing)}")
    
    if issues:
        print("❌ נמצאו בעיות במשתמשים:")
        for issue in issues:
            print(issue)
        return False
    else:
        print(f"✅ כל {len(users)} המשתמשים תקינים")
        return True

def check_threads():
    """בדוק תקינות שיחות"""
    print("\n🔍 בודק שיחות...")
    threads = load_json('threads.json')
    users = load_json('users.json')
    
    if threads is None:
        print("❌ קובץ threads.json לא נמצא!")
        return False
    
    if not threads:
        print("⚠️  אין שיחות במערכת")
        return True
    
    issues = []
    required_fields = ['id', 'title', 'content', 'created_by', 'created_at']
    
    for thread in threads:
        missing = [field for field in required_fields if field not in thread]
        if missing:
            issues.append(f"  ⚠️  שיחה '{thread.get('id', 'unknown')}' חסרה שדות: {', '.join(missing)}")
        
        # בדוק שהיוצר קיים
        creator = thread.get('created_by')
        if creator and creator not in users:
            issues.append(f"  ⚠️  שיחה '{thread.get('title', 'unknown')}' נוצרה על ידי משתמש לא קיים: {creator}")
    
    if issues:
        print("❌ נמצאו בעיות בשיחות:")
        for issue in issues:
            print(issue)
        return False
    else:
        print(f"✅ כל {len(threads)} השיחות תקינות")
        return True

def check_messages():
    """בדוק תקינות הודעות"""
    print("\n🔍 בודק הודעות...")
    messages = load_json('messages.json')
    threads = load_json('threads.json')
    users = load_json('users.json')
    
    if messages is None:
        print("❌ קובץ messages.json לא נמצא!")
        return False
    
    if not messages:
        print("⚠️  אין הודעות במערכת")
        return True
    
    thread_ids = {t['id'] for t in threads} if threads else set()
    issues = []
    orphaned = []
    
    for msg in messages:
        # בדוק שדות חובה
        required_fields = ['id', 'from', 'group_id', 'message', 'type', 'timestamp']
        missing = [field for field in required_fields if field not in msg]
        if missing:
            issues.append(f"  ⚠️  הודעה '{msg.get('id', 'unknown')}' חסרה שדות: {', '.join(missing)}")
        
        # בדוק שהשיחה קיימת
        group_id = msg.get('group_id')
        if group_id and group_id not in thread_ids:
            orphaned.append(f"  ⚠️  הודעה יתומה: {msg.get('id')} (שיחה {group_id} לא קיימת)")
        
        # בדוק שהשולח קיים
        sender = msg.get('from')
        if sender and sender not in users:
            issues.append(f"  ⚠️  הודעה מ-'{sender}' - משתמש לא קיים")
    
    if issues or orphaned:
        if issues:
            print("❌ נמצאו בעיות בהודעות:")
            for issue in issues:
                print(issue)
        if orphaned:
            print("❌ נמצאו הודעות יתומות:")
            for orph in orphaned:
                print(orph)
            print(f"\n💡 הפעל את השרת כדי לנקות אוטומטית {len(orphaned)} הודעות יתומות")
        return False
    else:
        print(f"✅ כל {len(messages)} ההודעות תקינות")
        return True

def main():
    """פונקציה ראשית"""
    print("=" * 60)
    print("🔧 בדיקת תקינות נתוני מערכת WhatsApp Web")
    print("=" * 60)
    
    results = []
    results.append(check_users())
    results.append(check_threads())
    results.append(check_messages())
    
    print("\n" + "=" * 60)
    if all(results):
        print("✅ כל הנתונים תקינים!")
    else:
        print("❌ נמצאו בעיות בנתונים. אנא תקן אותן.")
    print("=" * 60)

if __name__ == '__main__':
    main()

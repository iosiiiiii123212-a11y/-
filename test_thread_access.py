#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
סקריפט לבדיקת גישה לשיחות
"""

import requests
import json

BASE_URL = 'http://localhost:5000'

def test_login(username, password):
    """נסה להתחבר"""
    print(f"\n🔐 מנסה להתחבר כ-'{username}'...")
    
    session = requests.Session()
    response = session.post(
        f'{BASE_URL}/login',
        json={'username': username, 'password': password}
    )
    
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            print(f"✅ התחברות הצליחה!")
            return session
        else:
            print(f"❌ התחברות נכשלה: {data.get('message')}")
            return None
    else:
        print(f"❌ שגיאת שרת: {response.status_code}")
        return None

def test_get_threads(session, username):
    """נסה לקבל רשימת שיחות"""
    print(f"\n📋 מנסה לקבל רשימת שיחות...")
    
    response = session.get(f'{BASE_URL}/api/threads')
    
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            threads = data.get('threads', [])
            print(f"✅ קיבלנו {len(threads)} שיחות:")
            for thread in threads:
                print(f"   - {thread['title']} (ID: {thread['id']})")
            return threads
        else:
            print(f"❌ קבלת שיחות נכשלה: {data.get('message')}")
            return []
    else:
        print(f"❌ שגיאת שרת: {response.status_code}")
        return []

def test_get_messages(session, thread_id, thread_title):
    """נסה לקבל הודעות משיחה"""
    print(f"\n📨 מנסה לקבל הודעות מ-'{thread_title}' (ID: {thread_id})...")
    
    response = session.get(f'{BASE_URL}/api/messages/{thread_id}')
    
    print(f"   סטטוס: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            messages = data.get('messages', [])
            print(f"✅ קיבלנו {len(messages)} הודעות!")
            for msg in messages[:3]:  # הצג רק 3 ראשונות
                print(f"   - {msg['from']}: {msg['message'][:50]}...")
            return True
        else:
            print(f"❌ קבלת הודעות נכשלה: {data.get('message')}")
            return False
    elif response.status_code == 401:
        print(f"❌ לא מורשה - אולי לא מחובר?")
        return False
    elif response.status_code == 404:
        print(f"❌ השיחה לא נמצאה!")
        return False
    else:
        print(f"❌ שגיאת שרת: {response.status_code}")
        try:
            print(f"   תוכן: {response.text}")
        except:
            pass
        return False

def main():
    """פונקציה ראשית"""
    print("=" * 60)
    print("🧪 בדיקת גישה לשיחות - WhatsApp Web")
    print("=" * 60)
    
    # בדוק שהשרת רץ
    try:
        response = requests.get(BASE_URL, timeout=2)
        print("✅ השרת רץ!")
    except requests.exceptions.ConnectionError:
        print("❌ השרת לא רץ! הפעל את השרת קודם:")
        print("   python server.py")
        return
    except Exception as e:
        print(f"❌ שגיאה בחיבור לשרת: {e}")
        return
    
    # בדוק עם משתמש רגיל
    print("\n" + "=" * 60)
    print("בדיקה 1: משתמש רגיל - יוסף שלום")
    print("=" * 60)
    
    session = test_login('יוסף שלום', '123')
    if session:
        threads = test_get_threads(session, 'יוסף שלום')
        if threads:
            for thread in threads:
                test_get_messages(session, thread['id'], thread['title'])
    
    # בדוק עם מנהל
    print("\n" + "=" * 60)
    print("בדיקה 2: מנהל")
    print("=" * 60)
    
    session = test_login('מנהל', 'IOSEP@@123212')
    if session:
        threads = test_get_threads(session, 'מנהל')
        if threads:
            for thread in threads:
                test_get_messages(session, thread['id'], thread['title'])
    
    print("\n" + "=" * 60)
    print("✅ בדיקה הסתיימה!")
    print("=" * 60)

if __name__ == '__main__':
    main()

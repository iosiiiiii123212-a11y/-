# 💬 WhatsApp Web Clone

שיבוט מלא של WhatsApp Web עם Flask, SocketIO ו-Python.

---

## 🚀 התקנה מקומית

```bash
# התקן תלויות
pip install -r requirements.txt

# הרץ את השרת
python server.py
```

פתח בדפדפן: `http://localhost:5000`

---

## 🌐 פרסום ל-Render

### 1. העלה ל-GitHub
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/whatsapp-web-clone.git
git push -u origin main
```

### 2. פרסם ב-Render
1. לך ל-https://render.com
2. New → Web Service
3. חבר את ה-repository
4. Deploy!

**מדריך מפורט:** `README_DEPLOY.md`

---

## 🔄 Keep-Alive (שמירה על השרת ער)

השרת ב-Render Free "נרדם" אחרי 15 דקות.

**פתרון מהיר:**
1. הירשם ל-https://cron-job.org (חינם)
2. צור job שמבצע ping ל-`/health` כל 10 דקות
3. זהו!

**מדריך מפורט:** `KEEP_ALIVE_GUIDE.md`

---

## ✨ פיצ'רים

- ✅ שליחת הודעות בזמן אמת
- ✅ תמונות ועיצוב טקסט
- ✅ לייקים ודיסלייקים מודרניים
- ✅ מעקב אחרי משתמשים
- ✅ "מי צופה איתי" בזמן אמת
- ✅ סימון הודעות שנקראו
- ✅ פאנל מנהל
- ✅ תמיכה מלאה במובייל

---

## 👑 מנהל

- **שם משתמש:** `מנהל`
- **סיסמה:** `IOSEP@@123212`

---

## 📁 מבנה

```
3333/
├── server.py              # שרת Flask
├── requirements.txt       # תלויות
├── render.yaml           # הגדרות Render
├── static/               # CSS + JS
├── templates/            # HTML
└── *.json               # נתונים
```

---

**Made with ❤️ by יוסף שלום בן שטרית**

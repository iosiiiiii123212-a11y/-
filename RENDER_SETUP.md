# 🎯 הגדרות מדויקות ל-Render

## שלב 1: צור Web Service

לחץ על **"New +"** → **"Web Service"**

---

## שלב 2: חבר Repository

בחר את ה-repository שלך מ-GitHub

---

## שלב 3: מלא את השדות הבאים:

### 📝 Basic Settings:

| שדה | מה להכניס |
|-----|-----------|
| **Name** | `whatsapp-web` (או כל שם שתרצה) |
| **Region** | `Frankfurt (EU Central)` או `Oregon (US West)` |
| **Branch** | `main` |
| **Root Directory** | השאר ריק (או `3333` אם העלית את כל התיקייה) |

---

### 🔧 Build & Deploy:

| שדה | מה להכניס |
|-----|-----------|
| **Runtime** | `Python 3` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `gunicorn -k eventlet -w 1 server:app` |

---

### 💰 Instance Type:

בחר: **Free** (0$/חודש)

---

### 🔐 Environment Variables (Advanced):

לחץ על **"Advanced"** ואז **"Add Environment Variable"**

הוסף את המשתנים הבאים:

| Key | Value |
|-----|-------|
| `SECRET_KEY` | `your-super-secret-key-change-this-12345` |
| `PYTHON_VERSION` | `3.11.0` |

---

### ⚙️ Auto-Deploy:

✅ **Yes** - כדי שיעדכן אוטומטית כשדוחפים ל-GitHub

---

## שלב 4: לחץ "Create Web Service"

המתן 5-10 דקות לבנייה...

---

## ✅ אחרי שהפריסה הצליחה:

תקבל URL כמו:
```
https://whatsapp-web-xxxx.onrender.com
```

---

## 🐛 אם יש שגיאות:

### שגיאה: "Failed to build"

**בדוק:**
1. ש-`requirements.txt` קיים ב-root
2. ש-`server.py` קיים ב-root
3. ש-`Procfile` קיים ב-root

**פתרון:**
- אם העלית את תיקיית `3333`, שנה את **Root Directory** ל-`3333`

---

### שגיאה: "Application failed to start"

**בדוק את ה-Logs:**
1. לחץ על "Logs" בתפריט השמאלי
2. חפש שגיאות אדומות

**פתרונות נפוצים:**
- ודא ש-Start Command הוא: `gunicorn -k eventlet -w 1 server:app`
- ודא ש-`gunicorn` ו-`eventlet` ב-`requirements.txt`

---

### שגיאה: "Module not found"

**פתרון:**
הוסף את המודול החסר ל-`requirements.txt`

---

### WebSocket לא עובד

**פתרון:**
ודא שה-Start Command כולל `-k eventlet`

---

## 📋 סיכום - מה להכניס:

```
Name: whatsapp-web
Runtime: Python 3
Build Command: pip install -r requirements.txt
Start Command: gunicorn -k eventlet -w 1 server:app

Environment Variables:
- SECRET_KEY = your-secret-key-here
- PYTHON_VERSION = 3.11.0
```

---

**זהו! אם עדיין יש בעיה, העתק את השגיאה מה-Logs ותראה לי** 🚀

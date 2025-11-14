# 📦 פקודות Git להעלאה ל-GitHub

## שלב 1: הכנה

```bash
cd 3333
```

## שלב 2: אתחול Git

```bash
git init
git add .
git commit -m "Initial commit - WhatsApp Web Clone v2.4"
```

## שלב 3: חיבור ל-GitHub

**קודם צור repository ב-GitHub:**
1. לך ל-https://github.com/new
2. שם: `whatsapp-web-clone`
3. לחץ "Create repository"

**אחר כך הרץ (החלף YOUR_USERNAME בשם המשתמש שלך):**

```bash
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/whatsapp-web-clone.git
git push -u origin main
```

## שלב 4: עדכונים עתידיים

כשאתה משנה משהו:

```bash
git add .
git commit -m "תיאור השינוי"
git push
```

---

## 🔑 אם יש בעיות עם Authentication:

### אופציה 1: Personal Access Token (מומלץ)

1. לך ל-https://github.com/settings/tokens
2. "Generate new token" → "Classic"
3. תן שם: "WhatsApp Web"
4. סמן: `repo`
5. "Generate token"
6. **שמור את ה-token!**

כשמבקשים סיסמה, השתמש ב-token במקום הסיסמה.

### אופציה 2: SSH

```bash
# צור SSH key
ssh-keygen -t ed25519 -C "your_email@example.com"

# העתק את המפתח
cat ~/.ssh/id_ed25519.pub

# הוסף ב-GitHub:
# Settings → SSH and GPG keys → New SSH key

# שנה את ה-remote ל-SSH
git remote set-url origin git@github.com:YOUR_USERNAME/whatsapp-web-clone.git
```

---

## 📋 פקודות שימושיות:

```bash
# בדוק סטטוס
git status

# ראה היסטוריה
git log --oneline

# בטל שינויים
git checkout -- filename

# מחק קובץ
git rm filename
git commit -m "Deleted filename"

# שנה שם קובץ
git mv oldname newname
git commit -m "Renamed file"
```

---

**בהצלחה! 🚀**

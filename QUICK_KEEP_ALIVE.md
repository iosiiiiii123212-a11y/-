# ⚡ Keep-Alive מהיר - 2 דקות!

## 🎯 הדרך הכי פשוטה:

### 1. לך ל-Cron-Job.org
```
https://cron-job.org/en/
```

### 2. הירשם (חינם)
- לחץ "Sign up"
- מלא פרטים
- אשר מייל

### 3. צור Cron Job
- לחץ "Create cronjob"
- **Title:** `Keep Alive`
- **URL:** `https://YOUR-APP.onrender.com/health`
- **Schedule:** 
  - Minutes: `*/10`
  - Hours: `*`
  - Days: `*`
  - Months: `*`
- לחץ "Create"

### 4. זהו!
השרת יישאר ער 24/7! 🎉

---

## 🔍 בדיקה:

פתח בדפדפן:
```
https://YOUR-APP.onrender.com/health
```

אמור להראות:
```json
{
  "status": "ok",
  "message": "Server is alive! 🚀"
}
```

---

## 📝 החלף את ה-URL:

ב-`.github/workflows/keep-alive.yml`:
```yaml
# שנה את זה:
https://whatsapp-web-xxxx.onrender.com/health

# לזה:
https://YOUR-ACTUAL-URL.onrender.com/health
```

---

**זה הכל! 2 דקות והשרת ער לתמיד! ⚡**

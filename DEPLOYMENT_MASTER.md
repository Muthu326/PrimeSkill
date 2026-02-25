# 🏛️ INSTITUTIONAL CLOUD DEPLOYMENT GUIDE (MASTER)
CEO: MuthuKumar Krishnan

This guide allows you to run your **Prime Skill Pro Terminal** and **Institutional Scanner** 24/7 on the cloud.

---

## 🏗️ 1. PRE-DEPLOYMENT CHECKLIST
Ensure your project is ready for the cloud:
1.  **GitHub Repository**: Create a **Private** repository on GitHub.
2.  **Requirements**: `requirements.txt` is updated (Action taken by me).
3.  **Secrets**: Your API Keys must NOT be in the code. Move them to `.env`.

---

## ☁️ 2. CHOOSE YOUR CLOUD (RECOMMENDED: RENDER.COM)
Render is professional, stable, and handles background processes (scanners) perfectly.

### A. Deploy Frontend (Streamlit Dashboard)
1.  Go to [Render.com](https://render.com) and log in with GitHub.
2.  Click **New +** > **Web Service**.
3.  Select your GitHub repository.
4.  **Name**: `prime-skill-terminal`
5.  **Runtime**: `Python 3`
6.  **Build Command**: `pip install -r requirements.txt`
7.  **Start Command**: `streamlit run marsh_muthu_326_pro_terminal.py --server.port $PORT`
8.  **Environment Variables**: Add your `.env` keys here (UPSTOX_API_KEY, TELEGRAM_TOKEN, etc.).

### B. Deploy Backend (Institutional Scanner)
1.  Click **New +** > **Background Worker**.
2.  Select the same GitHub repository.
3.  **Name**: `prime-skill-scanner`
4.  **Build Command**: `pip install -r requirements.txt`
5.  **Start Command**: `python main.py`
6.  **Environment Variables**: Use the same keys as above.

---

## 🔐 3. ENVIRONMENT VARIABLES (CRITICAL)
Add these keys in the **Environment** tab of both services on Render:
- `UPSTOX_API_KEY`
- `UPSTOX_SECRET_KEY`
- `UPSTOX_ACCESS_TOKEN` (Or use the auth logic we built)
- `TELEGRAM_TOKEN`
- `TELEGRAM_CHAT_ID`
- `TEST_MODE`: `false` (For live signals)

---

## 🛠️ 4. HANDLING UPSTOX AUTH (CLOUD FIX)
Since you won't be there to click "Allow" on the cloud:
1.  **Method A (Recommended)**: Use a Long-Term Access Token.
2.  **Method B**: Run the `auth_upstox.py` locally first, get the token, and paste it into the Cloud Env Variable `UPSTOX_ACCESS_TOKEN`.

---

## 🚀 5. FINAL STEPS
1.  **Dashboard**: Open the auto-generated URL (e.g., `https://prime-skill-terminal.onrender.com`).
2.  **Scanner**: Check the **Logs** tab of the Background Worker. You should see:
    `🔥 PRO-VERSION BULLETPROOF ENGINE STARTING...`
    `📡 Mapping instruments...`
    `✅ Scan Cycle Complete.`

---
🏛 **Prime Skill Development | Built for Institutional Success**

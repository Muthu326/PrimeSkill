# 🚀 GUIDE: Deploying your Prime Skill Ultimate Pro Terminal to Streamlit Cloud

To make your terminal accessible as a "real website" that you can check from your phone or any computer, follow these simple steps:

## Prerequisites
1. **GitHub Account:** If you don't have one, create it at [github.com](https://github.com).
2. **Streamlit Account:** Use your GitHub account to sign up at [share.streamlit.io](https://share.streamlit.io).

---

## Step 1: Upload your code to GitHub

If you haven't uploaded your project to GitHub yet, use these commands in your project folder (where `marsh_muthu_326_pro_terminal.py` is):

1. **Initialize Git (if not done):**
   ```bash
   git init
   ```
2. **Add all files:**
   ```bash
   git add .
   ```
3. **Commit your code:**
   ```bash
   git commit -m "Final Refactored Version for Deployment"
   ```
4. **Create a remote repository on GitHub** (via the website) and then:
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/PrimeSkill.git
   git branch -M main
   git push -u origin main
   ```

---

## Step 2: Deploy to Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io).
2. Click **"Create app"**.
3. Select your repository: `PrimeSkill`.
4. Select the branch: `main`.
5. **Main file path:** `marsh_muthu_326_pro_terminal.py`.
6. Click **"Advanced settings..."** before deploying.

---

## Step 3: Configure Secrets (CRITICAL)

Since your code uses Telegram tokens and other sensitive data from `.env`, you must enter them in the **Secrets** modal:

Copy and paste your `.env` content into the Secrets box on Streamlit:
```toml
TELEGRAM_TOKEN = "your_bot_token_here"
TELEGRAM_CHAT_ID = "your_chat_id_here"
```

---

## Step 4: Launch! 🚀

1. Click **"Deploy!"**.
2. Wait 1-2 minutes for Streamlit to install the requirements from `requirements.txt`.
3. Your app will be live at a URL like: `https://prime-skill-terminal.streamlit.app`

---

## 💡 Important Notes:
- **Requirements:** Streamlit Cloud automatically reads your `requirements.txt` to install `pandas`, `yfinance`, `plotly`, etc.
- **Backend Scanner:** Streamlit Cloud is great for the UI, but it might pause if not used for a while. For the **24/7 Backend Scanner** (`am_backend_scanner.py`), it is recommended to keep it running on your local PC or a cheap VPS (like DigitalOcean or AWS).

---
**Guide created by Antigravity for Marsh Muthu 326**

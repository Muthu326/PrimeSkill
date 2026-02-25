# 🌐 HOW TO GET YOUR PUBLIC LINK

You have two ways to access your Pro Terminal:

### 1. Permanent Website (Streamlit Cloud)
This is a real website address (like `https://muthu-pro.streamlit.app`) that works 24/7 on your phone and PC.

**Steps to Deploy:**
1. **GitHub Upload**: Double-click `PUBLISH_TO_WEBSITE.bat`. This sends your code to GitHub.
2. **Launch App**: Go to [share.streamlit.io](https://share.streamlit.io), select your project, and click **Deploy**.
3. **Public URL**: You will get a link that looks like `https://prime-skill-terminal.streamlit.app`.

---

### 2. Instant Temporary Link (ngrok)
Use this if you want an immediate link without GitHub.

**Steps:**
1. **Download ngrok**: Go to [ngrok.com](https://ngrok.com) and download it to this folder.
2. **Start Dashboard**: Run your streamlit terminal as usual.
3. **Open Tunnel**: Open a new terminal and type:
   ```bash
   ngrok http 8501
   ```
4. **Public URL**: ngrok will give you a link like `https://a1b2-c3d4.ngrok-free.app`. Open this on your phone!

---

### ⏱ Sync Issues?
I have updated your dashboard to refresh every **30 seconds** instead of 5 minutes. 
Check the **Sidebar** → It now shows `Last Success: HH:MM:SS` so you know exactly when the data was last updated.

**Guide created for Marsh Muthu 326**

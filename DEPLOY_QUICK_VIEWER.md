# Quick Scan Viewer - Public URL Deployment Guide

## Overview
This guide shows you how to make your Quick Scan Viewer accessible via a **public internet URL** that anyone can access from anywhere.

---

## 🎯 Deployment Options

### Option 1: Network Access Only (No Internet)
**Good for:** Same WiFi/Local network access

**Steps:**
1. Run `START_VIEWER_SERVER.bat`
2. Share the Network URL shown (e.g., `http://192.168.1.100:8080/static/scan_viewer.html`)
3. Anyone on your WiFi can access it

**Pros:** Simple, instant, no signup  
**Cons:** Only works on same network

---

### Option 2: ngrok (Public Internet - Recommended)
**Good for:** Quick public URL, mobile access from anywhere

**Setup:**

1. **Download ngrok**
   ```
   Visit: https://ngrok.com/download
   Download for Windows
   Extract ngrok.exe to your PrimeSkill folder
   ```

2. **Get Auth Token** (Free)
   ```
   Sign up at ngrok.com (free account)
   Copy your authtoken from dashboard
   ```

3. **Configure ngrok**
   ```cmd
   ngrok config add-authtoken YOUR_AUTH_TOKEN_HERE
   ```

4. **Start Local Server**
   ```
   Double-click: START_VIEWER_SERVER.bat
   (Keep this running)
   ```

5. **Create Public Tunnel**
   ```cmd
   ngrok http 8080
   ```

6. **Get Your Public URL**
   ```
   You'll see:
   Forwarding: https://abc123.ngrok-free.app -> http://localhost:8080
   
   Your public URL: https://abc123.ngrok-free.app/static/scan_viewer.html
   ```

7. **Share URL**
   - Copy the https URL
   - Share with anyone
   - They can access from anywhere in the world!

**Pros:**
- ✅ Free tier available
- ✅ HTTPS (secure)
- ✅ Custom domains (paid)
- ✅ Works anywhere

**Cons:**
- ❌ URL changes each restart (unless paid)
- ❌ Requires ngrok to be running

---

### Option 3: Cloudflare Tunnel (Free, No Account)
**Good for:** Quick public URL without signup

**Setup:**

1. **Download cloudflared**
   ```
   Visit: https://github.com/cloudflare/cloudflared/releases
   Download cloudflared-windows-amd64.exe
   Rename to cloudflared.exe
   Move to PrimeSkill folder
   ```

2. **Start Local Server**
   ```
   Double-click: START_VIEWER_SERVER.bat
   (Keep this running)
   ```

3. **Create Tunnel**
   ```cmd
   cloudflared tunnel --url http://localhost:8080
   ```

4. **Get Your URL**
   ```
   You'll see:
   https://xyz-abc-123.trycloudflare.com
   
   Your URL: https://xyz-abc-123.trycloudflare.com/static/scan_viewer.html
   ```

**Pros:**
- ✅ No account needed
- ✅ Free
- ✅ HTTPS

**Cons:**
- ❌ URL changes every restart
- ❌ ".trycloudflare.com" domain

---

### Option 4: Streamlit Cloud (Full App Only)
**Good for:** Hosting the full Streamlit application

**Setup:**
See `DEPLOYMENT_GUIDE_STREAMLIT.md` for full details.

**Quick Steps:**
1. Push code to GitHub
2. Go to `share.streamlit.io`
3. Connect GitHub repo
4. Deploy `marsh_muthu_326_pro_terminal.py`

**URL:**
```
https://your-app-name.streamlit.app
```

**Pros:**
- ✅ Free hosting
- ✅ Permanent URL
- ✅ Auto-deploys on push

**Cons:**
- ❌ Only for Streamlit app (not Quick Viewer)
- ❌ May sleep if inactive

---

## 📱 Complete Workflow Example

### Scenario: Share Market Picks with Phone/Team

**Step 1: Start Local Server**
```
Double-click: START_VIEWER_SERVER.bat
Server starts on http://localhost:8080
```

**Step 2: Create Public Tunnel (ngrok)**
```cmd
ngrok http 8080
```

**Step 3: Copy Public URL**
```
Forwarding: https://abc123.ngrok-free.app
```

**Step 4: Build Full URL**
```
https://abc123.ngrok-free.app/static/scan_viewer.html
```

**Step 5: Share!**
- Send URL via WhatsApp/Telegram
- Open on phone
- View live market picks
- Auto-refreshes every 30 seconds

---

## 🔒 Security Considerations

### ⚠️ Important Notes:

1. **Public URLs are accessible to ANYONE who has the link**
   - Don't share with untrusted people
   - Consider password protection if needed

2. **Data Exposure**
   - The scan_cache.json is publicly accessible
   - Only market data (no personal info)
   - Review what's exposed before sharing

3. **Rate Limiting**
   - Free tiers have limits
   - ngrok: 40 connections/minute (free tier)
   - cloudflared: No official limits

4. **SSL/HTTPS**
   - ngrok and cloudflared provide HTTPS
   - Local server is HTTP only
   - Use tunnels for internet access

---

## 🎯 Recommended Setup for Different Use Cases

### Use Case 1: Personal Mobile Access
```
✅ Use: ngrok
Why: Stable, HTTPS, works from anywhere
Setup time: 5 minutes
```

### Use Case 2: Team Sharing (Same Office WiFi)
```
✅ Use: START_VIEWER_SERVER.bat (Network URL)
Why: No tunnel needed, faster
Setup time: 1 minute
```

### Use Case 3: Demo/Testing (Quick & Free)
```
✅ Use: cloudflared
Why: No signup, instant URL
Setup time: 2 minutes
```

### Use Case 4: Permanent Public Access
```
✅ Use: Streamlit Cloud + Quick Viewer
Why: Free hosting, permanent URL
Setup time: 15 minutes
```

---

## 🛠️ Troubleshooting

### Issue: "Connection refused"
**Solution:**
- Check if `START_VIEWER_SERVER.bat` is running
- Verify port 8080 is not blocked

### Issue: "ngrok not found"
**Solution:**
- Make sure ngrok.exe is in PrimeSkill folder
- Run from command prompt in correct directory

### Issue: "URL shows error page"
**Solution:**
- Append `/static/scan_viewer.html` to base URL
- Example: `https://abc123.ngrok-free.app/static/scan_viewer.html`

### Issue: "Data not updating"
**Solution:**
- Check if Streamlit app is running (generates data)
- Verify `data/scan_cache.json` is being updated
- Refresh viewer page

---

## 📊 Architecture Diagram

```
┌─────────────────┐
│ Streamlit App   │ ← Scans markets
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ scan_cache.json │ ← Saves results
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Python Server   │ ← Serves files
│ (Port 8080)     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ ngrok/tunnel    │ ← Creates public URL
└────────┬────────┘
         │
         ▼
    🌐 Internet
         │
         ▼
┌─────────────────┐
│ Mobile/Browser  │ ← Anyone can access
└─────────────────┘
```

---

## 🚀 Quick Start Commands

### Using ngrok (Recommended):
```batch
# Terminal 1: Start local server
START_VIEWER_SERVER.bat

# Terminal 2: Create public tunnel
ngrok http 8080

# Copy the HTTPS URL shown
# Share: https://xxxxx.ngrok-free.app/static/scan_viewer.html
```

### Using cloudflared:
```batch
# Terminal 1: Start local server
START_VIEWER_SERVER.bat

# Terminal 2: Create public tunnel
cloudflared tunnel --url http://localhost:8080

# Copy the HTTPS URL shown
# Share: https://xxxxx.trycloudflare.com/static/scan_viewer.html
```

---

## 💡 Pro Tips

1. **Keep Server Running**
   - Both local server AND tunnel must run together
   - Close either one = URL stops working

2. **Bookmark URLs**
   - If using ngrok paid ($8/month), get static domain
   - URL never changes, easy to bookmark

3. **Auto-Start on Boot**
   - Add START_VIEWER_SERVER.bat to Windows startup
   - Use Windows Task Scheduler for auto-ngrok

4. **Monitor Access**
   - ngrok dashboard shows who accessed: `http://localhost:4040`
   - See traffic, requests, errors

5. **Custom Domain** (Advanced)
   - ngrok paid: custom.yourdomain.com
   - Cloudflare: Full control with Cloudflare DNS

---

## 📝 File Checklist

Make sure you have:
- ✅ `serve_viewer.py` - HTTP server script
- ✅ `START_VIEWER_SERVER.bat` - Server launcher
- ✅ `SETUP_PUBLIC_URL.bat` - Setup guide
- ✅ `static/scan_viewer.html` - Viewer page
- ✅ `data/scan_cache.json` - Data file
- ✅ `ngrok.exe` (download separately)
- ✅ `cloudflared.exe` (download separately)

---

**Now you can share your market scans with anyone, anywhere! 🌐🚀**

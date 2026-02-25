# Quick Scan Viewer

## Ultra-Fast Market Scanner Viewer

This lightweight HTML viewer loads scan results **instantly** from cached JSON data without waiting for the full Streamlit app to load.

### Features:

- ⚡ **Instant Load** - Opens in milliseconds
- 📦 **Cached Data** - Reads from `data/scan_cache.json`
- 🔄 **Auto-Refresh** - Updates every 30 seconds
- 💎 **Quality Tiers** - Shows DIAMOND, TOP PICK, BEST CALL picks
- 📱 **Mobile Friendly** - Works on phone, tablet, desktop

### How to Use:

**Method 1: Double-click**
- Run `OPEN_QUICK_VIEWER.bat` in the main folder

**Method 2: From Streamlit**
- Click "⚡ Open Quick Viewer" in the sidebar

**Method 3: Direct Open**
- Open `static/scan_viewer.html` in any browser

### How It Works:

1. Main app scans markets → Saves to `data/scan_cache.json`
2. Quick viewer reads JSON → Displays instantly
3. Auto-refreshes every 30 seconds for latest data

### Perfect For:

- Quick glance at market picks without loading full app
- Checking alerts on mobile phone
- Lightweight monitoring on second screen
- Fast access when Streamlit is slow

---

**Created by:** Prime Skill Development | Marsh Muthu 326

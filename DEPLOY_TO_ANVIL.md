# 🦅 DEPLOYING TO ANVIL (Drag-and-Drop Web UI)

Anvil allows you to build a professional trading website using only Python and a Drag-and-Drop editor.

### Step 1: Create your Anvil App
1. Go to [Anvil.works](https://anvil.works) and Log in.
2. Click **"New Blank App"**.
3. Choose **"Material Design 3"** (Modern Look).

### Step 2: Enable Uplink (The Bridge)
1. In your Anvil Editor, click the **"+"** next to "Services" in the sidebar.
2. Select **"Uplink"**.
3. Click **"Enable Server Uplink"**.
4. **COPY the Uplink Key** (e.g., `server-X1Y2Z3...`).

### Step 3: Configure your PC
1. Open your `.env` file in VS Code.
2. Add this line at the bottom:
   ```env
   ANVIL_UPLINK_KEY = 'YOUR_COPIED_KEY_HERE'
   ```
3. Run the bridge on your PC:
   ```bash
   python anvil_bridge.py
   ```

### Step 4: Add Code to Anvil UI
In your Anvil Form (Design View), you can now call your local scanner data using this Python code in Anvil:

```python
# Inside Anvil Form
def refresh_button_click(self, **event_args):
    data = anvil.server.call('get_institutional_data')
    # Now you can show data.get('all') in an Anvil Data Grid!
    self.label_last_update.text = data.get('last_update')
```

### ✅ Why use Anvil?
- **Speed**: No web servers to manage.
- **Security**: Your scanner runs safely on your PC; only the results go to the web.
- **Professional**: Drag-and-drop buttons, charts, and tables that look like a bank terminal.

---
**Guide created for Marsh Muthu 326**

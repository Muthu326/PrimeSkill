import anvil.server
import json
import os
import time
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Path to your scanner results
INST_RESULTS_FILE = "data/inst_scanner_results.json"

@anvil.server.callable
def get_institutional_data():
    """Exposes local scanner results to Anvil UI"""
    if os.path.exists(INST_RESULTS_FILE):
        try:
            with open(INST_RESULTS_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            return {"error": str(e)}
    return {"error": "Scanner results not found yet."}

@anvil.server.callable
def get_pcr_status():
    """Returns the latest PCR metrics for Anvil dashboard"""
    if os.path.exists(INST_RESULTS_FILE):
        try:
            with open(INST_RESULTS_FILE, 'r') as f:
                data = json.load(f)
                return data.get('pcr', {})
        except:
            return {}
    return {}

def start_uplink():
    print("🚀 ANVIL UPLINK BRIDGE STARTING...")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    # User will need to provide their Anvil Uplink Key
    uplink_key = os.getenv("ANVIL_UPLINK_KEY")
    
    if not uplink_key:
        print("❌ ERROR: ANVIL_UPLINK_KEY not found in .env")
        print("Please add: ANVIL_UPLINK_KEY = 'your-key-here' to your .env file.")
        return

    try:
        anvil.server.connect(uplink_key)
        print("✅ CONNECTED TO ANVIL CLOUD!")
        print("📡 Your local scanner data is now accessible on the web.")
        print("⏹️  Press Ctrl+C to stop the bridge.")
        anvil.server.wait_forever()
    except Exception as e:
        print(f"❌ CONNECTION FAILED: {e}")

if __name__ == "__main__":
    start_uplink()

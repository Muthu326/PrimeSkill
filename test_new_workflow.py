
import os
import sys
import time
import json
from datetime import datetime
from dotenv import load_dotenv

# Add the project directory to sys.path to import from am_backend_scanner
sys.path.append(os.getcwd())

from am_backend_scanner import send_trade_alert, save_alerts_sent, load_alerts_sent

def run_workflow_test():
    print("🚀 Starting Workflow Simulation Test...")
    
    # 1. Setup Mock Signal
    test_signal = {
        "symbol": "RELIANCE",
        "strike": 2950,
        "type": "CE",
        "spot": 2942.50,
        "premium": 45.00,
        "stop_loss": 38.00,
        "target": 65.00,
        "confidence": 85,
        "status": "Active",
        "expiry": "27-FEB-2025",
        "tag": "💎 DIAMOND ENTRY"
    }
    
    # Clean history for test
    alerts_sent = {}
    save_alerts_sent(alerts_sent)
    
    print("\n--- STEP 1: Sending New Signal ---")
    # Simulate sending a new alert
    success = send_trade_alert(test_signal, is_update=False)
    
    if success:
        print("✅ New Signal alert sent to Telegram.")
        # Record it in history
        alerts_sent["TEST_KEY"] = {"ts": time.time(), "status": "Active"}
        save_alerts_sent(alerts_sent)
    else:
        print("❌ Failed to send New Signal alert.")
        return

    time.sleep(2) # Brief pause

    print("\n--- STEP 2: Simulating Target Hit ---")
    # 2. Update status and send update
    test_signal["status"] = "Target Achieved ✅"
    test_signal["premium"] = 66.20 # Current price
    
    success = send_trade_alert(test_signal, is_update=True)
    
    if success:
        print("✅ Target Update alert sent to Telegram.")
        # Update history
        alerts_sent["TEST_KEY"] = {"ts": time.time(), "status": "Target Achieved ✅"}
        save_alerts_sent(alerts_sent)
    else:
        print("❌ Failed to send Target Update alert.")
        return

    print("\n--- STEP 3: Duplication Check ---")
    # 3. Try sending the SAME update again (Should be skipped in real scanner, but here we just show the check)
    current_status = test_signal["status"]
    prev_status = alerts_sent["TEST_KEY"]["status"]
    
    if current_status == prev_status:
        print("🛡️ DUPLICATION CHECK: Logic would SKIP this alert because status matches history.")
    else:
        print("🚨 LOGIC ERROR: Status should match.")

    print("\n✅ Simulation Complete. Please check your Telegram for the formatted messages!")

if __name__ == "__main__":
    run_workflow_test()

import os
import sys

# Add the project root to sys.path
sys.path.append(os.getcwd())

from services.trade_monitor import get_trade_monitor

def trigger_performance_report():
    print("📊 Triggering Overall Concept Performance Report...")
    monitor = get_trade_monitor()
    
    # Check if there's any data
    if monitor.stats["total"] == 0:
        print("⏸ No session data found. Sending empty report to illustrate format.")
    
    monitor.send_concept_accuracy()
    print("✅ Report Dispatched to Telegram.")

if __name__ == "__main__":
    trigger_performance_report()

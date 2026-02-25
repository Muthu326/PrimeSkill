import os
import sys
from datetime import datetime

# Add the project root to sys.path
sys.path.append(os.getcwd())

from services.scheduler import get_scheduler

def test_intelligence_reports():
    print("🚀 Triggering Institutional Intelligence Briefs...")
    
    scheduler = get_scheduler()

    print("\n1️⃣ Dispatching Tomorrow Blueprint (Sample)...")
    scheduler.run_blueprint()
    
    print("\n2️⃣ Dispatching Early Morning Global Brief (Sample)...")
    scheduler.run_global_brief()
    
    print("\n3️⃣ Dispatching Pre-Market Tactical Plan (Sample)...")
    scheduler.run_tactical_plan()

    print("\n✅ All Sample Briefs Dispatched to Telegram.")

if __name__ == "__main__":
    test_intelligence_reports()

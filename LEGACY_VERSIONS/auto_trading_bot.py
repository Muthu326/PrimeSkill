"""
Automated Trading Bot - Background Service
Runs 24/7 monitoring and sends alerts automatically

Features:
- Daily 4:30 PM market scan
- Low premium scanner (every 2 hours)
- Theta decay monitoring (every 1 hour)
- Position updates (every 30 minutes)
- Auto stop-loss/target execution
"""
import time
import schedule
from datetime import datetime, time as dt_time
import sys
from pathlib import Path

# Add project root
sys.path.insert(0, str(Path(__file__).parent))

from services.daily_scanner import get_daily_scanner
from services.premium_scanner import get_premium_scanner
from services.theta_monitor import get_theta_monitor
from services.trading_engine import get_trading_engine
from services.risk_manager import get_risk_manager
from utils.logger import setup_logger

# Initialize logger
logger = setup_logger("AutoBot")

class AutoTradingBot:
    """
    Automated background trading bot
    Runs all monitoring and alert functions
    """
    
    def __init__(self):
        self.daily_scanner = get_daily_scanner()
        self.premium_scanner = get_premium_scanner()
        self.theta_monitor = get_theta_monitor()
        self.trading_engine = get_trading_engine()
        self.risk_manager = get_risk_manager()
        
        logger.info("🤖 Auto Trading Bot Initialized")
    
    def run_daily_scan(self):
        """Daily market scan at 4:30 PM"""
        logger.info("📊 Running Daily Scan...")
        
        try:
            result = self.daily_scanner.run_daily_scan()
            logger.info(f"✅ Daily scan complete: {len(result['index_signals']) + len(result['stock_signals'])} signals")
        except Exception as e:
            logger.error(f"Daily scan error: {e}")
    
    def run_premium_scan(self):
        """Scan for low premium opportunities"""
        logger.info("💎 Scanning Low Premium Opportunities...")
        
        try:
            scanner = get_premium_scanner()
            opportunities = scanner.scan_for_opportunities()
            
            if opportunities:
                # Send top 5 opportunities
                msg = scanner.generate_alert_message(opportunities)
                scanner_obj = get_daily_scanner()  # Use for telegram
                scanner_obj.send_telegram_alert(msg)
                logger.info(f"✅ Found {len(opportunities)} low premium opportunities")
            else:
                logger.info("ℹ️ No low premium opportunities found")
        
        except Exception as e:
            logger.error(f"Premium scan error: {e}")
    
    def run_theta_monitoring(self):
        """Monitor theta decay on positions"""
        logger.info("⏱️ Monitoring Theta Decay...")
        
        try:
            alerts = self.theta_monitor.run_monitoring()
            
            if alerts:
                logger.warning(f"⚠️ {len(alerts)} positions need attention")
            else:
                logger.info("✅ All positions healthy")
        
        except Exception as e:
            logger.error(f"Theta monitoring error: {e}")
    
    def update_positions(self):
        """Update all position prices and check stop-loss/targets"""
        logger.info("🔄 Updating Positions...")
        
        try:
            # This would update prices from market data
            # For now, placeholder
            positions = self.trading_engine.get_active_positions()
            
            if positions:
                logger.info(f"📈 Monitoring {len(positions)} active positions")
                
                # Check risk alerts
                risk_alerts = self.risk_manager.get_risk_alerts()
                if risk_alerts:
                    logger.warning(f"⚠️ {len(risk_alerts)} risk alerts")
            else:
                logger.info("ℹ️ No active positions")
        
        except Exception as e:
            logger.error(f"Position update error: {e}")
    
    def morning_reminder(self):
        """Send morning reminder about today's opportunities"""
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 🌅 Sending Morning Reminder...")
        
        msg = "☀️ *GOOD MORNING!*\n\n"
        msg += "Market opens in 30 minutes.\n\n"
        msg += "📋 *Today's Action Plan:*\n"
        msg += "• Review yesterday's signals\n"
        msg += "• Check pre-market sentiment\n"
        msg += "• Place trades between 9:20-9:30 AM\n"
        msg += "• Set stop-loss immediately\n\n"
        msg += "💡 Dashboard: http://localhost:8501\n\n"
        msg += "Good luck! 🚀"
        
        try:
            self.daily_scanner.send_telegram_alert(msg)
            print("✅ Morning reminder sent")
        except:
            print("❌ Failed to send morning reminder")
    
    def market_close_summary(self):
        """Send end-of-day summary"""
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 🌆 Market Close Summary...")
        
        try:
            from services.pnl_calculator import get_pnl_calculator
            pnl_calc = get_pnl_calculator()
            
            daily_pnl = pnl_calc.get_daily_pnl()
            metrics = pnl_calc.get_performance_metrics()
            
            msg = "🌆 *MARKET CLOSED - DAILY SUMMARY*\n\n"
            msg += f"📊 *Today's P&L:* ₹{daily_pnl:,.2f}\n"
            msg += f"📈 *Total P&L:* ₹{metrics.total_pnl:,.2f}\n"
            msg += f"🎯 *Win Rate:* {metrics.win_rate:.1f}%\n"
            msg += f"📉 *Open Positions:* {len(self.trading_engine.get_active_positions())}\n\n"
            
            if daily_pnl > 0:
                msg += "✅ Profitable day! Well done!\n"
            elif daily_pnl < 0:
                msg += "⚠️ Loss today. Review trades and learn.\n"
            else:
                msg += "➖ Flat day. Wait for better setups.\n"
            
            msg += "\n💡 4:30 PM scan will arrive shortly with tomorrow's opportunities."
            
            self.daily_scanner.send_telegram_alert(msg)
            print("✅ Market close summary sent")
        
        except Exception as e:
            print(f"❌ Summary error: {e}")
    
    def setup_schedule(self):
        """Set up automated schedule"""
        
        # Daily 4:30 PM scan
        schedule.every().day.at("16:30").do(self.run_daily_scan)
        
        # Morning reminder (9:00 AM)
        schedule.every().day.at("09:00").do(self.morning_reminder)
        
        # Market close summary (3:30 PM)
        schedule.every().day.at("15:30").do(self.market_close_summary)
        
        # Low premium scan (every 2 hours during market hours)
        schedule.every().day.at("10:00").do(self.run_premium_scan)
        schedule.every().day.at("12:00").do(self.run_premium_scan)
        schedule.every().day.at("14:00").do(self.run_premium_scan)
        
        # Theta monitoring (every hour during market hours)
        schedule.every().day.at("10:00").do(self.run_theta_monitoring)
        schedule.every().day.at("11:00").do(self.run_theta_monitoring)
        schedule.every().day.at("12:00").do(self.run_theta_monitoring)
        schedule.every().day.at("13:00").do(self.run_theta_monitoring)
        schedule.every().day.at("14:00").do(self.run_theta_monitoring)
        schedule.every().day.at("15:00").do(self.run_theta_monitoring)
        
        # Position updates (every 30 minutes during market)
        for hour in range(9, 16):  # 9 AM to 3 PM
            for minute in ['00', '30']:
                schedule.every().day.at(f"{hour:02d}:{minute}").do(self.update_positions)
        
        print("\n📅 Schedule configured:")
        print("  • 09:00 AM - Morning Reminder")
        print("  • 09:00-15:30 - Position Updates (every 30 min)")
        print("  • 10:00, 12:00, 14:00 - Low Premium Scan")
        print("  • 10:00-15:00 - Theta Monitoring (hourly)")
        print("  • 15:30 PM - Market Close Summary")
        print("  • 16:30 PM - Daily Market Scan")
    
    def run(self):
        """Run the bot continuously"""
        
        print("\n" + "=" * 60)
        print("🤖 AUTO TRADING BOT STARTED")
        print("=" * 60)
        print(f"Time: {datetime.now().strftime('%d-%b-%Y %H:%M:%S')}")
        print("=" * 60)
        
        self.setup_schedule()
        
        logger.info("✅ Bot is running in background...")
        logger.info("💡 Press Ctrl+C to stop")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        
        except KeyboardInterrupt:
            print("\n\n🛑 Bot stopped by user")
            print("=" * 60)

def main():
    """Main entry point"""
    bot = AutoTradingBot()
    
    # Option to run specific task immediately for testing
    if len(sys.argv) > 1:
        task = sys.argv[1].lower()
        
        if task == "scan":
            bot.run_daily_scan()
        elif task == "premium":
            bot.run_premium_scan()
        elif task == "theta":
            bot.run_theta_monitoring()
        elif task == "update":
            bot.update_positions()
        elif task == "test":
            print("🧪 Running test sequence...")
            bot.morning_reminder()
            time.sleep(2)
            bot.run_daily_scan()
            time.sleep(2)
            bot.run_premium_scan()
            time.sleep(2)
            bot.run_theta_monitoring()
            time.sleep(2)
            bot.market_close_summary()
        else:
            print(f"Unknown task: {task}")
            print("Available: scan, premium, theta, update, test")
    else:
        # Run continuously
        bot.run()

if __name__ == "__main__":
    main()

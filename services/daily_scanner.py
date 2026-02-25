"""
Daily Market Scanner - Automated 4:30 PM Analysis
Predicts next day CE/PE opportunities
"""
import pandas as pd
import numpy as np
from datetime import datetime, time, timedelta
import yfinance as yf
from typing import List, Dict, Tuple
import urllib.request
import urllib.parse
import json

from models.trade_models import OptionType, TrendType
from config.config import TELEGRAM_CONFIG, SYMBOLS, ALL_FO_STOCKS
from services.strategy_engine import get_strategy_engine
from services.options_pricer import get_options_pricer
from services.market_engine import calculate_indicators
from database import get_db_manager

# F&O Stocks List
FO_STOCKS = ALL_FO_STOCKS

class DailyScanner:
    """
    Automated Daily Scanner
    - Runs at 4:30 PM daily
    - Scans all indices and F&O stocks
    - Predicts next day CE/PE opportunities
    - Sends comprehensive report via Telegram/WhatsApp
    """
    
    def __init__(self):
        self.strategy_engine = get_strategy_engine()
        self.pricer = get_options_pricer()
        self.db = get_db_manager()
    
    def should_run_scan(self) -> bool:
        """Check if it's time to run daily scan (4:30 PM)"""
        now = datetime.now()
        target_time = time(16, 30)  # 4:30 PM
        
        # Check if within 5 minutes of target time
        current_time = now.time()
        time_diff = abs((datetime.combine(datetime.today(), current_time) - 
                        datetime.combine(datetime.today(), target_time)).seconds)
        
        return time_diff < 300  # Within 5 minutes
    
    def get_market_data(self, symbol: str, period: str = "20d") -> pd.DataFrame:
        """Fetch market data for symbol"""
        try:
            df = yf.download(symbol, period=period, interval="1d", progress=False)
            
            if df.empty:
                return pd.DataFrame()
            
            # Use unified indicator engine
            df = calculate_indicators(df)
            
            return df
        
        except Exception as e:
            print(f"Error fetching data for {symbol}: {e}")
            return pd.DataFrame()
    
    def analyze_symbol(self, symbol: str, name: str) -> Dict:
        """Analyze single symbol for opportunities"""
        df = self.get_market_data(symbol)
        
        if df.empty or len(df) < 20:
            return None
        
        latest = df.iloc[-1]
        spot = latest['Close']
        rsi = latest.get('RSI', 50)
        ema20 = latest.get('EMA20', spot)
        ema50 = latest.get('EMA50', spot)
        
        # Determine trend
        if spot > ema20 > ema50 and rsi > 50:
            trend = TrendType.BULLISH
            signal_type = "CALL"
            confidence = min(95, (rsi - 50) * 2 + (spot/ema20 - 1) * 100)
        elif spot < ema20 < ema50 and rsi < 50:
            trend = TrendType.BEARISH
            signal_type = "PUT"
            confidence = min(95, (50 - rsi) * 2 + (1 - spot/ema20) * 100)
        else:
            return None  # Skip neutral/sideways
        
        # Estimate IV
        iv = self.pricer.estimate_iv_from_history(name)
        
        # Get strike recommendation
        strike_gap = 50 if "NIFTY" in name else (100 if "BANK" in name else 50)
        atm_strike = round(spot / strike_gap) * strike_gap
        
        if signal_type == "CALL":
            recommended_strike = atm_strike  # ATM for aggressive
        else:
            recommended_strike = atm_strike  # ATM for aggressive
        
        # Calculate premium
        days_to_expiry = self._get_next_expiry_days()
        
        if signal_type == "CALL":
            premium = self.pricer.bs_calculator.call_price(
                spot, recommended_strike, days_to_expiry/365, 0.06, iv/100
            )
        else:
            premium = self.pricer.bs_calculator.put_price(
                spot, recommended_strike, days_to_expiry/365, 0.06, iv/100
            )
        
        # Calculate targets
        target_price = premium * 1.8  # 80% profit
        stop_loss = premium * 0.6   # 40% stop loss
        
        return {
            'symbol': name,
            'spot': round(spot, 2),
            'trend': trend.value,
            'signal': signal_type,
            'confidence': round(confidence, 1),
            'strike': recommended_strike,
            'premium': round(premium, 2),
            'target': round(target_price, 2),
            'stop_loss': round(stop_loss, 2),
            'rsi': round(rsi, 2),
            'iv': round(iv, 2),
            'days_to_expiry': days_to_expiry
        }
    
    def _get_next_expiry_days(self) -> int:
        """Get days to next Thursday (weekly expiry)"""
        now = datetime.now()
        days_ahead = 3 - now.weekday()  # Thursday is 3
        if days_ahead <= 0:
            days_ahead += 7
        return max(1, days_ahead)
    
    def scan_all_indices(self) -> List[Dict]:
        """Scan all 5 indices"""
        indices = [
            ("^NSEI", "NIFTY50"),
            ("^BSESN", "SENSEX"),
            ("^NSEBANK", "BANKNIFTY"),
            ("NIFTY_FIN_SERVICE", "FINNIFTY"),
            ("NIFTY_MID_SELECT", "MIDCPNIFTY")
        ]
        
        results = []
        
        print("📊 Scanning Indices...")
        for ticker, name in indices:
            try:
                result = self.analyze_symbol(ticker, name)
                if result:
                    results.append(result)
                    print(f"✅ {name}: {result['signal']} @ {result['premium']}")
            except Exception as e:
                print(f"❌ Error scanning {name}: {e}")
        
        return results
    
    def scan_top_fo_stocks(self, limit: int = 20) -> List[Dict]:
        """Scan top F&O stocks with strong signals"""
        results = []
        
        print(f"📈 Scanning Top {limit} F&O Stocks...")
        
        for stock in FO_STOCKS[:limit]:  # Scan first 20 for speed
            try:
                name = stock.replace(".NS", "")
                result = self.analyze_symbol(stock, name)
                
                if result and result['confidence'] > 70:  # Only strong signals
                    results.append(result)
                    print(f"✅ {name}: {result['signal']} @ ₹{result['premium']}")
            
            except Exception as e:
                pass  # Skip errors silently for stocks
        
        # Sort by confidence
        results.sort(key=lambda x: x['confidence'], reverse=True)
        
        return results[:10]  # Top 10 stocks
    
    def generate_report(self, index_signals: List[Dict], stock_signals: List[Dict]) -> str:
        """Generate comprehensive daily report"""
        report = "🎯 *DAILY F&O OPPORTUNITIES REPORT*\n"
        report += f"📅 Date: {datetime.now().strftime('%d-%b-%Y')}\n"
        report += f"⏰ Generated at: {datetime.now().strftime('%I:%M %p')}\n"
        report += "=" * 40 + "\n\n"
        
        # Index Signals
        if index_signals:
            report += "📊 *INDEX SIGNALS* (Top Picks)\n\n"
            
            for sig in index_signals:
                report += f"*{sig['symbol']}*\n"
                report += f"  Spot: ₹{sig['spot']:,.2f}\n"
                report += f"  Signal: *{sig['signal']}* ({sig['confidence']:.0f}% confidence)\n"
                report += f"  Strike: {sig['strike']}\n"
                report += f"  Premium: ₹{sig['premium']:.2f}\n"
                report += f"  Target: ₹{sig['target']:.2f} (+80%)\n"
                report += f"  Stop Loss: ₹{sig['stop_loss']:.2f} (-40%)\n"
                report += f"  RSI: {sig['rsi']:.0f} | IV: {sig['iv']:.0f}%\n"
                report += f"  Days to Expiry: {sig['days_to_expiry']}\n"
                report += "\n"
        
        # Stock Signals
        if stock_signals:
            report += "📈 *TOP F&O STOCK OPPORTUNITIES*\n\n"
            
            for idx, sig in enumerate(stock_signals[:5], 1):  # Top 5
                report += f"{idx}. *{sig['symbol']}*\n"
                report += f"   {sig['signal']} @ ₹{sig['premium']:.2f} → Target: ₹{sig['target']:.2f}\n"
                report += f"   Confidence: {sig['confidence']:.0f}% | RSI: {sig['rsi']:.0f}\n\n"
        
        # Summary
        report += "=" * 40 + "\n"
        report += f"✅ Total Opportunities: {len(index_signals) + len(stock_signals)}\n"
        report += f"📊 Indices: {len(index_signals)} signals\n"
        report += f"📈 Stocks: {len(stock_signals)} signals\n\n"
        
        report += "⚠️ *Risk Management:*\n"
        report += "• Always use stop loss (-40%)\n"
        report += "• Book profit at target (+80%)\n"
        report += "• Max 2% capital per trade\n"
        report += "• Avoid trading on expiry day\n\n"
        
        report += "💡 *Next Steps:*\n"
        report += "1. Review signals in dashboard\n"
        report += "2. Place trades tomorrow morning (9:20-9:30 AM)\n"
        report += "3. Monitor positions throughout the day\n"
        report += "4. Book profits at targets\n\n"
        
        report += "_This is a paper trading system. No real money involved._\n"
        report += "📱 Check dashboard for detailed analysis"
        
        return report
    
    def send_telegram_alert(self, message: str):
        """Send alert via Telegram"""
        try:
            url = f"https://api.telegram.org/bot{TELEGRAM_CONFIG['token']}/sendMessage"
            data = urllib.parse.urlencode({
                'chat_id': TELEGRAM_CONFIG['chat_id'],
                'text': message,
                'parse_mode': 'Markdown'
            }).encode('utf-8')
            
            req = urllib.request.Request(url, data=data)
            with urllib.request.urlopen(req, timeout=10) as response:
                result = json.loads(response.read().decode('utf-8'))
                return result.get('ok', False)
        
        except Exception as e:
            print(f"Telegram error: {e}")
            return False
    
    def send_whatsapp_alert(self, message: str, phone: str = None):
        """
        Send alert via WhatsApp using Twilio/WATI/CallMeBot
        
        For CallMeBot (Free):
        1. Save +34 644 17 04 03 to contacts
        2. Send "I allow callmebot to send me messages" via WhatsApp
        3. You'll get API key
        """
        # This is a placeholder - you need to configure WhatsApp API
        # Options:
        # 1. CallMeBot (Free, simple)
        # 2. Twilio (Paid, official)
        # 3. WATI (Paid, business)
        
        print(f"WhatsApp alert ready: {message[:100]}...")
        
        # TODO: Implement based on your preference
        # For CallMeBot:
        # url = f"https://api.callmebot.com/whatsapp.php?phone={phone}&text={urllib.parse.quote(message)}&apikey=YOUR_API_KEY"
        
        pass
    
    def run_daily_scan(self):
        """Run complete daily scan"""
        print("\n" + "=" * 50)
        print("🚀 STARTING DAILY MARKET SCAN")
        print("=" * 50)
        
        # Scan indices
        index_signals = self.scan_all_indices()
        
        # Scan stocks
        stock_signals = self.scan_top_fo_stocks(limit=30)
        
        # Generate report
        report = self.generate_report(index_signals, stock_signals)
        
        # Send alerts
        print("\n📱 Sending alerts...")
        
        # Telegram
        success = self.send_telegram_alert(report)
        if success:
            print("✅ Telegram alert sent!")
        else:
            print("❌ Telegram failed")
        
        # WhatsApp (if configured)
        # self.send_whatsapp_alert(report, phone="YOUR_PHONE")
        
        # Save to database
        self.db.save_alert("DAILY_SCAN", report, severity="INFO")
        
        print("\n✅ Daily scan completed!")
        print("=" * 50)
        
        return {
            'index_signals': index_signals,
            'stock_signals': stock_signals,
            'report': report
        }

# Singleton
_daily_scanner = None

def get_daily_scanner() -> DailyScanner:
    """Get singleton daily scanner"""
    global _daily_scanner
    if _daily_scanner is None:
        _daily_scanner = DailyScanner()
    return _daily_scanner

# CLI Test
if __name__ == "__main__":
    scanner = get_daily_scanner()
    result = scanner.run_daily_scan()
    
    print("\n📊 RESULTS:")
    print(f"Index Signals: {len(result['index_signals'])}")
    print(f"Stock Signals: {len(result['stock_signals'])}")

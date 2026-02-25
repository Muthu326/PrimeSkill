"""
Strategy Engine - Advanced F&O Options Trading Strategies
Implements 7 profitable strategies with technical analysis
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any

from models.trade_models import (
    StrategyType, StrategySignal, MarketCondition, TrendType,
    OptionType, Greeks
)
from config.config import STRATEGY_PARAMS, IV_THRESHOLDS, EXPIRY_CONFIG, RISK_LIMITS
from services.options_pricer import get_options_pricer

class StrategyEngine:
    """
    Advanced Strategy Evaluation Engine
    Analyzes market conditions and generates trading signals
    """
    
    def __init__(self):
        self.options_pricer = get_options_pricer()
    
    def analyze_market_condition(self, df: pd.DataFrame, symbol: str, spot: float) -> MarketCondition:
        """
        Comprehensive market analysis using technical indicators
        
        Args:
            df: DataFrame with OHLCV and indicators (from calculate_indicators())
            symbol: Trading symbol
            spot: Current spot price
        
        Returns:
            MarketCondition object with complete analysis
        """
        if df.empty or len(df) < 20:
            return MarketCondition(
                symbol=symbol,
                spot_price=spot,
                trend=TrendType.NEUTRAL,
                rsi=50.0,
                adx=20.0,
                iv=20.0,
                iv_regime="NORMAL"
            )
        
        latest = df.iloc[-1]
        
        # Get indicators
        rsi = latest.get('RSI', 50.0)
        adx = latest.get('ADX', 20.0)
        ema20 = latest.get('EMA20', spot)
        ema50 = latest.get('EMA50', spot)
        ema200 = latest.get('EMA200', spot) if 'EMA200' in df.columns else ema50
        support = latest.get('Support', spot * 0.98)
        resistance = latest.get('Resistance', spot * 1.02)
        supertrend = latest.get('Supertrend', spot)
        
        # Determine trend
        if spot > ema20 > ema50 and rsi > 50:
            trend = TrendType.BULLISH
        elif spot < ema20 < ema50 and rsi < 50:
            trend = TrendType.BEARISH
        elif abs(spot - ema20) < (spot * 0.01):  # Within 1% of EMA20
            trend = TrendType.RANGE_BOUND
        else:
            trend = TrendType.NEUTRAL
        
        # Estimate IV
        iv = self.options_pricer.estimate_iv_from_history(symbol)
        
        # IV Regime
        if iv < IV_THRESHOLDS['LOW']:
            iv_regime = "LOW"
        elif iv < IV_THRESHOLDS['NORMAL']:
            iv_regime = "NORMAL"
        elif iv < IV_THRESHOLDS['HIGH']:
            iv_regime = "HIGH"
        else:
            iv_regime = "VERY_HIGH"
        
        # Trading signal
        if spot > supertrend and rsi > 40 and rsi < 70 and adx > 20:
            signal = "BUY"
            confidence = min(0.95, (adx / 40) * 0.8)
        elif spot < supertrend and rsi < 60 and rsi > 30 and adx > 20:
            signal = "SELL"
            confidence = min(0.95, (adx / 40) * 0.8)
        else:
            signal = "NEUTRAL"
            confidence = 0.5
        
        return MarketCondition(
            symbol=symbol,
            spot_price=spot,
            trend=trend,
            rsi=round(rsi, 2),
            adx=round(adx, 2),
            iv=round(iv, 2),
            iv_regime=iv_regime,
            support=round(support, 2),
            resistance=round(resistance, 2),
            ema20=round(ema20, 2),
            ema50=round(ema50, 2),
            supertrend=round(supertrend, 2),
            signal=signal,
            confidence=round(confidence, 2)
        )
    
    def evaluate_long_call(self, market: MarketCondition, days_to_expiry: int) -> Optional[StrategySignal]:
        """
        Evaluate LONG CALL strategy
        Best for: Strong bullish trends with low to moderate IV
        """
        params = STRATEGY_PARAMS['LONG_CALL']
        
        # Check conditions
        if (market.trend not in [TrendType.BULLISH] or
            market.rsi < params['min_rsi'] or
            market.rsi > params['max_rsi'] or
            market.adx < params['min_adx'] or
            market.iv_regime not in ['LOW', 'NORMAL']):
            return None
        
        # Select strike (ATM or slightly OTM for better leverage)
        strike = self.options_pricer.get_option_by_moneyness(
            market.spot_price, market.symbol, params['strike_selection'].split('_')[0], "CE"
        )
        
        # Calculate premium and Greeks
        premium = self.options_pricer.bs_calculator.call_price(
            market.spot_price, strike, days_to_expiry/365, 0.06, market.iv/100
        )
        greeks = self.options_pricer.bs_calculator.calculate_greeks(
            market.spot_price, strike, days_to_expiry/365, 0.06, market.iv/100, "CE"
        )
        
        # Risk management
        entry_price = round(premium, 2)
        stop_loss = round(entry_price * (1 - RISK_LIMITS['stop_loss_percent']), 2)
        target = round(entry_price * (1 + RISK_LIMITS['target_profit_percent']), 2)
        max_loss = -entry_price
        max_profit = float('inf')  # Theoretically unlimited
        risk_reward = abs(target - entry_price) / abs(stop_loss - entry_price) if stop_loss != entry_price else 0
        
        # Confidence based on trend strength
        confidence = min(0.95, market.adx / 40 * 0.9) if market.signal == "BUY" else 0.6
        
        return StrategySignal(
            strategy_type=StrategyType.LONG_CALL,
            symbol=market.symbol,
            action="BUY",
            confidence=round(confidence, 2),
            entry_price=entry_price,
            stop_loss=stop_loss,
            target=target,
            position_size=1,
            max_loss=max_loss,
            max_profit=max_profit,
            risk_reward=round(risk_reward, 2),
            market_condition=market,
            option_legs=[{
                'type': 'CE',
                'strike': strike,
                'action': 'BUY',
                'premium': entry_price,
                'delta': greeks.delta
            }],
            notes=f"Bullish trend detected. RSI: {market.rsi}, ADX: {market.adx}, IV: {market.iv}%"
        )
    
    def evaluate_long_put(self, market: MarketCondition, days_to_expiry: int) -> Optional[StrategySignal]:
        """
        Evaluate LONG PUT strategy
        Best for: Strong bearish trends with low to moderate IV
        """
        params = STRATEGY_PARAMS['LONG_PUT']
        
        # Check conditions
        if (market.trend not in [TrendType.BEARISH] or
            market.rsi < params['min_rsi'] or
            market.rsi > params['max_rsi'] or
            market.adx < params['min_adx'] or
            market.iv_regime not in ['LOW', 'NORMAL']):
            return None
        
        # Select strike
        strike = self.options_pricer.get_option_by_moneyness(
            market.spot_price, market.symbol, params['strike_selection'].split('_')[0], "PE"
        )
        
        # Calculate premium and Greeks
        premium = self.options_pricer.bs_calculator.put_price(
            market.spot_price, strike, days_to_expiry/365, 0.06, market.iv/100
        )
        greeks = self.options_pricer.bs_calculator.calculate_greeks(
            market.spot_price, strike, days_to_expiry/365, 0.06, market.iv/100, "PE"
        )
        
        entry_price = round(premium, 2)
        stop_loss = round(entry_price * (1 - RISK_LIMITS['stop_loss_percent']), 2)
        target = round(entry_price * (1 + RISK_LIMITS['target_profit_percent']), 2)
        max_loss = -entry_price
        max_profit = float('inf')
        risk_reward = abs(target - entry_price) / abs(stop_loss - entry_price) if stop_loss != entry_price else 0
        
        confidence = min(0.95, market.adx / 40 * 0.9) if market.signal == "SELL" else 0.6
        
        return StrategySignal(
            strategy_type=StrategyType.LONG_PUT,
            symbol=market.symbol,
            action="BUY",
            confidence=round(confidence, 2),
            entry_price=entry_price,
            stop_loss=stop_loss,
            target=target,
            position_size=1,
            max_loss=max_loss,
            max_profit=max_profit,
            risk_reward=round(risk_reward, 2),
            market_condition=market,
            option_legs=[{
                'type': 'PE',
                'strike': strike,
                'action': 'BUY',
                'premium': entry_price,
                'delta': greeks.delta
            }],
            notes=f"Bearish trend detected. RSI: {market.rsi}, ADX: {market.adx}, IV: {market.iv}%"
        )
    
    def evaluate_bull_call_spread(self, market: MarketCondition, days_to_expiry: int) -> Optional[StrategySignal]:
        """
        Evaluate BULL CALL SPREAD strategy
        Best for: Moderately bullish with high IV (to reduce cost)
        """
        params = STRATEGY_PARAMS['BULL_CALL_SPREAD']
        
        if (market.trend not in [TrendType.BULLISH] or
            market.rsi < params['min_rsi'] or
            market.iv_regime not in ['HIGH', 'VERY_HIGH']):
            return None
        
        # Buy ATM call
        buy_strike = self.options_pricer.get_option_by_moneyness(
            market.spot_price, market.symbol, "ATM", "CE"
        )
        buy_premium = self.options_pricer.bs_calculator.call_price(
            market.spot_price, buy_strike, days_to_expiry/365, 0.06, market.iv/100
        )
        
        # Sell OTM2 call
        sell_strike = self.options_pricer.get_option_by_moneyness(
            market.spot_price, market.symbol, "OTM2", "CE"
        )
        sell_premium = self.options_pricer.bs_calculator.call_price(
            market.spot_price, sell_strike, days_to_expiry/365, 0.06, market.iv/100
        )
        
        # Net debit
        net_debit = buy_premium - sell_premium
        entry_price = round(net_debit, 2)
        
        # Max profit when spot > sell_strike at expiry
        max_profit = (sell_strike - buy_strike) - net_debit
        max_loss = -net_debit
        
        stop_loss = round(entry_price * (1 - RISK_LIMITS['stop_loss_percent']), 2)
        target = round(max_profit * 0.7, 2)  # Target 70% of max profit
        risk_reward = abs(target) / abs(max_loss) if max_loss != 0 else 0
        
        confidence = min(0.85, market.adx / 35 * 0.8)
        
        return StrategySignal(
            strategy_type=StrategyType.BULL_CALL_SPREAD,
            symbol=market.symbol,
            action="BUY",
            confidence=round(confidence, 2),
            entry_price=entry_price,
            stop_loss=stop_loss,
            target=target,
            position_size=1,
            max_loss=round(max_loss, 2),
            max_profit=round(max_profit, 2),
            risk_reward=round(risk_reward, 2),
            market_condition=market,
            option_legs=[
                {'type': 'CE', 'strike': buy_strike, 'action': 'BUY', 'premium': round(buy_premium, 2)},
                {'type': 'CE', 'strike': sell_strike, 'action': 'SELL', 'premium': round(sell_premium, 2)}
            ],
            notes=f"Bull Call Spread. Net Debit: ₹{entry_price}. Max Profit: ₹{max_profit:.2f}"
        )
    
    def evaluate_bear_put_spread(self, market: MarketCondition, days_to_expiry: int) -> Optional[StrategySignal]:
        """
        Evaluate BEAR PUT SPREAD strategy
        Best for: Moderately bearish with high IV
        """
        params = STRATEGY_PARAMS['BEAR_PUT_SPREAD']
        
        if (market.trend not in [TrendType.BEARISH] or
            market.rsi > params['max_rsi'] or
            market.iv_regime not in ['HIGH', 'VERY_HIGH']):
            return None
        
        # Buy ATM put
        buy_strike = self.options_pricer.get_option_by_moneyness(
            market.spot_price, market.symbol, "ATM", "PE"
        )
        buy_premium = self.options_pricer.bs_calculator.put_price(
            market.spot_price, buy_strike, days_to_expiry/365, 0.06, market.iv/100
        )
        
        # Sell OTM2 put
        sell_strike = self.options_pricer.get_option_by_moneyness(
            market.spot_price, market.symbol, "OTM2", "PE"
        )
        sell_premium = self.options_pricer.bs_calculator.put_price(
            market.spot_price, sell_strike, days_to_expiry/365, 0.06, market.iv/100
        )
        
        net_debit = buy_premium - sell_premium
        entry_price = round(net_debit, 2)
        
        max_profit = (buy_strike - sell_strike) - net_debit
        max_loss = -net_debit
        
        stop_loss = round(entry_price * (1 - RISK_LIMITS['stop_loss_percent']), 2)
        target = round(max_profit * 0.7, 2)
        risk_reward = abs(target) / abs(max_loss) if max_loss != 0 else 0
        
        confidence = min(0.85, market.adx / 35 * 0.8)
        
        return StrategySignal(
            strategy_type=StrategyType.BEAR_PUT_SPREAD,
            symbol=market.symbol,
            action="BUY",
            confidence=round(confidence, 2),
            entry_price=entry_price,
            stop_loss=stop_loss,
            target=target,
            position_size=1,
            max_loss=round(max_loss, 2),
            max_profit=round(max_profit, 2),
            risk_reward=round(risk_reward, 2),
            market_condition=market,
            option_legs=[
                {'type': 'PE', 'strike': buy_strike, 'action': 'BUY', 'premium': round(buy_premium, 2)},
                {'type': 'PE', 'strike': sell_strike, 'action': 'SELL', 'premium': round(sell_premium, 2)}
            ],
            notes=f"Bear Put Spread. Net Debit: ₹{entry_price}. Max Profit: ₹{max_profit:.2f}"
        )
    
    def evaluate_long_straddle(self, market: MarketCondition, days_to_expiry: int) -> Optional[StrategySignal]:
        """
        Evaluate LONG STRADDLE strategy
        Best for: Expecting big move (high volatility) with currently low IV
        """
        params = STRATEGY_PARAMS['LONG_STRADDLE']
        
        if (market.iv_regime not in ['LOW', 'NORMAL'] or
            market.rsi < params['min_rsi'] or
            market.rsi > params['max_rsi'] or
            market.trend != TrendType.NEUTRAL):
            return None
        
        # Buy ATM call and ATM put
        atm_strike = self.options_pricer.get_option_by_moneyness(
            market.spot_price, market.symbol, "ATM", "CE"
        )
        
        call_premium = self.options_pricer.bs_calculator.call_price(
            market.spot_price, atm_strike, days_to_expiry/365, 0.06, market.iv/100
        )
        put_premium = self.options_pricer.bs_calculator.put_price(
            market.spot_price, atm_strike, days_to_expiry/365, 0.06, market.iv/100
        )
        
        total_premium = call_premium + put_premium
        entry_price = round(total_premium, 2)
        
        # Breakevens
        upper_breakeven = atm_strike + total_premium
        lower_breakeven = atm_strike - total_premium
        
        max_loss = -total_premium
        max_profit = float('inf')
        
        stop_loss = round(entry_price * (1 - RISK_LIMITS['stop_loss_percent']), 2)
        target = round(entry_price * 1.5, 2)  # Target 50% profit
        risk_reward = 1.5
        
        confidence = 0.70 if market.iv < 20 else 0.60
        
        return StrategySignal(
            strategy_type=StrategyType.LONG_STRADDLE,
            symbol=market.symbol,
            action="BUY",
            confidence=round(confidence, 2),
            entry_price=entry_price,
            stop_loss=stop_loss,
            target=target,
            position_size=1,
            max_loss=round(max_loss, 2),
            max_profit=max_profit,
            risk_reward=round(risk_reward, 2),
            market_condition=market,
            option_legs=[
                {'type': 'CE', 'strike': atm_strike, 'action': 'BUY', 'premium': round(call_premium, 2)},
                {'type': 'PE', 'strike': atm_strike, 'action': 'BUY', 'premium': round(put_premium, 2)}
            ],
            notes=f"Long Straddle. Breakeven: {lower_breakeven:.0f} - {upper_breakeven:.0f}"
        )
    
    def evaluate_long_strangle(self, market: MarketCondition, days_to_expiry: int) -> Optional[StrategySignal]:
        """
        Evaluate LONG STRANGLE strategy
        Best for: Expecting VERY BIG move with low IV (cheaper than straddle)
        """
        params = STRATEGY_PARAMS['LONG_STRANGLE']
        
        if (market.iv_regime not in ['LOW'] or
            market.trend != TrendType.NEUTRAL):
            return None
        
        # Buy OTM call and OTM put
        call_strike = self.options_pricer.get_option_by_moneyness(
            market.spot_price, market.symbol, "OTM1", "CE"
        )
        put_strike = self.options_pricer.get_option_by_moneyness(
            market.spot_price, market.symbol, "OTM1", "PE"
        )
        
        call_premium = self.options_pricer.bs_calculator.call_price(
            market.spot_price, call_strike, days_to_expiry/365, 0.06, market.iv/100
        )
        put_premium = self.options_pricer.bs_calculator.put_price(
            market.spot_price, put_strike, days_to_expiry/365, 0.06, market.iv/100
        )
        
        total_premium = call_premium + put_premium
        entry_price = round(total_premium, 2)
        
        max_loss = -total_premium
        max_profit = float('inf')
        
        stop_loss = round(entry_price * (1 - RISK_LIMITS['stop_loss_percent']), 2)
        target = round(entry_price * 2.0, 2)  # Target 100% profit
        risk_reward = 2.0
        
        confidence = 0.65
        
        return StrategySignal(
            strategy_type=StrategyType.LONG_STRANGLE,
            symbol=market.symbol,
            action="BUY",
            confidence=round(confidence, 2),
            entry_price=entry_price,
            stop_loss=stop_loss,
            target=target,
            position_size=1,
            max_loss=round(max_loss, 2),
            max_profit=max_profit,
            risk_reward=round(risk_reward, 2),
            market_condition=market,
            option_legs=[
                {'type': 'CE', 'strike': call_strike, 'action': 'BUY', 'premium': round(call_premium, 2)},
                {'type': 'PE', 'strike': put_strike, 'action': 'BUY', 'premium': round(put_premium, 2)}
            ],
            notes=f"Long Strangle. Cheaper than straddle, needs bigger move to profit."
        )
    
    def evaluate_iron_condor(self, market: MarketCondition, days_to_expiry: int) -> Optional[StrategySignal]:
        """
        Evaluate IRON CONDOR strategy
        Best for: Range-bound market with high IV (premium collection)
        """
        params = STRATEGY_PARAMS['IRON_CONDOR']
        
        if (market.trend not in [TrendType.RANGE_BOUND, TrendType.NEUTRAL] or
            market.iv_regime not in ['HIGH', 'VERY_HIGH'] or
            market.adx > 25):  # Low ADX means no strong trend
            return None
        
        # This is a credit spread strategy (sell options, buy further OTM for protection)
        # We'll implement a simplified version for now
        
        # Note: Iron Condor is complex and requires careful risk management
        # Skipping for MVP, but structure is here
        
        return None  # TODO: Implement Iron Condor in Phase 2
    
    def get_strategy_recommendations(self, 
                                    df: pd.DataFrame,
                                    symbol: str,
                                    spot: float,
                                    days_to_expiry: int) -> List[StrategySignal]:
        """
        Get all applicable strategy recommendations for current market
        
        Args:
            df: DataFrame with technical indicators
            symbol: Trading symbol
            spot: Current spot price
            days_to_expiry: Days to expiry
        
        Returns:
            List of StrategySignal objects sorted by confidence
        """
        # Analyze market
        market = self.analyze_market_condition(df, symbol, spot)
        
        # Check expiry constraints
        if (days_to_expiry < EXPIRY_CONFIG['min_days_to_expiry'] or
            days_to_expiry > EXPIRY_CONFIG['max_days_to_expiry']):
            return []
        
        # Evaluate all strategies
        strategies = []
        
        signal = self.evaluate_long_call(market, days_to_expiry)
        if signal:
            strategies.append(signal)
        
        signal = self.evaluate_long_put(market, days_to_expiry)
        if signal:
            strategies.append(signal)
        
        signal = self.evaluate_bull_call_spread(market, days_to_expiry)
        if signal:
            strategies.append(signal)
        
        signal = self.evaluate_bear_put_spread(market, days_to_expiry)
        if signal:
            strategies.append(signal)
        
        signal = self.evaluate_long_straddle(market, days_to_expiry)
        if signal:
            strategies.append(signal)
        
        signal = self.evaluate_long_strangle(market, days_to_expiry)
        if signal:
            strategies.append(signal)
        
        # Sort by confidence (highest first)
        strategies.sort(key=lambda x: x.confidence, reverse=True)
        
        return strategies

# Singleton instance
_strategy_engine = None

def get_strategy_engine() -> StrategyEngine:
    """Get singleton strategy engine instance"""
    global _strategy_engine
    if _strategy_engine is None:
        _strategy_engine = StrategyEngine()
    return _strategy_engine

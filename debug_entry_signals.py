#!/usr/bin/env python3
"""진입 신호 디버깅"""

import asyncio
import sys
import os
from pathlib import Path

# 프로젝트 루트 경로를 sys.path에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from frontend.backtest.backend.engines.backtest_engine import BacktestEngine, BacktestConfig_

async def debug_entry_signals():
    """진입 신호 디버깅"""
    print("=== 진입 신호 디버깅 ===\n")
    
    # 테스트 설정 - 더 짧은 기간
    config = BacktestConfig_(
        symbol="BTCUSDT",
        start_date="2024-01-01", 
        end_date="2024-01-15",  # 2주로 단축
        timeframe="1d",
        initial_balance=10000.0,
        commission_rate=0.0004,
        leverage=1.0,
        systems=[1, 2]
    )
    
    engine = BacktestEngine(config)
    price_data = await engine.load_historical_data()
    
    print(f"생성된 데이터: {len(price_data)}개")
    print("가격 데이터 샘플:")
    for i, data in enumerate(price_data[:5]):
        print(f"  {i}: {data.date.strftime('%Y-%m-%d')} O:{data.open:.2f} H:{data.high:.2f} L:{data.low:.2f} C:{data.close:.2f}")
    
    print(f"\n진입 신호 체크 시작점: {min(30, len(price_data) - 1)}번째 데이터부터")
    
    # 진입 신호 확인
    signal_count = 0
    long_signals = 0
    short_signals = 0
    
    for i in range(min(30, len(price_data) - 1), len(price_data)):
        current_data = price_data[:i+1]
        current_price = current_data[-1].close
        
        # ATR 계산
        try:
            atr_period = min(20, len(current_data) - 1)
            if atr_period < 2:
                continue
            atr = engine.turtle_strategy.indicators.calculate_atr(current_data[-atr_period-1:], atr_period)
        except:
            continue
        
        # 신호 체크
        for system in [1, 2]:
            long_signal = engine.turtle_strategy.check_entry_signal("BTCUSDT", current_data, system, "LONG")
            short_signal = engine.turtle_strategy.check_entry_signal("BTCUSDT", current_data, system, "SHORT")
            
            if long_signal or short_signal:
                signal_count += 1
                if long_signal:
                    long_signals += 1
                    print(f"📈 LONG 신호 발견! 날짜: {current_data[-1].date.strftime('%Y-%m-%d')}, 시스템: {system}, 가격: {current_price:.2f}")
                if short_signal:
                    short_signals += 1
                    print(f"📉 SHORT 신호 발견! 날짜: {current_data[-1].date.strftime('%Y-%m-%d')}, 시스템: {system}, 가격: {current_price:.2f}")
                
                # 돌파 상세 분석
                if system == 1:
                    period = 20
                elif system == 2:
                    period = 55
                    
                if len(current_data) >= period + 1:
                    if long_signal:
                        highest_high = max(p.high for p in current_data[-period-1:-1])
                        print(f"    롱 돌파: 현재가 {current_price:.2f} > {period}일 최고가 {highest_high:.2f}")
                    if short_signal:
                        lowest_low = min(p.low for p in current_data[-period-1:-1])
                        print(f"    숏 돌파: 현재가 {current_price:.2f} < {period}일 최저가 {lowest_low:.2f}")
    
    print(f"\n총 신호 수: {signal_count}")
    print(f"롱 신호: {long_signals}개")
    print(f"숏 신호: {short_signals}개")
    
    # 가격 트렌드 확인
    print(f"\n가격 트렌드 분석:")
    start_price = price_data[0].close
    end_price = price_data[-1].close
    trend = "상승" if end_price > start_price else "하락"
    change_pct = ((end_price - start_price) / start_price) * 100
    print(f"시작가: {start_price:.2f}")
    print(f"종료가: {end_price:.2f}")
    print(f"변화율: {change_pct:.2f}% ({trend})")

if __name__ == "__main__":
    asyncio.run(debug_entry_signals())
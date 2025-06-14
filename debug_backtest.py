#!/usr/bin/env python3
"""
백테스트 디버깅 스크립트
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))

from frontend.backtest.backend.engines.backtest_engine import BacktestEngine, BacktestConfig_

async def debug_backtest():
    config = BacktestConfig_(
        symbol='BTCUSDT',
        start_date='2024-01-01',
        end_date='2024-03-01',  # 2개월로 늘림
        timeframe='1d',
        initial_balance=10000.0,
        commission_rate=0.0004,
        systems=[1, 2]
    )
    
    engine = BacktestEngine(config)
    
    # 과거 데이터 로드
    price_data = await engine.load_historical_data()
    print(f"로드된 데이터: {len(price_data)}개 캔들")
    
    # 처음 몇 개 데이터 출력
    print("\n=== 가격 데이터 샘플 ===")
    for i, data in enumerate(price_data[:5]):
        print(f"{i+1}. {data.date.strftime('%Y-%m-%d')}: O:{data.open:.2f}, H:{data.high:.2f}, L:{data.low:.2f}, C:{data.close:.2f}")
    
    # ATR 계산 테스트
    try:
        atr_period = min(20, len(price_data) - 1)
        if atr_period >= 2:
            atr = engine.turtle_strategy.indicators.calculate_atr(price_data[-atr_period-1:], atr_period)
            print(f"\nATR ({atr_period}일): {atr:.2f}")
        else:
            print("\nATR 계산을 위한 데이터 부족")
    except Exception as e:
        print(f"ATR 계산 오류: {e}")
    
    # 진입 신호 확인
    print("\n=== 진입 신호 확인 ===")
    symbol = config.symbol
    
    for i in range(min(30, len(price_data) - 1), len(price_data)):
        current_data = price_data[:i+1]
        current_price = current_data[-1].close
        
        # 시스템별 진입 신호 확인
        for system in config.systems:
            long_signal = engine.turtle_strategy.check_entry_signal(symbol, current_data, system, "LONG")
            short_signal = engine.turtle_strategy.check_entry_signal(symbol, current_data, system, "SHORT")
            
            if long_signal or short_signal:
                print(f"날짜: {current_data[-1].date.strftime('%Y-%m-%d')}, 가격: {current_price:.2f}")
                print(f"  시스템 {system} - LONG: {long_signal}, SHORT: {short_signal}")
                
                # 돌파 상세 정보
                if system == 1:
                    period = 20
                elif system == 2:
                    period = 55
                
                if len(current_data) >= period + 1:
                    highest_high = max(p.high for p in current_data[-period-1:-1])
                    lowest_low = min(p.low for p in current_data[-period-1:-1])
                    print(f"  {period}일 최고가: {highest_high:.2f}, 최저가: {lowest_low:.2f}")
                    print(f"  현재가: {current_price:.2f}")
                    print(f"  상승 돌파 여부: {current_price > highest_high}")
                    print(f"  하락 돌파 여부: {current_price < lowest_low}")
        
        # 처음 몇 개 신호만 출력
        if i - min(30, len(price_data) - 1) >= 5:
            break
    
    print("\n=== 백테스트 실행 ===")
    results = await engine.run_backtest()
    
    print(f'총 거래 수: {results.metrics.total_trades}')
    print(f'롱 거래: {results.metrics.long_trades}')
    print(f'숏 거래: {results.metrics.short_trades}')
    
    return results

if __name__ == "__main__":
    # 실행
    results = asyncio.run(debug_backtest())
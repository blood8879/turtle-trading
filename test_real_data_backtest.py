#!/usr/bin/env python3
"""실제 데이터로 백테스트 테스트 (API 키 없이)"""

import asyncio
import sys
import os
from pathlib import Path

# 프로젝트 루트 경로를 sys.path에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from frontend.backtest.backend.engines.backtest_engine import BacktestEngine, BacktestConfig_

async def test_real_data_backtest():
    """실제 Binance 데이터로 백테스트 (API 키 없이)"""
    print("=== 실제 데이터 백테스트 테스트 ===\n")
    
    # 테스트 설정들
    test_configs = [
        {
            'name': '일봉 - 1개월',
            'config': BacktestConfig_(
                symbol="BTCUSDT",
                start_date="2024-05-01", 
                end_date="2024-05-31",
                timeframe="1d",
                initial_balance=10000.0,
                commission_rate=0.0004,
                leverage=1.0,
                systems=[1, 2]
            )
        },
        {
            'name': '4시간봉 - 1주일',
            'config': BacktestConfig_(
                symbol="BTCUSDT",
                start_date="2024-05-20", 
                end_date="2024-05-27",
                timeframe="4h",
                initial_balance=10000.0,
                commission_rate=0.0004,
                leverage=1.0,
                systems=[1, 2]
            )
        }
    ]
    
    for test in test_configs:
        print(f"🧪 테스트: {test['name']}")
        print("-" * 50)
        
        # 백테스트 실행
        engine = BacktestEngine(test['config'])
        results = await engine.run_backtest()
        
        print(f"📊 결과:")
        print(f"  초기 자금: ${results.initial_balance:,.2f}")
        print(f"  최종 자금: ${results.final_balance:,.2f}")
        print(f"  총 수익률: {results.metrics.total_return:.2%}")
        print(f"  총 거래 수: {results.metrics.total_trades}번")
        print(f"  승률: {results.metrics.win_rate:.1%}")
        print(f"  롱 거래: {results.metrics.long_trades}개")
        print(f"  숏 거래: {results.metrics.short_trades}개")
        
        # 거래 내역 (최대 3개)
        if results.trades:
            print(f"  최근 거래:")
            for i, trade in enumerate(results.trades[:3]):
                entry_date = trade.entry_date.strftime('%m-%d') if hasattr(trade.entry_date, 'strftime') else str(trade.entry_date)[:5]
                print(f"    {i+1}. {trade.direction} {trade.entry_price:.2f} -> {trade.exit_price:.2f} "
                      f"P&L: {trade.pnl:.2f} ({trade.exit_reason})")
        
        print("\n")

async def test_different_timeframes():
    """다양한 시간프레임 테스트"""
    print("=== 다양한 시간프레임 테스트 ===\n")
    
    timeframes = ['1h', '4h', '1d']
    
    for timeframe in timeframes:
        print(f"📈 {timeframe} 시간프레임 테스트")
        
        config = BacktestConfig_(
            symbol="BTCUSDT",
            start_date="2024-05-01", 
            end_date="2024-05-15",
            timeframe=timeframe,
            initial_balance=10000.0,
            commission_rate=0.0004,
            leverage=1.0,
            systems=[1, 2]
        )
        
        engine = BacktestEngine(config)
        
        # 데이터만 로드해서 확인
        try:
            data = await engine.load_historical_data(use_real_data=True)
            print(f"  ✅ {timeframe}: {len(data)}개 캔들 로드 성공")
            
            if data:
                print(f"    첫 데이터: {data[0].date.strftime('%Y-%m-%d %H:%M')} - ${data[0].close:,.2f}")
                print(f"    마지막 데이터: {data[-1].date.strftime('%Y-%m-%d %H:%M')} - ${data[-1].close:,.2f}")
        except Exception as e:
            print(f"  ❌ {timeframe}: 오류 - {e}")
        
        print()

if __name__ == "__main__":
    print("🚀 API 키 없이 실제 데이터 백테스트 시작\n")
    
    # 먼저 다양한 시간프레임 데이터 로드 테스트
    asyncio.run(test_different_timeframes())
    
    # 실제 백테스트 실행
    asyncio.run(test_real_data_backtest())
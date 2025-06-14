#!/usr/bin/env python3
"""
백테스트 테스트 스크립트
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import BacktestConfig
from frontend.backtest.backend.engines.backtest_engine import BacktestEngine


async def test_backtest():
    """백테스트 테스트 (레버리지 포함)"""
    print("🐢 백테스트 테스트 시작")
    
    try:
        # 레버리지 테스트 케이스들
        test_cases = [
            {"leverage": 1.0, "name": "현물 (1x)"},
            {"leverage": 2.0, "name": "2배 레버리지"},
            {"leverage": 5.0, "name": "5배 레버리지"},
            {"leverage": 10.0, "name": "10배 레버리지"}
        ]
        
        for test_case in test_cases:
            print(f"\n--- {test_case['name']} 테스트 ---")
            
            # 백테스트 설정
            config = BacktestConfig(
                symbol='BTCUSDT',
                start_date='2024-01-01', 
                end_date='2024-12-31',
                timeframe='1d',
                initial_balance=10000.0,
                commission_rate=0.0004,
                systems=[1, 2],
                leverage=test_case['leverage']
            )
            
            print(f"설정: {config.symbol}, {config.start_date} ~ {config.end_date}")
            print(f"초기 자금: ${config.initial_balance:,.2f}")
            print(f"레버리지: {config.leverage}x")
            
            # 백테스트 엔진 생성 및 실행
            engine = BacktestEngine(config)
            results = await engine.run_backtest()
            
            print(f"최종 자금: ${results.final_capital:,.2f}")
            print(f"총 수익률: {results.performance_metrics.total_return:.1%}")
            print(f"최대 낙폭: {results.performance_metrics.max_drawdown:.1%}")
            print(f"샤프 비율: {results.performance_metrics.sharpe_ratio:.2f}")
            print(f"승률: {results.performance_metrics.win_rate:.1%}")
            print(f"총 거래수: {results.performance_metrics.total_trades}")
        
        print("\n✅ 모든 레버리지 테스트 완료!")
        return True
        
    except Exception as e:
        print(f"❌ 백테스트 오류: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_backtest())
    if success:
        print("\n🎉 백테스트 테스트 성공!")
        sys.exit(0)
    else:
        print("\n💥 백테스트 테스트 실패!")
        sys.exit(1)
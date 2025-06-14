#!/usr/bin/env python3
"""간단한 실제 데이터 테스트"""

import asyncio
import sys
import os
from pathlib import Path
from datetime import datetime, timedelta

# 프로젝트 루트 경로를 sys.path에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from frontend.backtest.backend.engines.backtest_engine import BacktestEngine, BacktestConfig_

async def test_simple_real_data():
    """간단한 실제 데이터 테스트"""
    print("=== 간단한 실제 데이터 테스트 ===\n")
    
    # 더 최근 날짜로 설정 (과거 30일)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=60)  # 2개월 전
    
    config = BacktestConfig_(
        symbol="BTCUSDT",
        start_date=start_date.strftime('%Y-%m-%d'), 
        end_date=end_date.strftime('%Y-%m-%d'),
        timeframe="1d",
        initial_balance=10000.0,
        commission_rate=0.0004,
        leverage=1.0,
        systems=[1, 2]
    )
    
    print(f"📅 테스트 기간: {config.start_date} ~ {config.end_date}")
    
    # 백테스트 실행
    engine = BacktestEngine(config)
    results = await engine.run_backtest()
    
    print("\n📊 백테스트 결과:")
    print("=" * 50)
    print(f"초기 자금: ${results.initial_balance:,.2f}")
    print(f"최종 자금: ${results.final_balance:,.2f}")
    print(f"총 수익률: {results.metrics.total_return:.2%}")
    print(f"최대 드로다운: {results.metrics.max_drawdown:.2%}")
    print(f"샤프 비율: {results.metrics.sharpe_ratio:.2f}")
    
    print(f"\n📈 거래 통계:")
    print(f"총 거래 수: {results.metrics.total_trades}번")
    print(f"승률: {results.metrics.win_rate:.1%}")
    print(f"평균 수익: ${results.metrics.avg_win:,.2f}")
    print(f"평균 손실: ${results.metrics.avg_loss:,.2f}")
    print(f"롱 거래: {results.metrics.long_trades}개")
    print(f"숏 거래: {results.metrics.short_trades}개")
    
    # 거래 내역
    if results.trades:
        print(f"\n📋 거래 내역:")
        print("-" * 70)
        print("날짜       | 방향 | 진입가    | 청산가    | P&L      | 사유")
        print("-" * 70)
        
        for trade in results.trades:
            entry_date = trade.entry_date.strftime('%m-%d') if hasattr(trade.entry_date, 'strftime') else str(trade.entry_date)[:5]
            print(f"{entry_date} | {trade.direction:4} | {trade.entry_price:8.2f} | {trade.exit_price:8.2f} | "
                  f"{trade.pnl:8.2f} | {trade.exit_reason}")
        
        total_pnl = sum(t.pnl for t in results.trades)
        print("-" * 70)
        print(f"{'':40} 총 P&L: {total_pnl:8.2f}")
    
    # 실제 데이터 vs 시뮬레이션 데이터 확인
    if "실제 데이터" in str(results):
        print("\n✅ 실제 Binance 데이터 사용됨")
    else:
        print("\n🎲 시뮬레이션 데이터 사용됨")

if __name__ == "__main__":
    asyncio.run(test_simple_real_data())
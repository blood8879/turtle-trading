#!/usr/bin/env python3
"""수정된 백테스트 엔진 테스트"""

import asyncio
import sys
import os
from pathlib import Path

# 프로젝트 루트 경로를 sys.path에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from frontend.backtest.backend.engines.backtest_engine import BacktestEngine, BacktestConfig_

async def test_fixed_backtest():
    """수정된 백테스트 테스트"""
    print("=== 수정된 백테스트 엔진 테스트 ===\n")
    
    # 테스트 설정
    config = BacktestConfig_(
        symbol="BTCUSDT",
        start_date="2024-01-01", 
        end_date="2024-02-29",  # 2개월로 단축
        timeframe="1d",
        initial_balance=10000.0,
        commission_rate=0.0004,
        leverage=1.0,
        systems=[1, 2]
    )
    
    # 백테스트 실행
    engine = BacktestEngine(config)
    results = await engine.run_backtest()
    
    print("📊 전체 성과 요약")
    print("=" * 50)
    print(f"초기 자금: ${results.initial_balance:,.2f}")
    print(f"최종 자금: ${results.final_balance:,.2f}")
    print(f"총 수익률: {results.metrics.total_return:.2%}")
    print(f"연환산 수익률: {results.metrics.annualized_return:.2%}")
    print(f"최대 드로다운: {results.metrics.max_drawdown:.2%}")
    print(f"샤프 비율: {results.metrics.sharpe_ratio:.2f}")
    
    print("\n📊 거래 통계")
    print("=" * 50) 
    print(f"총 거래 수: {results.metrics.total_trades}번")
    print(f"승률: {results.metrics.win_rate:.1%}")
    print(f"평균 수익: ${results.metrics.avg_win:,.2f}")
    print(f"평균 손실: ${results.metrics.avg_loss:,.2f}")
    print(f"수익 팩터: {results.metrics.profit_factor:.2f}")
    print(f"최대 연속 승: {results.metrics.max_consecutive_wins}번")
    print(f"최대 연속 패: {results.metrics.max_consecutive_losses}번")
    
    print("\n📊 롱/숏 포지션")
    print("=" * 50)
    print(f"롱 거래 수: {results.metrics.long_trades}번")
    print(f"숏 거래 수: {results.metrics.short_trades}번")
    print(f"롱 승률: {results.metrics.long_win_rate:.1%}")
    print(f"숏 승률: {results.metrics.short_win_rate:.1%}")
    
    # 거래 상세 내역
    print("\n📋 거래 내역")
    print("=" * 70)
    print("날짜       | 방향 | 진입가  | 청산가  | 수량    | P&L     | 사유")
    print("-" * 70)
    
    total_pnl = 0
    for trade in results.trades:
        entry_date = trade.entry_date.strftime('%m-%d') if hasattr(trade.entry_date, 'strftime') else str(trade.entry_date)[:5]
        total_pnl += trade.pnl
        print(f"{entry_date} | {trade.direction:4} | {trade.entry_price:7.2f} | {trade.exit_price:7.2f} | "
              f"{trade.size:7.4f} | {trade.pnl:7.2f} | {trade.exit_reason}")
    
    print("-" * 70)
    print(f"{'':40} 총 P&L: {total_pnl:7.2f}")
    
    # 수동 P&L 검증
    print(f"\n🔍 P&L 검증:")
    print(f"거래 P&L 합계: ${total_pnl:,.2f}")
    print(f"잔고 변화: ${results.final_balance - results.initial_balance:,.2f}")
    print(f"차이: ${(results.final_balance - results.initial_balance) - total_pnl:,.2f}")
    
    # 숏 거래 체크
    short_trades = [t for t in results.trades if t.direction == "SHORT"]
    print(f"\n✅ 숏 거래 확인: {len(short_trades)}개 (전체 {len(results.trades)}개 중)")

if __name__ == "__main__":
    asyncio.run(test_fixed_backtest())
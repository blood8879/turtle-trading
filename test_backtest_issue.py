#!/usr/bin/env python3
"""
백테스트 이슈 분석용 스크립트
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))

from frontend.backtest.backend.engines.backtest_engine import BacktestEngine, BacktestConfig_

async def test_backtest():
    config = BacktestConfig_(
        symbol='BTCUSDT',
        start_date='2024-01-01',
        end_date='2024-12-31',
        timeframe='1d',
        initial_balance=10000.0,
        commission_rate=0.0004,
        systems=[1, 2]
    )
    
    engine = BacktestEngine(config)
    results = await engine.run_backtest()
    
    print('=== 백테스트 결과 ===')
    print(f'초기 자금: ${results.initial_balance:,.2f}')
    print(f'최종 자금: ${results.final_balance:,.2f}')
    print(f'총 수익: ${results.final_balance - results.initial_balance:,.2f}')
    print(f'총 수익률: {results.metrics.total_return:.2%}')
    print(f'총 거래 수: {results.metrics.total_trades}')
    print(f'승률: {results.metrics.win_rate:.1%}')
    print(f'평균 수익: ${results.metrics.avg_win:,.2f}')
    print(f'평균 손실: ${results.metrics.avg_loss:,.2f}')
    print(f'최대 수익: ${results.metrics.largest_win:,.2f}')
    print(f'최대 손실: ${results.metrics.largest_loss:,.2f}')
    print(f'수익 팩터: {results.metrics.profit_factor:.2f}')
    print(f'롱 거래: {results.metrics.long_trades}')
    print(f'숏 거래: {results.metrics.short_trades}')
    
    print('\n=== 거래 내역 (처음 10개) ===')
    for i, trade in enumerate(results.trades[:10]):
        print(f'{i+1}. {trade.symbol} {trade.direction} - 진입: ${trade.entry_price:,.2f}, 청산: ${trade.exit_price:,.2f}, P&L: ${trade.pnl:,.2f} ({trade.exit_reason})')
    
    if results.trades:
        print('\n=== 손익 분석 ===')
        winning_trades = [t for t in results.trades if t.pnl > 0]
        losing_trades = [t for t in results.trades if t.pnl <= 0]
        
        total_wins = sum(t.pnl for t in winning_trades)
        total_losses = sum(t.pnl for t in losing_trades)
        
        print(f'승리 거래 수: {len(winning_trades)}')
        print(f'패배 거래 수: {len(losing_trades)}')
        print(f'총 수익: ${total_wins:,.2f}')
        print(f'총 손실: ${total_losses:,.2f}')
        print(f'순손익: ${total_wins + total_losses:,.2f}')
        
        print('\n=== 개별 거래 분석 ===')
        for i, trade in enumerate(results.trades):
            direction_mult = 1 if trade.direction == "LONG" else -1
            price_diff = (trade.exit_price - trade.entry_price) * direction_mult
            manual_pnl = price_diff * trade.size
            
            print(f'거래 {i+1}: {trade.direction}')
            print(f'  진입가: ${trade.entry_price:,.2f}')
            print(f'  청산가: ${trade.exit_price:,.2f}')
            print(f'  사이즈: {trade.size:.4f}')
            print(f'  가격차이: ${price_diff:,.2f}')
            print(f'  수동 계산 P&L: ${manual_pnl:,.2f}')
            print(f'  실제 P&L: ${trade.pnl:,.2f}')
            print(f'  차이: ${manual_pnl - trade.pnl:,.2f}')
            print()
    
    return results

if __name__ == "__main__":
    # 실행
    results = asyncio.run(test_backtest())
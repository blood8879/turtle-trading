#!/usr/bin/env python3
"""개선된 백테스트 테스트 - 다양한 시간프레임"""

import asyncio
import sys
import os
from pathlib import Path
from datetime import datetime, timedelta

# 프로젝트 루트 경로를 sys.path에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from frontend.backtest.backend.engines.backtest_engine import BacktestEngine, BacktestConfig_

async def test_multiple_timeframes():
    """다양한 시간프레임에서 백테스트 테스트"""
    print("=== 개선된 터틀 트레이딩 백테스트 ===\n")
    
    # 테스트할 시간프레임들
    timeframes = ['15m', '1h', '4h', '1d']
    
    # 시간프레임별 적절한 기간 설정
    test_configs = {
        '15m': {
            'days': 7,
            'description': '15분봉 7일'
        },
        '1h': {
            'days': 30, 
            'description': '1시간봉 30일'
        },
        '4h': {
            'days': 60,
            'description': '4시간봉 60일'
        },
        '1d': {
            'days': 180,
            'description': '일봉 180일'
        }
    }
    
    results = []
    
    for timeframe in timeframes:
        config_info = test_configs[timeframe]
        
        # 백테스트 기간 설정
        end_date = datetime.now()
        start_date = end_date - timedelta(days=config_info['days'])
        
        config = BacktestConfig_(
            symbol="BTCUSDT",
            start_date=start_date.strftime('%Y-%m-%d'),
            end_date=end_date.strftime('%Y-%m-%d'),
            timeframe=timeframe,
            initial_balance=10000.0,
            commission_rate=0.0004,
            leverage=1.0,
            systems=[1, 2]
        )
        
        print(f"🧪 {config_info['description']} 백테스트 실행중...")
        print(f"   기간: {config.start_date} ~ {config.end_date}")
        
        try:
            engine = BacktestEngine(config)
            result = await engine.run_backtest()
            
            # 결과 출력
            metrics = result.metrics
            print(f"   📊 결과:")
            print(f"      총 수익률: {metrics.total_return:.2%}")
            print(f"      총 거래 수: {metrics.total_trades}번")
            print(f"      롱 거래: {metrics.long_trades}번")
            print(f"      숏 거래: {metrics.short_trades}번")
            print(f"      승률: {metrics.win_rate:.2%}")
            print(f"      최대 드로다운: {metrics.max_drawdown:.2%}")
            print(f"      수익 팩터: {metrics.profit_factor:.2f}")
            print()
            
            results.append({
                'timeframe': timeframe,
                'description': config_info['description'],
                'metrics': metrics
            })
            
        except Exception as e:
            print(f"   ❌ 오류 발생: {str(e)}")
            print()
    
    # 결과 요약
    print("=" * 80)
    print("📋 백테스트 결과 요약")
    print("=" * 80)
    print("시간프레임 | 총 수익률 | 거래 수 | 승률    | 최대DD  | 수익팩터")
    print("-" * 80)
    
    for result in results:
        m = result['metrics']
        print(f"{result['timeframe']:>8} | {m.total_return:>8.2%} | {m.total_trades:>5}개 | "
              f"{m.win_rate:>6.2%} | {m.max_drawdown:>6.2%} | {m.profit_factor:>7.2f}")
    
    print("-" * 80)
    
    # 최고 성과 분석
    if results:
        best_return = max(results, key=lambda x: x['metrics'].total_return)
        most_trades = max(results, key=lambda x: x['metrics'].total_trades)
        
        print(f"\n🏆 최고 수익률: {best_return['timeframe']} ({best_return['metrics'].total_return:.2%})")
        print(f"📈 최다 거래: {most_trades['timeframe']} ({most_trades['metrics'].total_trades}번)")

async def test_single_timeframe_detailed():
    """단일 시간프레임 상세 테스트"""
    print("\n=== 15분봉 상세 분석 ===\n")
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    
    config = BacktestConfig_(
        symbol="BTCUSDT",
        start_date=start_date.strftime('%Y-%m-%d'),
        end_date=end_date.strftime('%Y-%m-%d'),
        timeframe="15m",
        initial_balance=10000.0,
        commission_rate=0.0004,
        leverage=1.0,
        systems=[1, 2]
    )
    
    print(f"📊 상세 분석: 15분봉 7일 백테스트")
    print(f"기간: {config.start_date} ~ {config.end_date}")
    
    engine = BacktestEngine(config)
    result = await engine.run_backtest()
    
    print(f"\n📈 성과 지표:")
    m = result.metrics
    print(f"  총 수익률: {m.total_return:.2%}")
    print(f"  연환산 수익률: {m.annualized_return:.2%}")
    print(f"  최대 드로다운: {m.max_drawdown:.2%}")
    print(f"  샤프 비율: {m.sharpe_ratio:.2f}")
    print(f"  수익 팩터: {m.profit_factor:.2f}")
    
    print(f"\n📊 거래 통계:")
    print(f"  총 거래 수: {m.total_trades}번")
    print(f"  승리 거래: {m.winning_trades}번")
    print(f"  손실 거래: {m.losing_trades}번")
    print(f"  승률: {m.win_rate:.2%}")
    print(f"  평균 승리: ${m.avg_win:.2f}")
    print(f"  평균 손실: ${m.avg_loss:.2f}")
    print(f"  최대 승리: ${m.largest_win:.2f}")
    print(f"  최대 손실: ${m.largest_loss:.2f}")
    
    print(f"\n📋 포지션 분석:")
    print(f"  롱 거래: {m.long_trades}번 (승률: {m.long_win_rate:.2%})")
    print(f"  숏 거래: {m.short_trades}번 (승률: {m.short_win_rate:.2%})")
    
    print(f"\n⏱️ 거래 패턴:")
    print(f"  평균 거래 기간: {m.avg_trade_duration:.1f}일")
    print(f"  최대 연속 승리: {m.max_consecutive_wins}번")
    print(f"  최대 연속 손실: {m.max_consecutive_losses}번")
    
    # 거래 내역 출력 (최근 10개)
    if result.trades:
        print(f"\n📝 최근 거래 내역 (최대 10개):")
        recent_trades = result.trades[-10:] if len(result.trades) > 10 else result.trades
        for i, trade in enumerate(recent_trades, 1):
            pnl_pct = (trade.pnl / 10000) * 100  # 초기 자본 대비 수익률
            print(f"  {i:2d}. {trade.direction} | "
                  f"진입: ${trade.entry_price:.2f} | "
                  f"청산: ${trade.exit_price:.2f} | "
                  f"P&L: ${trade.pnl:.2f} ({pnl_pct:+.2f}%) | "
                  f"사유: {trade.exit_reason}")

if __name__ == "__main__":
    asyncio.run(test_multiple_timeframes())
    asyncio.run(test_single_timeframe_detailed())
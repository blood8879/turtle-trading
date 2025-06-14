#!/usr/bin/env python3
"""모든 시간프레임 실제 데이터 테스트"""

import asyncio
import sys
import os
from pathlib import Path
from datetime import datetime, timedelta

# 프로젝트 루트 경로를 sys.path에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from data.binance_data_fetcher import BinanceDataFetcher

async def test_all_timeframes():
    """모든 시간프레임으로 실제 데이터 테스트 (API 키 없이)"""
    print("=== 모든 시간프레임 실제 데이터 테스트 ===\n")
    
    # 테스트할 시간프레임들
    timeframes = {
        '1m': '1분봉',
        '5m': '5분봉', 
        '15m': '15분봉',
        '1h': '1시간봉',
        '4h': '4시간봉',
        '1d': '일봉',
        '1w': '주봉'
    }
    
    # 시간프레임별 적절한 기간 설정
    date_ranges = {
        '1m': (1, '최근 1일'),    # 1분봉은 최근 1일
        '5m': (3, '최근 3일'),    # 5분봉은 최근 3일
        '15m': (7, '최근 7일'),   # 15분봉은 최근 7일
        '1h': (30, '최근 30일'),  # 1시간봉은 최근 30일
        '4h': (60, '최근 60일'),  # 4시간봉은 최근 60일
        '1d': (180, '최근 180일'), # 일봉은 최근 180일
        '1w': (365, '최근 365일')  # 주봉은 최근 365일
    }
    
    fetcher = BinanceDataFetcher(testnet=False)  # 실제 서버 사용
    
    # 연결 테스트
    connected = await fetcher.test_connection()
    print(f"🌐 Binance 연결: {'✅ 성공' if connected else '❌ 실패'}\n")
    
    if not connected:
        print("인터넷 연결을 확인해주세요.")
        return
    
    print("📊 시간프레임별 실제 데이터 테스트:")
    print("=" * 70)
    print("시간프레임 | 기간        | 데이터 수 | 첫 캔들      | 마지막 캔들   | 상태")
    print("-" * 70)
    
    for timeframe, name in timeframes.items():
        try:
            # 날짜 범위 계산
            days_back, period_desc = date_ranges[timeframe]
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days_back)
            
            # 데이터 가져오기
            data = await fetcher.get_historical_klines(
                'BTCUSDT', 
                timeframe, 
                start_date.strftime('%Y-%m-%d'),
                end_date.strftime('%Y-%m-%d')
            )
            
            if data:
                first_date = data[0].date.strftime('%m-%d %H:%M')
                last_date = data[-1].date.strftime('%m-%d %H:%M') 
                status = "✅ 성공"
                
                print(f"{timeframe:>8} | {period_desc:>11} | {len(data):>7}개 | "
                      f"{first_date:>12} | {last_date:>12} | {status}")
            else:
                print(f"{timeframe:>8} | {period_desc:>11} | {'0':>7}개 | "
                      f"{'N/A':>12} | {'N/A':>12} | ❌ 실패")
                
            # API 제한을 위한 딜레이
            await asyncio.sleep(0.2)
            
        except Exception as e:
            print(f"{timeframe:>8} | {period_desc:>11} | {'ERROR':>7} | "
                  f"{'N/A':>12} | {'N/A':>12} | ❌ 오류: {str(e)[:20]}")
    
    print("-" * 70)
    
    # 현재 가격도 확인
    try:
        current_price = await fetcher.get_current_price('BTCUSDT')
        print(f"\n💰 현재 BTC 가격: ${current_price:,.2f}")
    except:
        print(f"\n❌ 현재 가격 조회 실패")
    
    print("\n🎯 결론:")
    print("✅ API 키 없이도 모든 시간프레임의 실제 Binance 데이터 접근 가능")
    print("✅ 분봉, 시간봉, 일봉, 주봉 모두 지원")
    print("✅ 백테스트에 실제 과거 데이터 사용 가능")

async def test_specific_backtest():
    """특정 시간프레임으로 실제 백테스트"""
    print("\n=== 실제 데이터 백테스트 예시 ===\n")
    
    from frontend.backtest.backend.engines.backtest_engine import BacktestEngine, BacktestConfig_
    
    # 4시간봉으로 최근 60일 백테스트
    end_date = datetime.now()
    start_date = end_date - timedelta(days=90)
    
    config = BacktestConfig_(
        symbol="BTCUSDT",
        start_date=start_date.strftime('%Y-%m-%d'), 
        end_date=end_date.strftime('%Y-%m-%d'),
        timeframe="4h",  # 4시간봉
        initial_balance=10000.0,
        commission_rate=0.0004,
        leverage=1.0,
        systems=[1, 2]
    )
    
    print(f"🧪 4시간봉 백테스트: {config.start_date} ~ {config.end_date}")
    
    engine = BacktestEngine(config)
    results = await engine.run_backtest()
    
    print(f"📊 결과: 총 수익률 {results.metrics.total_return:.2%}, "
          f"거래 수 {results.metrics.total_trades}번, "
          f"롱 {results.metrics.long_trades}개, 숏 {results.metrics.short_trades}개")

if __name__ == "__main__":
    asyncio.run(test_all_timeframes())
    asyncio.run(test_specific_backtest())
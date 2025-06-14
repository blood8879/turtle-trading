"""
테스트 설정 및 픽스처
"""

import pytest
import sys
import os
from pathlib import Path
from datetime import datetime, timedelta

# 프로젝트 루트를 파이썬 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from strategy.turtle_strategy import PriceData, TradingUnit, Position

@pytest.fixture
def sample_price_data():
    """샘플 가격 데이터 픽스처"""
    base_date = datetime(2024, 1, 1)
    data = []
    
    # 30일간의 샘플 데이터 생성
    base_price = 50000
    for i in range(30):
        # 약간의 변동성이 있는 가격 시뮬레이션
        price_change = (i * 50) + ((i % 3 - 1) * 200)  # 전체적 상승 + 일일 변동
        price = base_price + price_change
        
        data.append(PriceData(
            symbol="BTCUSDT",
            date=base_date + timedelta(days=i),
            open=price,
            high=price + 300,
            low=price - 300,
            close=price + 100,
            volume=1000 + (i * 10)
        ))
    
    return data

@pytest.fixture
def sample_trading_unit():
    """샘플 거래 유닛 픽스처"""
    return TradingUnit(
        entry_price=50000,
        entry_date=datetime(2024, 1, 15),
        size=0.1,
        stop_loss=48000,
        system=1,
        unit_number=1
    )

@pytest.fixture
def sample_position(sample_trading_unit):
    """샘플 포지션 픽스처"""
    return Position(
        symbol="BTCUSDT",
        direction="LONG",
        units=[sample_trading_unit],
        total_size=0.1,
        avg_price=50000
    )

@pytest.fixture
def test_account_balance():
    """테스트용 계좌 잔고"""
    return 10000.0

@pytest.fixture
def test_atr_value():
    """테스트용 ATR 값"""
    return 1000.0

@pytest.fixture
def setup_test_directories():
    """테스트 디렉토리 설정"""
    directories = [
        "data/backtest_results",
        "data/historical", 
        "data/live_trading",
        "logs"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
    
    yield directories
    
    # 테스트 후 정리는 하지 않음 (실제 데이터 보존)

@pytest.fixture
def mock_binance_data():
    """모의 Binance 데이터"""
    return {
        "symbol": "BTCUSDT",
        "price": "50000.00",
        "time": 1672531200000,  # 2023-01-01 00:00:00 UTC
        "klines": [
            [
                1672531200000,  # Open time
                "50000.00",     # Open
                "50500.00",     # High
                "49500.00",     # Low
                "50200.00",     # Close
                "100.50",       # Volume
                1672534800000,  # Close time
                "5025000.00",   # Quote asset volume
                1000,           # Number of trades
                "50.25",        # Taker buy base asset volume
                "2512500.00",   # Taker buy quote asset volume
                "0"             # Ignore
            ]
        ]
    }

@pytest.fixture(scope="session")
def event_loop():
    """이벤트 루프 픽스처 (비동기 테스트용)"""
    import asyncio
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

# 테스트 전용 설정
@pytest.fixture(autouse=True)
def setup_test_config():
    """테스트용 설정 (모든 테스트에 자동 적용)"""
    # 테스트 환경 변수 설정
    os.environ["TESTING"] = "true"
    os.environ["LOG_LEVEL"] = "WARNING"  # 테스트 중 로그 줄이기
    
    yield
    
    # 테스트 후 정리
    if "TESTING" in os.environ:
        del os.environ["TESTING"]

# 마커 정의
def pytest_configure(config):
    """pytest 설정"""
    config.addinivalue_line(
        "markers", "slow: 느린 테스트 마커 (전체 백테스트 등)"
    )
    config.addinivalue_line(
        "markers", "integration: 통합 테스트 마커"
    )
    config.addinivalue_line(
        "markers", "unit: 단위 테스트 마커"
    )

# 테스트 결과 요약 출력
def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """테스트 결과 요약"""
    if exitstatus == 0:
        terminalreporter.write_line("🎉 모든 테스트가 성공했습니다!", green=True)
    else:
        terminalreporter.write_line("❌ 일부 테스트가 실패했습니다.", red=True)
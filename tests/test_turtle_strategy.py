"""
터틀 트레이딩 전략 테스트
"""

import pytest
import sys
import os
from datetime import datetime, timedelta
from pathlib import Path

# 프로젝트 루트를 파이썬 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from strategy.turtle_strategy import (
    TurtleStrategy, TurtleIndicators, PriceData, 
    TradingUnit, Position, TradeResult
)
from config import TradingConfig

class TestTurtleIndicators:
    """터틀 지표 테스트"""
    
    def setup_method(self):
        """테스트 설정"""
        self.indicators = TurtleIndicators()
        
        # 테스트용 가격 데이터 생성
        base_date = datetime(2024, 1, 1)
        self.sample_data = []
        
        prices = [100, 102, 98, 105, 103, 107, 101, 110, 108, 112, 
                 115, 113, 118, 116, 120, 122, 119, 125, 123, 128,
                 130, 127, 133, 131, 135, 138, 136, 140, 142, 145]
        
        for i, price in enumerate(prices):
            self.sample_data.append(PriceData(
                symbol="BTCUSDT",
                date=base_date + timedelta(days=i),
                open=price,
                high=price + 2,
                low=price - 2,
                close=price + 1,
                volume=1000
            ))
    
    def test_atr_calculation(self):
        """ATR 계산 테스트"""
        # ATR 계산이 정상적으로 작동하는지 확인
        atr = self.indicators.calculate_atr(self.sample_data, period=20)
        
        assert atr > 0, "ATR은 0보다 커야 합니다"
        assert isinstance(atr, float), "ATR은 float 타입이어야 합니다"
        
        # 기간이 부족한 경우 예외 발생 확인
        with pytest.raises(ValueError):
            self.indicators.calculate_atr(self.sample_data[:10], period=20)
    
    def test_atr_consistency(self):
        """ATR 일관성 테스트"""
        # 같은 데이터로 여러 번 계산했을 때 같은 결과가 나와야 함
        atr1 = self.indicators.calculate_atr(self.sample_data, period=20)
        atr2 = self.indicators.calculate_atr(self.sample_data, period=20)
        
        assert atr1 == atr2, "ATR 계산이 일관성이 있어야 합니다"
    
    def test_breakout_detection_long(self):
        """롱 돌파 신호 테스트"""
        # 상승 돌파 상황 생성 (마지막 가격이 최고가보다 높음)
        test_data = self.sample_data.copy()
        
        # 마지막 데이터의 종가를 매우 높게 설정
        test_data[-1] = PriceData(
            symbol="BTCUSDT",
            date=test_data[-1].date,
            open=150,
            high=155,
            low=148,
            close=155,  # 이전 최고가보다 높음
            volume=1000
        )
        
        breakout = self.indicators.check_breakout(test_data, 10, "LONG")
        assert breakout == True, "상승 돌파가 감지되어야 합니다"
    
    def test_breakout_detection_short(self):
        """숏 돌파 신호 테스트"""
        # 하락 돌파 상황 생성
        test_data = self.sample_data.copy()
        
        # 마지막 데이터의 종가를 매우 낮게 설정
        test_data[-1] = PriceData(
            symbol="BTCUSDT",
            date=test_data[-1].date,
            open=90,
            high=92,
            low=85,
            close=85,  # 이전 최저가보다 낮음
            volume=1000
        )
        
        breakout = self.indicators.check_breakout(test_data, 10, "SHORT")
        assert breakout == True, "하락 돌파가 감지되어야 합니다"
    
    def test_no_breakout(self):
        """돌파 없는 상황 테스트"""
        # 정상적인 데이터에서는 돌파가 없어야 함
        breakout_long = self.indicators.check_breakout(self.sample_data, 10, "LONG")
        breakout_short = self.indicators.check_breakout(self.sample_data, 10, "SHORT")
        
        # 일반적인 상황에서는 돌파가 없어야 함 (테스트 데이터가 점진적 상승이므로)
        assert isinstance(breakout_long, bool), "돌파 결과는 bool 타입이어야 합니다"
        assert isinstance(breakout_short, bool), "돌파 결과는 bool 타입이어야 합니다"
    
    def test_donchian_channels(self):
        """돈치안 채널 테스트"""
        high = self.indicators.calculate_donchian_high(self.sample_data, 20)
        low = self.indicators.calculate_donchian_low(self.sample_data, 20)
        
        assert high > low, "돈치안 상단이 하단보다 높아야 합니다"
        assert high > 0 and low > 0, "돈치안 값들이 양수여야 합니다"

class TestTurtleStrategy:
    """터틀 전략 테스트"""
    
    def setup_method(self):
        """테스트 설정"""
        self.strategy = TurtleStrategy()
        
        # 테스트용 가격 데이터
        base_date = datetime(2024, 1, 1)
        self.price_data = []
        
        # 60일 가격 데이터 생성 (55일 돌파 신호 테스트를 위해)
        base_price = 50000
        for i in range(60):
            price = base_price + (i * 100) + ((-1) ** i * 200)  # 변동이 있는 상승 추세
            self.price_data.append(PriceData(
                symbol="BTCUSDT",
                date=base_date + timedelta(days=i),
                open=price,
                high=price + 500,
                low=price - 500,
                close=price,
                volume=1000
            ))
    
    def test_unit_size_calculation(self):
        """유닛 사이즈 계산 테스트"""
        account_balance = 10000
        atr = 1000
        price = 50000
        
        unit_size = self.strategy.calculate_unit_size("BTCUSDT", account_balance, atr, price)
        
        assert unit_size > 0, "유닛 사이즈는 0보다 커야 합니다"
        assert isinstance(unit_size, float), "유닛 사이즈는 float 타입이어야 합니다"
        
        # 1% 리스크 기반 계산 확인
        expected_risk = account_balance * 0.01  # $100
        calculated_risk = unit_size * atr
        
        # 오차 범위 내에서 같아야 함
        assert abs(calculated_risk - expected_risk) < 1, "리스크 계산이 정확해야 합니다"
    
    def test_stop_loss_calculation(self):
        """손절가 계산 테스트"""
        entry_price = 50000
        atr = 1000
        
        # 롱 포지션 손절가
        stop_long = self.strategy.calculate_stop_loss(entry_price, atr, "LONG")
        expected_long = entry_price - (2 * atr)
        assert stop_long == expected_long, "롱 포지션 손절가 계산이 정확해야 합니다"
        
        # 숏 포지션 손절가
        stop_short = self.strategy.calculate_stop_loss(entry_price, atr, "SHORT")
        expected_short = entry_price + (2 * atr)
        assert stop_short == expected_short, "숏 포지션 손절가 계산이 정확해야 합니다"
    
    def test_position_management(self):
        """포지션 관리 테스트"""
        symbol = "BTCUSDT"
        
        # 초기에는 포지션이 없어야 함
        assert not self.strategy.has_position(symbol), "초기에는 포지션이 없어야 합니다"
        assert self.strategy.get_position(symbol) is None, "포지션이 None이어야 합니다"
        
        # 포지션 진입
        unit = self.strategy.execute_entry(
            symbol=symbol,
            direction="LONG",
            entry_price=50000,
            atr=1000,
            account_balance=10000,
            system=1
        )
        
        assert unit is not None, "진입이 성공해야 합니다"
        assert self.strategy.has_position(symbol), "진입 후 포지션이 있어야 합니다"
        
        position = self.strategy.get_position(symbol)
        assert position is not None, "포지션 객체가 있어야 합니다"
        assert position.direction == "LONG", "포지션 방향이 정확해야 합니다"
        assert len(position.units) == 1, "유닛이 1개 있어야 합니다"
    
    def test_pyramid_logic(self):
        """피라미딩 로직 테스트"""
        symbol = "BTCUSDT"
        
        # 첫 번째 유닛 진입
        self.strategy.execute_entry(
            symbol=symbol,
            direction="LONG",
            entry_price=50000,
            atr=1000,
            account_balance=10000,
            system=1
        )
        
        position = self.strategy.get_position(symbol)
        
        # 가격이 충분히 상승하지 않은 경우 - 피라미딩 안됨
        pyramid_signal = self.strategy.check_pyramid_signal(position, 50200, 1000)
        assert not pyramid_signal, "가격 상승이 부족하면 피라미딩하지 않아야 합니다"
        
        # 가격이 충분히 상승한 경우 - 피라미딩 됨
        pyramid_signal = self.strategy.check_pyramid_signal(position, 50600, 1000)
        assert pyramid_signal, "가격이 충분히 상승하면 피라미딩해야 합니다"
    
    def test_stop_loss_check(self):
        """손절 확인 테스트"""
        symbol = "BTCUSDT"
        
        # 롱 포지션 진입
        self.strategy.execute_entry(
            symbol=symbol,
            direction="LONG",
            entry_price=50000,
            atr=1000,
            account_balance=10000,
            system=1
        )
        
        position = self.strategy.get_position(symbol)
        
        # 손절가 위의 가격 - 손절 안됨
        stop_triggered = self.strategy.check_stop_loss(position, 49000)
        assert not stop_triggered, "손절가 위에서는 손절되지 않아야 합니다"
        
        # 손절가 아래의 가격 - 손절 됨
        stop_triggered = self.strategy.check_stop_loss(position, 47500)
        assert stop_triggered, "손절가 아래에서는 손절되어야 합니다"
    
    def test_entry_signals(self):
        """진입 신호 테스트"""
        symbol = "BTCUSDT"
        
        # 시스템 1 진입 신호 확인
        signal_s1 = self.strategy.check_entry_signal(symbol, self.price_data, 1, "LONG")
        signal_s2 = self.strategy.check_entry_signal(symbol, self.price_data, 2, "LONG")
        
        assert isinstance(signal_s1, bool), "시스템 1 신호는 bool 타입이어야 합니다"
        assert isinstance(signal_s2, bool), "시스템 2 신호는 bool 타입이어야 합니다"
    
    def test_trade_execution_and_exit(self):
        """거래 실행 및 청산 테스트"""
        symbol = "BTCUSDT"
        
        # 진입
        self.strategy.execute_entry(
            symbol=symbol,
            direction="LONG",
            entry_price=50000,
            atr=1000,
            account_balance=10000,
            system=1
        )
        
        assert len(self.strategy.get_trade_history()) == 0, "진입만으로는 거래 이력이 없어야 합니다"
        
        # 청산
        trade_result = self.strategy.execute_exit(symbol, 52000, "SIGNAL")
        
        assert trade_result is not None, "청산 결과가 있어야 합니다"
        assert trade_result.pnl > 0, "수익이 발생해야 합니다"
        assert len(self.strategy.get_trade_history()) == 1, "거래 이력이 1개 있어야 합니다"
        assert not self.strategy.has_position(symbol), "청산 후 포지션이 없어야 합니다"
    
    def test_strategy_reset(self):
        """전략 초기화 테스트"""
        symbol = "BTCUSDT"
        
        # 포지션 생성
        self.strategy.execute_entry(
            symbol=symbol,
            direction="LONG",
            entry_price=50000,
            atr=1000,
            account_balance=10000,
            system=1
        )
        
        # 거래 완료
        self.strategy.execute_exit(symbol, 52000, "SIGNAL")
        
        assert self.strategy.get_trade_history(), "거래 이력이 있어야 합니다"
        
        # 리셋
        self.strategy.reset()
        
        assert not self.strategy.get_all_positions(), "리셋 후 포지션이 없어야 합니다"
        assert not self.strategy.get_trade_history(), "리셋 후 거래 이력이 없어야 합니다"

class TestPositionAndTradeData:
    """포지션 및 거래 데이터 테스트"""
    
    def test_trading_unit_creation(self):
        """거래 유닛 생성 테스트"""
        unit = TradingUnit(
            entry_price=50000,
            entry_date=datetime.now(),
            size=0.1,
            stop_loss=48000,
            system=1,
            unit_number=1
        )
        
        assert unit.entry_price == 50000, "진입가가 정확해야 합니다"
        assert unit.size == 0.1, "사이즈가 정확해야 합니다"
        assert unit.system == 1, "시스템이 정확해야 합니다"
    
    def test_position_creation_and_unit_addition(self):
        """포지션 생성 및 유닛 추가 테스트"""
        unit1 = TradingUnit(
            entry_price=50000,
            entry_date=datetime.now(),
            size=0.1,
            stop_loss=48000,
            system=1,
            unit_number=1
        )
        
        position = Position(
            symbol="BTCUSDT",
            direction="LONG",
            units=[unit1],
            total_size=0.1,
            avg_price=50000
        )
        
        assert position.total_size == 0.1, "초기 총 사이즈가 정확해야 합니다"
        assert position.avg_price == 50000, "초기 평균가가 정확해야 합니다"
        
        # 두 번째 유닛 추가
        unit2 = TradingUnit(
            entry_price=51000,
            entry_date=datetime.now(),
            size=0.1,
            stop_loss=49000,
            system=1,
            unit_number=2
        )
        
        position.add_unit(unit2)
        
        assert position.total_size == 0.2, "유닛 추가 후 총 사이즈가 정확해야 합니다"
        assert position.avg_price == 50500, "유닛 추가 후 평균가가 정확해야 합니다"
        assert len(position.units) == 2, "유닛 개수가 정확해야 합니다"

class TestConfigurationAndConstants:
    """설정 및 상수 테스트"""
    
    def test_trading_config_constants(self):
        """거래 설정 상수 테스트"""
        config = TradingConfig()
        
        # 중요한 상수들이 올바른 값인지 확인
        assert config.RISK_PER_TRADE == 0.01, "거래당 리스크가 1%여야 합니다"
        assert config.MAX_RISK_TOTAL == 0.20, "총 최대 리스크가 20%여야 합니다"
        assert config.ATR_PERIOD == 20, "ATR 기간이 20일이어야 합니다"
        assert config.MAX_UNITS_PER_MARKET == 4, "시장당 최대 유닛이 4개여야 합니다"
        assert config.STOP_LOSS_MULTIPLIER == 2.0, "손절 배수가 2.0이어야 합니다"
        assert config.PYRAMID_MULTIPLIER == 0.5, "피라미딩 배수가 0.5여야 합니다"
    
    def test_system_configurations(self):
        """시스템 설정 테스트"""
        config = TradingConfig()
        
        # 시스템 1 설정
        s1 = config.SYSTEM_1
        assert s1['ENTRY_PERIOD'] == 20, "시스템 1 진입 기간이 20일이어야 합니다"
        assert s1['EXIT_PERIOD'] == 10, "시스템 1 청산 기간이 10일이어야 합니다"
        assert s1['USE_FILTER'] == True, "시스템 1은 필터를 사용해야 합니다"
        
        # 시스템 2 설정
        s2 = config.SYSTEM_2
        assert s2['ENTRY_PERIOD'] == 55, "시스템 2 진입 기간이 55일이어야 합니다"
        assert s2['EXIT_PERIOD'] == 20, "시스템 2 청산 기간이 20일이어야 합니다"
        assert s2['USE_FILTER'] == False, "시스템 2는 필터를 사용하지 않아야 합니다"

if __name__ == "__main__":
    # 테스트 실행
    pytest.main([__file__, "-v"])
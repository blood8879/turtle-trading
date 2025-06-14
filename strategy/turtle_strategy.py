"""
Turtle Trading Strategy Implementation
터틀 트레이딩 전략의 핵심 로직 구현
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging
import sys
import os

# utils 디렉토리를 sys.path에 추가
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from config import TradingConfig, TradingMode
from utils.trade_journal import TradeJournalManager

logger = logging.getLogger(__name__)

@dataclass
class PriceData:
    """OHLCV 가격 데이터"""
    symbol: str
    date: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float

@dataclass
class TradingUnit:
    """터틀 거래 유닛"""
    entry_price: float
    entry_date: datetime
    size: float
    stop_loss: float
    system: int  # 1 or 2
    unit_number: int  # 1-4

@dataclass
class Position:
    """포지션 정보"""
    symbol: str
    direction: str  # 'LONG' or 'SHORT'
    units: List[TradingUnit]
    total_size: float
    avg_price: float
    
    def add_unit(self, unit: TradingUnit):
        """유닛 추가"""
        self.units.append(unit)
        self.total_size += unit.size
        # 평균 단가 재계산
        total_value = sum(u.size * u.entry_price for u in self.units)
        self.avg_price = total_value / self.total_size

@dataclass
class TradeResult:
    """거래 결과"""
    symbol: str
    direction: str
    entry_price: float
    exit_price: float
    size: float
    pnl: float
    entry_date: datetime
    exit_date: datetime
    system: int
    exit_reason: str  # 'SIGNAL', 'STOP_LOSS'

class TurtleIndicators:
    """터틀 트레이딩 지표 계산"""
    
    @staticmethod
    def calculate_atr(price_data: List[PriceData], period: int = 20) -> float:
        """ATR (Average True Range) 계산"""
        if len(price_data) < period + 1:
            raise ValueError(f"ATR 계산을 위해서는 최소 {period + 1}개의 데이터가 필요합니다.")
        
        true_ranges = []
        
        for i in range(1, len(price_data)):
            current = price_data[i]
            previous = price_data[i-1]
            
            tr1 = current.high - current.low
            tr2 = abs(current.high - previous.close)
            tr3 = abs(current.low - previous.close)
            
            true_range = max(tr1, tr2, tr3)
            true_ranges.append(true_range)
        
        # 최근 period 기간의 평균
        recent_trs = true_ranges[-period:]
        return sum(recent_trs) / len(recent_trs)
    
    
    @staticmethod
    def check_breakout(price_data: List[PriceData], period: int, direction: str) -> bool:
        """돌파 신호 확인"""
        if len(price_data) < period + 1:
            return False
        
        current_price = price_data[-1].close
        
        if direction == "LONG":
            # 최근 period 기간의 최고가 (현재 제외)
            highest_high = max(p.high for p in price_data[-period-1:-1])
            return current_price > highest_high
        
        elif direction == "SHORT":
            # 최근 period 기간의 최저가 (현재 제외)
            lowest_low = min(p.low for p in price_data[-period-1:-1])
            return current_price < lowest_low
        
        return False
    
    @staticmethod
    def calculate_donchian_high(price_data: List[PriceData], period: int) -> float:
        """돈치안 채널 상단 (최고가)"""
        if len(price_data) < period:
            return price_data[-1].high
        return max(p.high for p in price_data[-period:])
    
    @staticmethod
    def calculate_donchian_low(price_data: List[PriceData], period: int) -> float:
        """돈치안 채널 하단 (최저가)"""
        if len(price_data) < period:
            return price_data[-1].low
        return min(p.low for p in price_data[-period:])

class TurtleStrategy:
    """터틀 트레이딩 전략 메인 클래스"""
    
    def __init__(self, trading_mode: str = TradingMode.BACKTEST):
        self.config = TradingConfig()
        self.indicators = TurtleIndicators()
        self.positions: Dict[str, Position] = {}
        self.trade_history: List[TradeResult] = []
        self.last_trade_results: Dict[str, bool] = {}  # 마지막 거래 결과 (승/패)
        
        # 매매일지 관리자 초기화
        self.trading_mode = trading_mode
        self.journal = TradeJournalManager(trading_mode)
        self.active_trade_ids: Dict[str, str] = {}  # symbol -> trade_id 매핑
        
    def calculate_unit_size(self, symbol: str, account_balance: float, 
                          atr: float, price: float, leverage: float = 1.0) -> float:
        """유닛 사이즈 계산 (레버리지 적용)"""
        # 1% 리스크 기반 포지션 사이징
        dollar_volatility = atr * 1.0  # 계약 크기 = 1 (현물/선물 기준)
        risk_amount = account_balance * self.config.RISK_PER_TRADE
        
        # 레버리지 적용: 레버리지가 높을수록 같은 리스크로 더 큰 포지션 가능
        base_unit_size = risk_amount / dollar_volatility
        leveraged_unit_size = base_unit_size * leverage
        
        return max(0.001, leveraged_unit_size)  # 최소 거래 단위
    
    def calculate_atr_for_timeframe(self, price_data: List[PriceData], timeframe: str = "1d") -> float:
        """시간프레임에 맞는 ATR 계산"""
        atr_period = self.config.get_atr_period(timeframe)
        
        # 사용 가능한 데이터에 따라 ATR 기간 조정
        available_period = min(atr_period, len(price_data) - 1)
        if available_period < 2:
            raise ValueError(f"ATR 계산을 위해서는 최소 2개의 데이터가 필요합니다. (현재: {len(price_data)})")
        
        return self.indicators.calculate_atr(price_data[-available_period-1:], available_period)
    
    def check_entry_signal(self, symbol: str, price_data: List[PriceData], 
                         system: int, direction: str = "LONG", timeframe: str = "1d") -> bool:
        """진입 신호 확인 (시간프레임 적응)"""
        # 공통 설정에서 시간프레임별 브레이크아웃 기간 가져오기
        multiplier = self.config.get_timeframe_multiplier(timeframe)
        
        if system == 1:
            # 시스템 1: 20일 돌파 + 필터 (시간프레임 조정)
            entry_period = self.config.SYSTEM_1['ENTRY_PERIOD'] * multiplier
            # 최소 2기간, 최대 100기간으로 제한
            entry_period = max(2, min(100, entry_period))
            
            breakout = self.indicators.check_breakout(price_data, entry_period, direction)
            
            if self.config.SYSTEM_1['USE_FILTER']:
                # 마지막 거래가 손실이었다면 진입 안함
                last_loss = self.last_trade_results.get(symbol, False)
                return breakout and not last_loss
            else:
                return breakout
                
        elif system == 2:
            # 시스템 2: 55일 돌파 (필터 없음, 시간프레임 조정)
            entry_period = self.config.SYSTEM_2['ENTRY_PERIOD'] * multiplier
            # 최소 2기간, 최대 200기간으로 제한
            entry_period = max(2, min(200, entry_period))
            
            return self.indicators.check_breakout(price_data, entry_period, direction)
        
        return False
    
    def check_exit_signal(self, position: Position, price_data: List[PriceData], timeframe: str = "1d") -> bool:
        """청산 신호 확인 (시간프레임 적응)"""
        if not position.units:
            return False
        
        # 공통 설정에서 시간프레임별 브레이크아웃 기간 가져오기
        multiplier = self.config.get_timeframe_multiplier(timeframe)
        system = position.units[0].system
        
        if system == 1:
            exit_period = self.config.SYSTEM_1['EXIT_PERIOD'] * multiplier
        else:
            exit_period = self.config.SYSTEM_2['EXIT_PERIOD'] * multiplier
        
        # 최소 2기간, 최대 100기간으로 제한
        exit_period = max(2, min(100, exit_period))
        
        # 반대 방향 돌파로 청산
        if position.direction == "LONG":
            return self.indicators.check_breakout(price_data, exit_period, "SHORT")
        else:
            return self.indicators.check_breakout(price_data, exit_period, "LONG")
    
    def check_stop_loss(self, position: Position, current_price: float) -> bool:
        """손절 확인"""
        for unit in position.units:
            if position.direction == "LONG":
                if current_price <= unit.stop_loss:
                    return True
            else:  # SHORT
                if current_price >= unit.stop_loss:
                    return True
        return False
    
    def check_pyramid_signal(self, position: Position, current_price: float, 
                           atr: float) -> bool:
        """피라미딩 신호 확인"""
        if len(position.units) >= self.config.MAX_UNITS_PER_MARKET:
            return False
        
        first_entry = position.units[0]
        current_units = len(position.units)
        
        if position.direction == "LONG":
            price_move = current_price - first_entry.entry_price
            required_move = self.config.PYRAMID_MULTIPLIER * atr * current_units
            return price_move >= required_move
        else:  # SHORT
            price_move = first_entry.entry_price - current_price
            required_move = self.config.PYRAMID_MULTIPLIER * atr * current_units
            return price_move >= required_move
    
    def calculate_stop_loss(self, entry_price: float, atr: float, direction: str) -> float:
        """손절가 계산"""
        if direction == "LONG":
            return entry_price - (self.config.STOP_LOSS_MULTIPLIER * atr)
        else:  # SHORT
            return entry_price + (self.config.STOP_LOSS_MULTIPLIER * atr)
    
    def update_stop_losses(self, position: Position, new_stop: float):
        """모든 유닛의 손절가 업데이트 (트레일링)"""
        for unit in position.units:
            if position.direction == "LONG":
                # 롱 포지션: 손절가는 올릴 수만 있음
                unit.stop_loss = max(unit.stop_loss, new_stop)
            else:  # SHORT
                # 숏 포지션: 손절가는 내릴 수만 있음
                unit.stop_loss = min(unit.stop_loss, new_stop)
    
    def execute_entry(self, symbol: str, direction: str, entry_price: float,
                     atr: float, account_balance: float, system: int, leverage: float = 1.0) -> Optional[TradingUnit]:
        """진입 실행 (레버리지 적용)"""
        # 유닛 사이즈 계산
        unit_size = self.calculate_unit_size(symbol, account_balance, atr, entry_price, leverage)
        
        # 손절가 계산
        stop_loss = self.calculate_stop_loss(entry_price, atr, direction)
        
        # 새 유닛 생성
        new_unit = TradingUnit(
            entry_price=entry_price,
            entry_date=datetime.now(),
            size=unit_size,
            stop_loss=stop_loss,
            system=system,
            unit_number=1 if symbol not in self.positions else len(self.positions[symbol].units) + 1
        )
        
        # 포지션 업데이트
        if symbol not in self.positions:
            self.positions[symbol] = Position(
                symbol=symbol,
                direction=direction,
                units=[new_unit],
                total_size=unit_size,
                avg_price=entry_price
            )
            
            # 새 포지션인 경우 매매일지에 진입 기록
            trade_id = self.journal.log_trade_entry(
                symbol=symbol,
                direction=direction,
                entry_price=entry_price,
                size=unit_size,
                stop_loss=stop_loss,
                atr=atr,
                leverage=leverage,
                account_balance=account_balance,
                system=system,
                unit_number=new_unit.unit_number,
                notes=f"시스템 {system} 신규 진입"
            )
            self.active_trade_ids[symbol] = trade_id
        else:
            self.positions[symbol].add_unit(new_unit)
            
            # 피라미딩인 경우 매매일지에 피라미딩 기록
            if symbol in self.active_trade_ids:
                self.journal.log_pyramid_entry(
                    trade_id=self.active_trade_ids[symbol],
                    symbol=symbol,
                    direction=direction,
                    entry_price=entry_price,
                    size=unit_size,
                    stop_loss=stop_loss,
                    atr=atr,
                    leverage=leverage,
                    account_balance=account_balance,
                    system=system,
                    unit_number=new_unit.unit_number,
                    notes=f"유닛 {new_unit.unit_number} 피라미딩"
                )
        
        logger.info(f"진입 실행: {symbol} {direction} {unit_size:.4f} @ {entry_price:.2f} (레버리지: {leverage}x)")
        return new_unit
    
    def execute_exit(self, symbol: str, exit_price: float, reason: str, 
                    account_balance: float = 0.0, leverage: float = 1.0) -> Optional[TradeResult]:
        """청산 실행"""
        if symbol not in self.positions:
            return None
        
        position = self.positions[symbol]
        
        # P&L 계산
        if position.direction == "LONG":
            pnl = (exit_price - position.avg_price) * position.total_size
        else:  # SHORT
            pnl = (position.avg_price - exit_price) * position.total_size
        
        # 거래 결과 기록
        trade_result = TradeResult(
            symbol=symbol,
            direction=position.direction,
            entry_price=position.avg_price,
            exit_price=exit_price,
            size=position.total_size,
            pnl=pnl,
            entry_date=position.units[0].entry_date,
            exit_date=datetime.now(),
            system=position.units[0].system,
            exit_reason=reason
        )
        
        self.trade_history.append(trade_result)
        
        # 매매일지에 청산 기록
        if symbol in self.active_trade_ids:
            self.journal.log_trade_exit(
                trade_id=self.active_trade_ids[symbol],
                symbol=symbol,
                direction=position.direction,
                entry_price=position.avg_price,
                exit_price=exit_price,
                size=position.total_size,
                pnl=pnl,
                account_balance=account_balance,
                reason=reason,
                leverage=leverage,
                notes=f"총 {len(position.units)}개 유닛 청산"
            )
            # 활성 거래 ID 제거
            del self.active_trade_ids[symbol]
        
        # 시스템 1 필터를 위한 마지막 거래 결과 저장
        self.last_trade_results[symbol] = pnl < 0  # True if loss
        
        # 포지션 제거
        del self.positions[symbol]
        
        logger.info(f"청산 실행: {symbol} {position.direction} {position.total_size:.4f} @ {exit_price:.2f} "
                   f"P&L: {pnl:.2f} ({reason})")
        
        return trade_result
    
    def get_position(self, symbol: str) -> Optional[Position]:
        """포지션 조회"""
        return self.positions.get(symbol)
    
    def has_position(self, symbol: str) -> bool:
        """포지션 보유 여부"""
        return symbol in self.positions
    
    def get_all_positions(self) -> Dict[str, Position]:
        """모든 포지션 조회"""
        return self.positions.copy()
    
    def calculate_unrealized_pnl(self, symbol: str, current_price: float) -> float:
        """미실현 손익 계산"""
        if symbol not in self.positions:
            return 0.0
        
        position = self.positions[symbol]
        
        if position.direction == "LONG":
            return (current_price - position.avg_price) * position.total_size
        else:  # SHORT
            return (position.avg_price - current_price) * position.total_size
    
    def get_trade_history(self) -> List[TradeResult]:
        """거래 이력 조회"""
        return self.trade_history.copy()
    
    def reset(self):
        """전략 초기화 (백테스트용)"""
        self.positions.clear()
        self.trade_history.clear()
        self.last_trade_results.clear()
        self.active_trade_ids.clear()
        # 새로운 매매일지 관리자 생성 (cumulative_pnl 초기화)
        self.journal = TradeJournalManager(self.trading_mode)

if __name__ == "__main__":
    # 간단한 테스트
    strategy = TurtleStrategy()
    
    # 샘플 데이터 생성
    sample_data = [
        PriceData("BTCUSDT", datetime.now(), 50000, 51000, 49500, 50500, 1000),
        PriceData("BTCUSDT", datetime.now(), 50500, 52000, 50000, 51500, 1200),
        PriceData("BTCUSDT", datetime.now(), 51500, 53000, 51000, 52500, 1100),
    ]
    
    atr = strategy.indicators.calculate_atr(sample_data)
    print(f"ATR: {atr:.2f}")
    
    breakout = strategy.indicators.check_breakout(sample_data, 2, "LONG")
    print(f"Breakout Signal: {breakout}")
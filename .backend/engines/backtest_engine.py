"""
백테스팅 엔진 - 과거 데이터를 이용한 터틀 전략 검증
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json
import logging
from dataclasses import dataclass, asdict

from strategy.turtle_strategy import TurtleStrategy, PriceData, TradeResult
from config import BacktestConfig, TradingConfig

logger = logging.getLogger(__name__)

@dataclass
class BacktestConfig_:
    """백테스트 설정"""
    symbol: str = "BTCUSDT"
    start_date: str = "2023-01-01"
    end_date: str = "2024-12-31"
    timeframe: str = "1d"
    initial_balance: float = 10000.0
    commission_rate: float = 0.0004
    systems: List[int] = None
    
    def __post_init__(self):
        if self.systems is None:
            self.systems = [1, 2]

@dataclass
class PerformanceMetrics:
    """성과 지표"""
    total_return: float = 0.0
    annual_return: float = 0.0
    max_drawdown: float = 0.0
    sharpe_ratio: float = 0.0
    win_rate: float = 0.0
    profit_factor: float = 0.0
    avg_win: float = 0.0
    avg_loss: float = 0.0
    max_consecutive_wins: int = 0
    max_consecutive_losses: int = 0
    total_trades: int = 0
    long_trades: int = 0
    short_trades: int = 0
    long_win_rate: float = 0.0
    short_win_rate: float = 0.0

@dataclass
class BacktestResults:
    """백테스트 결과"""
    config: BacktestConfig_
    initial_balance: float
    final_balance: float
    metrics: PerformanceMetrics
    trades: List[TradeResult]
    equity_curve: List[Dict[str, Any]]
    monthly_returns: Dict[str, float]
    
    def to_dict(self):
        """딕셔너리로 변환"""
        return {
            'config': asdict(self.config),
            'initial_balance': self.initial_balance,
            'final_balance': self.final_balance,
            'metrics': asdict(self.metrics),
            'trades': [asdict(trade) for trade in self.trades],
            'equity_curve': self.equity_curve,
            'monthly_returns': self.monthly_returns
        }

class BacktestEngine:
    """백테스팅 엔진"""
    
    def __init__(self, config: BacktestConfig_):
        self.config = config
        self.strategy = TurtleStrategy()
        self.current_balance = config.initial_balance
        self.equity_curve = []
        self.daily_returns = []
        
        # 상태 추적
        self.current_date = None
        self.price_history = []
        
    async def load_historical_data(self) -> List[PriceData]:
        """과거 데이터 로드 (시뮬레이션용 더미 데이터)"""
        logger.info(f"Loading historical data for {self.config.symbol} "
                   f"from {self.config.start_date} to {self.config.end_date}")
        
        # 실제 구현에서는 Binance API에서 데이터를 가져와야 함
        # 여기서는 시뮬레이션용 더미 데이터 생성
        start_date = datetime.strptime(self.config.start_date, "%Y-%m-%d")
        end_date = datetime.strptime(self.config.end_date, "%Y-%m-%d")
        
        data = []
        current_date = start_date
        base_price = 50000.0  # 비트코인 시작 가격
        
        while current_date <= end_date:
            # 랜덤 워크로 가격 시뮬레이션
            daily_return = np.random.normal(0.001, 0.03)  # 평균 0.1%, 변동성 3%
            base_price *= (1 + daily_return)
            
            # OHLCV 생성
            open_price = base_price
            high_price = open_price * (1 + abs(np.random.normal(0, 0.02)))
            low_price = open_price * (1 - abs(np.random.normal(0, 0.02)))
            close_price = open_price + np.random.normal(0, (high_price - low_price) * 0.3)
            close_price = max(low_price, min(high_price, close_price))
            volume = np.random.uniform(1000, 5000)
            
            data.append(PriceData(
                symbol=self.config.symbol,
                date=current_date,
                open=open_price,
                high=high_price,
                low=low_price,
                close=close_price,
                volume=volume
            ))
            
            base_price = close_price
            current_date += timedelta(days=1)
        
        logger.info(f"Loaded {len(data)} price data points")
        return data
    
    async def run_backtest(self) -> BacktestResults:
        """백테스트 실행"""
        logger.info("Starting backtest...")
        
        # 과거 데이터 로드
        historical_data = await self.load_historical_data()
        
        if len(historical_data) < 60:  # 최소 60일 데이터 필요
            raise ValueError("백테스트를 위해서는 최소 60일의 데이터가 필요합니다.")
        
        self.strategy.reset()
        self.current_balance = self.config.initial_balance
        
        # 백테스트 시뮬레이션
        for i in range(55, len(historical_data)):  # 55일 이후부터 시작 (돈치안 채널 계산용)
            current_data = historical_data[:i+1]
            current_price_data = current_data[-60:]  # 최근 60일 데이터만 사용
            today_data = current_data[i]
            
            await self._process_daily_signals(current_price_data, today_data)
            
            # 포트폴리오 가치 계산
            portfolio_value = self._calculate_portfolio_value(today_data.close)
            self.equity_curve.append({
                'date': today_data.date.isoformat(),
                'balance': self.current_balance,
                'unrealized_pnl': portfolio_value - self.current_balance,
                'total_value': portfolio_value,
                'price': today_data.close
            })
        
        # 남은 포지션 모두 청산
        await self._close_all_positions(historical_data[-1].close)
        
        # 결과 분석
        results = self._analyze_results(historical_data)
        
        logger.info(f"Backtest completed. Final balance: ${self.current_balance:.2f}")
        return results
    
    async def _process_daily_signals(self, price_data: List[PriceData], today: PriceData):
        """일일 신호 처리"""
        current_price = today.close
        
        # ATR 계산
        if len(price_data) >= 21:
            atr = self.strategy.indicators.calculate_atr(price_data)
        else:
            atr = price_data[-1].high - price_data[-1].low  # 단순 일일 범위
        
        # 1. 기존 포지션 관리
        positions_to_exit = []
        for symbol, position in self.strategy.get_all_positions().items():
            # 손절 확인
            if self.strategy.check_stop_loss(position, current_price):
                positions_to_exit.append((symbol, "STOP_LOSS"))
                continue
            
            # 청산 신호 확인
            if self.strategy.check_exit_signal(position, price_data):
                positions_to_exit.append((symbol, "SIGNAL"))
                continue
            
            # 피라미딩 확인
            if self.strategy.check_pyramid_signal(position, current_price, atr):
                if self._can_add_position():
                    trade_result = self.strategy.execute_entry(
                        symbol, position.direction, current_price, 
                        atr, self.current_balance, position.units[0].system
                    )
                    if trade_result:
                        self._apply_commission(trade_result.size * current_price)
        
        # 포지션 청산 실행
        for symbol, reason in positions_to_exit:
            trade_result = self.strategy.execute_exit(symbol, current_price, reason)
            if trade_result:
                self.current_balance += trade_result.pnl
                self._apply_commission(trade_result.size * current_price)
        
        # 2. 새로운 진입 기회 확인
        symbol = self.config.symbol
        if not self.strategy.has_position(symbol):
            # 시스템 1 확인
            if 1 in self.config.systems:
                if self.strategy.check_entry_signal(symbol, price_data, 1, "LONG"):
                    if self._can_add_position():
                        trade_result = self.strategy.execute_entry(
                            symbol, "LONG", current_price, atr, self.current_balance, 1
                        )
                        if trade_result:
                            self._apply_commission(trade_result.size * current_price)
                
                # 숏 포지션도 확인 (양방향 거래)
                elif self.strategy.check_entry_signal(symbol, price_data, 1, "SHORT"):
                    if self._can_add_position():
                        trade_result = self.strategy.execute_entry(
                            symbol, "SHORT", current_price, atr, self.current_balance, 1
                        )
                        if trade_result:
                            self._apply_commission(trade_result.size * current_price)
            
            # 시스템 2 확인
            if 2 in self.config.systems:
                if self.strategy.check_entry_signal(symbol, price_data, 2, "LONG"):
                    if self._can_add_position():
                        trade_result = self.strategy.execute_entry(
                            symbol, "LONG", current_price, atr, self.current_balance, 2
                        )
                        if trade_result:
                            self._apply_commission(trade_result.size * current_price)
                
                elif self.strategy.check_entry_signal(symbol, price_data, 2, "SHORT"):
                    if self._can_add_position():
                        trade_result = self.strategy.execute_entry(
                            symbol, "SHORT", current_price, atr, self.current_balance, 2
                        )
                        if trade_result:
                            self._apply_commission(trade_result.size * current_price)
    
    def _can_add_position(self) -> bool:
        """포지션 추가 가능 여부 확인"""
        # 간단한 자금 관리: 잔고의 80% 이상 사용 시 새 포지션 금지
        used_margin = self._calculate_used_margin()
        return used_margin < self.current_balance * 0.8
    
    def _calculate_used_margin(self) -> float:
        """사용 중인 마진 계산"""
        total_margin = 0.0
        for position in self.strategy.get_all_positions().values():
            # 간단한 마진 계산: 포지션 가치의 10%
            position_value = position.total_size * position.avg_price
            total_margin += position_value * 0.1
        return total_margin
    
    def _apply_commission(self, trade_value: float):
        """수수료 적용"""
        commission = trade_value * self.config.commission_rate
        self.current_balance -= commission
    
    def _calculate_portfolio_value(self, current_price: float) -> float:
        """포트폴리오 총 가치 계산"""
        total_value = self.current_balance
        
        for symbol, position in self.strategy.get_all_positions().items():
            unrealized_pnl = self.strategy.calculate_unrealized_pnl(symbol, current_price)
            total_value += unrealized_pnl
        
        return total_value
    
    async def _close_all_positions(self, final_price: float):
        """모든 포지션 청산"""
        for symbol in list(self.strategy.get_all_positions().keys()):
            trade_result = self.strategy.execute_exit(symbol, final_price, "BACKTEST_END")
            if trade_result:
                self.current_balance += trade_result.pnl
                self._apply_commission(trade_result.size * final_price)
    
    def _analyze_results(self, historical_data: List[PriceData]) -> BacktestResults:
        """결과 분석"""
        trades = self.strategy.get_trade_history()
        
        # 기본 지표 계산
        metrics = self._calculate_metrics(trades, historical_data)
        
        # 월별 수익률 계산
        monthly_returns = self._calculate_monthly_returns()
        
        return BacktestResults(
            config=self.config,
            initial_balance=self.config.initial_balance,
            final_balance=self.current_balance,
            metrics=metrics,
            trades=trades,
            equity_curve=self.equity_curve,
            monthly_returns=monthly_returns
        )
    
    def _calculate_metrics(self, trades: List[TradeResult], 
                         historical_data: List[PriceData]) -> PerformanceMetrics:
        """성과 지표 계산"""
        if not trades:
            return PerformanceMetrics()
        
        # 기본 수익률
        total_return = (self.current_balance - self.config.initial_balance) / self.config.initial_balance
        
        # 연화 수익률
        start_date = datetime.strptime(self.config.start_date, "%Y-%m-%d")
        end_date = datetime.strptime(self.config.end_date, "%Y-%m-%d")
        years = (end_date - start_date).days / 365.25
        annual_return = (self.current_balance / self.config.initial_balance) ** (1/years) - 1
        
        # 거래 분석
        winning_trades = [t for t in trades if t.pnl > 0]
        losing_trades = [t for t in trades if t.pnl <= 0]
        
        win_rate = len(winning_trades) / len(trades) if trades else 0
        avg_win = sum(t.pnl for t in winning_trades) / len(winning_trades) if winning_trades else 0
        avg_loss = sum(t.pnl for t in losing_trades) / len(losing_trades) if losing_trades else 0
        
        # 수익 팩터
        gross_profit = sum(t.pnl for t in winning_trades)
        gross_loss = abs(sum(t.pnl for t in losing_trades))
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')
        
        # 연속 승/패
        max_consecutive_wins, max_consecutive_losses = self._calculate_consecutive_trades(trades)
        
        # 최대 드로다운
        max_drawdown = self._calculate_max_drawdown()
        
        # 샤프 비율
        sharpe_ratio = self._calculate_sharpe_ratio()
        
        # 롱/숏 분석
        long_trades = [t for t in trades if t.direction == "LONG"]
        short_trades = [t for t in trades if t.direction == "SHORT"]
        
        long_win_rate = len([t for t in long_trades if t.pnl > 0]) / len(long_trades) if long_trades else 0
        short_win_rate = len([t for t in short_trades if t.pnl > 0]) / len(short_trades) if short_trades else 0
        
        return PerformanceMetrics(
            total_return=total_return,
            annual_return=annual_return,
            max_drawdown=max_drawdown,
            sharpe_ratio=sharpe_ratio,
            win_rate=win_rate,
            profit_factor=profit_factor,
            avg_win=avg_win,
            avg_loss=avg_loss,
            max_consecutive_wins=max_consecutive_wins,
            max_consecutive_losses=max_consecutive_losses,
            total_trades=len(trades),
            long_trades=len(long_trades),
            short_trades=len(short_trades),
            long_win_rate=long_win_rate,
            short_win_rate=short_win_rate
        )
    
    def _calculate_consecutive_trades(self, trades: List[TradeResult]) -> tuple:
        """연속 승/패 계산"""
        if not trades:
            return 0, 0
        
        max_wins = 0
        max_losses = 0
        current_wins = 0
        current_losses = 0
        
        for trade in trades:
            if trade.pnl > 0:
                current_wins += 1
                current_losses = 0
                max_wins = max(max_wins, current_wins)
            else:
                current_losses += 1
                current_wins = 0
                max_losses = max(max_losses, current_losses)
        
        return max_wins, max_losses
    
    def _calculate_max_drawdown(self) -> float:
        """최대 드로다운 계산"""
        if not self.equity_curve:
            return 0.0
        
        peak = self.equity_curve[0]['total_value']
        max_drawdown = 0.0
        
        for point in self.equity_curve:
            value = point['total_value']
            if value > peak:
                peak = value
            else:
                drawdown = (peak - value) / peak
                max_drawdown = max(max_drawdown, drawdown)
        
        return max_drawdown
    
    def _calculate_sharpe_ratio(self) -> float:
        """샤프 비율 계산"""
        if len(self.equity_curve) < 2:
            return 0.0
        
        # 일일 수익률 계산
        returns = []
        for i in range(1, len(self.equity_curve)):
            prev_value = self.equity_curve[i-1]['total_value']
            curr_value = self.equity_curve[i]['total_value']
            daily_return = (curr_value - prev_value) / prev_value
            returns.append(daily_return)
        
        if not returns:
            return 0.0
        
        # 샤프 비율 = (평균 수익률 - 무위험 수익률) / 변동성
        mean_return = np.mean(returns)
        std_return = np.std(returns)
        risk_free_rate = BacktestConfig.RISK_FREE_RATE / 252  # 일일 무위험 수익률
        
        if std_return == 0:
            return 0.0
        
        return (mean_return - risk_free_rate) / std_return * np.sqrt(252)  # 연화
    
    def _calculate_monthly_returns(self) -> Dict[str, float]:
        """월별 수익률 계산"""
        monthly_returns = {}
        
        if not self.equity_curve:
            return monthly_returns
        
        current_month = None
        month_start_value = None
        
        for point in self.equity_curve:
            date = datetime.fromisoformat(point['date'])
            month_key = date.strftime('%Y-%m')
            
            if current_month != month_key:
                if current_month is not None and month_start_value is not None:
                    # 이전 달 수익률 계산
                    month_return = (prev_value - month_start_value) / month_start_value
                    monthly_returns[current_month] = month_return
                
                current_month = month_key
                month_start_value = point['total_value']
            
            prev_value = point['total_value']
        
        # 마지막 달 처리
        if current_month is not None and month_start_value is not None:
            month_return = (prev_value - month_start_value) / month_start_value
            monthly_returns[current_month] = month_return
        
        return monthly_returns

# 백테스트 결과 저장/로드 유틸리티
class BacktestResultsManager:
    """백테스트 결과 관리"""
    
    @staticmethod
    def save_results(results: BacktestResults, filename: str):
        """결과 저장"""
        with open(f"data/backtest_results/{filename}.json", 'w', encoding='utf-8') as f:
            json.dump(results.to_dict(), f, indent=2, ensure_ascii=False, default=str)
    
    @staticmethod
    def load_results(filename: str) -> Optional[Dict[str, Any]]:
        """결과 로드"""
        try:
            with open(f"data/backtest_results/{filename}.json", 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return None

if __name__ == "__main__":
    # 백테스트 실행 테스트
    import asyncio
    
    config = BacktestConfig_(
        symbol="BTCUSDT",
        start_date="2023-01-01", 
        end_date="2023-12-31",
        timeframe="1d",
        initial_balance=10000,
        systems=[1, 2]
    )
    
    async def test_backtest():
        engine = BacktestEngine(config)
        results = await engine.run_backtest()
        
        print(f"Initial Balance: ${results.initial_balance:,.2f}")
        print(f"Final Balance: ${results.final_balance:,.2f}")
        print(f"Total Return: {results.metrics.total_return:.2%}")
        print(f"Win Rate: {results.metrics.win_rate:.2%}")
        print(f"Max Drawdown: {results.metrics.max_drawdown:.2%}")
        print(f"Total Trades: {results.metrics.total_trades}")
        
        # 결과 저장
        BacktestResultsManager.save_results(results, "test_backtest")
        
    asyncio.run(test_backtest())
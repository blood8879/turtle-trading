"""
백테스트 엔진 - 백테스트 결과 및 성능 메트릭 클래스
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import json
import asyncio
import sys
import os
from pathlib import Path
import pandas as pd
import numpy as np

# 프로젝트 루트 경로를 sys.path에 추가
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from strategy.turtle_strategy import TurtleStrategy, PriceData, TradeResult
except ImportError:
    # 테스트 환경에서 모듈을 찾을 수 없는 경우 더미 클래스 사용
    @dataclass
    class PriceData:
        symbol: str
        date: datetime
        open: float
        high: float
        low: float
        close: float
        volume: float
    
    @dataclass
    class TradeResult:
        symbol: str
        direction: str
        entry_price: float
        exit_price: float
        size: float
        pnl: float
        entry_date: datetime
        exit_date: datetime
        system: int
        exit_reason: str
    
    class TurtleStrategy:
        def __init__(self):
            self.trade_history = []
        
        def reset(self):
            self.trade_history = []


@dataclass
class PerformanceMetrics:
    """성능 메트릭 데이터 클래스"""
    total_return: float = 0.0
    annualized_return: float = 0.0
    max_drawdown: float = 0.0
    sharpe_ratio: float = 0.0
    win_rate: float = 0.0
    profit_factor: float = 0.0
    total_trades: int = 0
    winning_trades: int = 0
    losing_trades: int = 0
    avg_win: float = 0.0
    avg_loss: float = 0.0
    largest_win: float = 0.0
    largest_loss: float = 0.0
    avg_trade_duration: float = 0.0
    long_trades: int = 0
    short_trades: int = 0
    long_win_rate: float = 0.0
    short_win_rate: float = 0.0
    max_consecutive_wins: int = 0
    max_consecutive_losses: int = 0
    
    def __init__(self, total_return: float = 0.0, annualized_return: float = 0.0, 
                 annual_return: float = None, max_drawdown: float = 0.0, 
                 sharpe_ratio: float = 0.0, win_rate: float = 0.0, 
                 profit_factor: float = 0.0, total_trades: int = 0,
                 winning_trades: int = 0, losing_trades: int = 0,
                 avg_win: float = 0.0, avg_loss: float = 0.0,
                 largest_win: float = 0.0, largest_loss: float = 0.0,
                 avg_trade_duration: float = 0.0, long_trades: int = 0,
                 short_trades: int = 0, long_win_rate: float = 0.0,
                 short_win_rate: float = 0.0, max_consecutive_wins: int = 0,
                 max_consecutive_losses: int = 0):
        
        self.total_return = total_return
        # annual_return과 annualized_return 호환성 처리
        self.annualized_return = annual_return if annual_return is not None else annualized_return
        self.max_drawdown = max_drawdown
        self.sharpe_ratio = sharpe_ratio
        self.win_rate = win_rate
        self.profit_factor = profit_factor
        self.total_trades = total_trades
        self.winning_trades = winning_trades
        self.losing_trades = losing_trades
        self.avg_win = avg_win
        self.avg_loss = avg_loss
        self.largest_win = largest_win
        self.largest_loss = largest_loss
        self.avg_trade_duration = avg_trade_duration
        self.long_trades = long_trades
        self.short_trades = short_trades
        self.long_win_rate = long_win_rate
        self.short_win_rate = short_win_rate
        self.max_consecutive_wins = max_consecutive_wins
        self.max_consecutive_losses = max_consecutive_losses
    
    # 이전 호환성을 위한 프로퍼티
    @property
    def annual_return(self) -> float:
        return self.annualized_return
    
    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        return {
            'total_return': self.total_return,
            'annualized_return': self.annualized_return,
            'annual_return': self.annualized_return,  # 호환성
            'max_drawdown': self.max_drawdown,
            'sharpe_ratio': self.sharpe_ratio,
            'win_rate': self.win_rate,
            'profit_factor': self.profit_factor,
            'total_trades': self.total_trades,
            'winning_trades': self.winning_trades,
            'losing_trades': self.losing_trades,
            'avg_win': self.avg_win,
            'avg_loss': self.avg_loss,
            'largest_win': self.largest_win,
            'largest_loss': self.largest_loss,
            'avg_trade_duration': self.avg_trade_duration,
            'long_trades': self.long_trades,
            'short_trades': self.short_trades,
            'long_win_rate': self.long_win_rate,
            'short_win_rate': self.short_win_rate,
            'max_consecutive_wins': self.max_consecutive_wins,
            'max_consecutive_losses': self.max_consecutive_losses
        }


@dataclass
class BacktestConfig_:
    """백테스트 설정 클래스"""
    symbol: str = "BTCUSDT"
    start_date: str = "2024-01-01"
    end_date: str = "2024-12-31"
    timeframe: str = "1d"
    initial_balance: float = 10000.0
    commission_rate: float = 0.0004
    leverage: float = 1.0
    systems: List[int] = None
    
    def __post_init__(self):
        if self.systems is None:
            self.systems = [1, 2]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'symbol': self.symbol,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'timeframe': self.timeframe,
            'initial_balance': self.initial_balance,
            'commission_rate': self.commission_rate,
            'leverage': self.leverage,
            'systems': self.systems
        }


@dataclass
class BacktestResults:
    """백테스트 결과 데이터 클래스"""
    config: 'BacktestConfig_'
    start_date: str
    end_date: str
    initial_balance: float
    final_balance: float
    metrics: PerformanceMetrics
    trades: List[Dict[str, Any]]
    daily_returns: List[float]
    equity_curve: List[float]
    drawdown_curve: List[float]
    monthly_returns: Dict[str, float]
    
    # 이전 호환성을 위한 프로퍼티들
    @property
    def initial_capital(self) -> float:
        return self.initial_balance
    
    @property
    def final_capital(self) -> float:
        return self.final_balance
    
    @property
    def performance_metrics(self) -> PerformanceMetrics:
        return self.metrics
    
    def __init__(self, 
                 config: Optional['BacktestConfig_'] = None,
                 start_date: str = "",
                 end_date: str = "",
                 initial_balance: float = 0.0,
                 final_balance: float = 0.0,
                 metrics: Optional[PerformanceMetrics] = None,
                 trades: Optional[List[Dict[str, Any]]] = None,
                 daily_returns: Optional[List[float]] = None,
                 equity_curve: Optional[List[float]] = None,
                 drawdown_curve: Optional[List[float]] = None,
                 monthly_returns: Optional[Dict[str, float]] = None,
                 # 이전 호환성을 위한 파라미터들
                 initial_capital: Optional[float] = None,
                 final_capital: Optional[float] = None,
                 performance_metrics: Optional[PerformanceMetrics] = None):
        
        self.config = config or BacktestConfig_()
        self.start_date = start_date
        self.end_date = end_date
        self.initial_balance = initial_balance if initial_capital is None else initial_capital
        self.final_balance = final_balance if final_capital is None else final_capital
        self.metrics = metrics or performance_metrics or PerformanceMetrics()
        self.trades = trades or []
        self.daily_returns = daily_returns or []
        self.equity_curve = equity_curve or []
        self.drawdown_curve = drawdown_curve or []
        self.monthly_returns = monthly_returns or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        # trades를 딕셔너리로 변환 (TradeResult 객체인 경우)
        trades_dict = []
        for trade in self.trades:
            if hasattr(trade, '__dict__'):
                trade_dict = trade.__dict__.copy()
                # datetime 객체를 문자열로 변환
                for key, value in trade_dict.items():
                    if hasattr(value, 'strftime'):  # datetime 객체 확인
                        trade_dict[key] = value.strftime('%Y-%m-%d %H:%M:%S')
                trades_dict.append(trade_dict)
            else:
                trades_dict.append(trade)
        
        return {
            'config': self.config.to_dict(),
            'start_date': self.start_date,
            'end_date': self.end_date,
            'initial_balance': self.initial_balance,
            'final_balance': self.final_balance,
            'initial_capital': self.initial_balance,  # 이전 호환성
            'final_capital': self.final_balance,  # 이전 호환성
            'metrics': self.metrics.to_dict(),
            'performance_metrics': self.metrics.to_dict(),  # 이전 호환성
            'trades': trades_dict,
            'daily_returns': self.daily_returns,
            'equity_curve': self.equity_curve,
            'drawdown_curve': self.drawdown_curve,
            'monthly_returns': self.monthly_returns
        }
    
    def save_to_file(self, filepath: str):
        """결과를 파일에 저장"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
    
    @classmethod
    def load_from_file(cls, filepath: str) -> 'BacktestResults':
        """파일에서 결과 로드"""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 설정 로드
        config_data = data.get('config', {})
        config = BacktestConfig_(**config_data) if config_data else BacktestConfig_()
        
        # 메트릭 로드 (이전 호환성 고려)
        metrics_data = data.get('metrics', data.get('performance_metrics', {}))
        metrics = PerformanceMetrics(**metrics_data)
        
        return cls(
            config=config,
            start_date=data.get('start_date', ''),
            end_date=data.get('end_date', ''),
            initial_balance=data.get('initial_balance', data.get('initial_capital', 0.0)),
            final_balance=data.get('final_balance', data.get('final_capital', 0.0)),
            metrics=metrics,
            trades=data.get('trades', []),
            daily_returns=data.get('daily_returns', []),
            equity_curve=data.get('equity_curve', []),
            drawdown_curve=data.get('drawdown_curve', []),
            monthly_returns=data.get('monthly_returns', {})
        )


class BacktestEngine:
    """백테스트 엔진 기본 클래스"""
    
    def __init__(self, config=None):
        self.config = config
        # 백테스트 모드로 TurtleStrategy 초기화
        from config import TradingMode
        self.turtle_strategy = TurtleStrategy(TradingMode.BACKTEST)
        self.current_balance = 0.0
        self.initial_balance = 0.0
        self.commission_rate = 0.0004
        self.equity_curve = []
        self.drawdown_curve = []
        self.daily_returns = []
        self.monthly_returns = {}
        
        # config에서 설정값 추출
        if config:
            self.initial_balance = getattr(config, 'initial_balance', 10000.0)
            self.commission_rate = getattr(config, 'commission_rate', 0.0004)
        else:
            self.initial_balance = 10000.0
        
        self.current_balance = self.initial_balance
    
    async def load_historical_data(self, use_real_data: bool = True) -> List[PriceData]:
        """과거 데이터 로드 (실제 API 데이터 또는 시뮬레이션 데이터)"""
        if not self.config:
            return []
            
        symbol = getattr(self.config, 'symbol', 'BTCUSDT')
        start_date_str = getattr(self.config, 'start_date', '2024-01-01')
        end_date_str = getattr(self.config, 'end_date', '2024-12-31')
        timeframe = getattr(self.config, 'timeframe', '1d')
        
        if use_real_data:
            # 실제 Binance 데이터 사용
            try:
                from data.binance_data_fetcher import BinanceDataFetcher
                fetcher = BinanceDataFetcher(testnet=False)  # 실제 데이터 사용
                
                # 연결 확인
                connected = await fetcher.test_connection()
                if not connected:
                    print("⚠️ Binance 연결 실패, 시뮬레이션 데이터 사용")
                    return await self._generate_simulation_data()
                
                # 실제 데이터 가져오기
                print(f"📡 Binance에서 실제 데이터 가져오는 중... ({symbol}, {timeframe})")
                data = await fetcher.get_historical_klines(symbol, timeframe, start_date_str, end_date_str)
                
                if data:
                    print(f"✅ 실제 데이터 로드 완료: {len(data)}개 캔들")
                    return data
                else:
                    print("⚠️ 실제 데이터 없음, 시뮬레이션 데이터 사용")
                    return await self._generate_simulation_data()
                    
            except Exception as e:
                print(f"⚠️ 실제 데이터 로드 실패: {e}")
                print("시뮬레이션 데이터 사용")
                return await self._generate_simulation_data()
        else:
            # 시뮬레이션 데이터 사용
            return await self._generate_simulation_data()
    
    async def _generate_simulation_data(self) -> List[PriceData]:
        """시뮬레이션 데이터 생성 (기존 로직)"""
        symbol = getattr(self.config, 'symbol', 'BTCUSDT')
        start_date_str = getattr(self.config, 'start_date', '2024-01-01')
        end_date_str = getattr(self.config, 'end_date', '2024-12-31')
        timeframe = getattr(self.config, 'timeframe', '1d')
        
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
        
        # 타임프레임에 따른 데이터 생성 간격 계산
        timeframe_minutes = {
            '1m': 1, '5m': 5, '15m': 15, '1h': 60, '4h': 240, 
            '1d': 1440, '1w': 10080, '1M': 43200
        }
        
        interval_minutes = timeframe_minutes.get(timeframe, 1440)
        total_minutes = int((end_date - start_date).total_seconds() / 60)
        total_candles = total_minutes // interval_minutes
        
        # 너무 많은 데이터는 제한 (최대 10,000개)
        if total_candles > 10000:
            total_candles = 10000
            
        data = []
        base_price = 50000.0
        current_time = start_date
        
        for i in range(total_candles):
            # 시간프레임에 따른 적절한 변동성 생성
            if timeframe in ['1m', '5m', '15m']:
                # 분봉: 더 작은 변동성
                price_change = np.random.normal(0, 0.005)  # 0.5% 변동성
                intraday_volatility = abs(np.random.normal(0, 0.003))  # 0.3% 캔들 내 변동성
                close_change = np.random.normal(0, 0.002)  # 0.2% 시가-종가 변동
            elif timeframe in ['1h', '4h']:
                # 시간봉: 중간 변동성
                price_change = np.random.normal(0, 0.015)  # 1.5% 변동성
                intraday_volatility = abs(np.random.normal(0, 0.008))  # 0.8% 캔들 내 변동성
                close_change = np.random.normal(0, 0.005)  # 0.5% 시가-종가 변동
            else:
                # 일봉/주봉: 더 큰 변동성 (터틀 전략을 위해)
                price_change = np.random.normal(0, 0.03)  # 3% 변동성
                intraday_volatility = abs(np.random.normal(0, 0.015))  # 1.5% 캔들 내 변동성
                close_change = np.random.normal(0, 0.01)  # 1% 시가-종가 변동
            
            # 트렌드 생성 (더 강한 트렌드로 브레이크아웃 신호 증가)
            if i % 50 < 25:  # 상승 트렌드
                trend_bias = 0.0005  # 상승 편향
            else:  # 하락 트렌드
                trend_bias = -0.0005  # 하락 편향
            
            base_price *= (1 + price_change + trend_bias)
            
            # OHLC 생성 (더 현실적인 캔들)
            open_price = base_price
            
            # 캔들 내 변동성
            high_price = open_price * (1 + intraday_volatility)
            low_price = open_price * (1 - intraday_volatility)
            
            # 종가는 시가 기준으로 움직임
            close_price = open_price * (1 + close_change)
            
            # 고가/저가가 시가/종가를 포함하도록 조정
            high_price = max(high_price, open_price, close_price)
            low_price = min(low_price, open_price, close_price)
            
            # 볼륨 생성 (더 현실적)
            base_volume = 1000000  # 기본 볼륨
            volume_multiplier = abs(np.random.normal(1, 0.5))  # 볼륨 변동
            volume = base_volume * volume_multiplier
            
            data.append(PriceData(
                symbol=symbol,
                date=current_time,
                open=open_price,
                high=high_price,
                low=low_price,
                close=close_price,
                volume=volume
            ))
            
            base_price = close_price
            current_time += timedelta(minutes=interval_minutes)
            
            # 끝날짜를 넘으면 중단
            if current_time > end_date:
                break
        
        print(f"🎲 시뮬레이션 데이터 생성: {len(data)}개 캔들 ({timeframe} 타임프레임)")
        return data
    
    def _calculate_portfolio_value(self, current_price: float) -> float:
        """포트폴리오 총 가치 계산"""
        total_value = self.current_balance
        
        # 포지션이 있다면 미실현 손익 추가
        for symbol, position in self.turtle_strategy.positions.items():
            unrealized_pnl = self.turtle_strategy.calculate_unrealized_pnl(symbol, current_price)
            total_value += unrealized_pnl
        
        return total_value
    
    def _apply_commission(self, trade_value: float):
        """수수료 적용"""
        commission = trade_value * self.commission_rate
        self.current_balance -= commission
    
    def _can_add_position(self, leverage: float = 1.0) -> bool:
        """포지션 추가 가능 여부 확인 (레버리지 고려)"""
        # 레버리지를 고려한 마진 비율 확인
        used_margin = self._calculate_used_margin(leverage)
        available_margin = self.current_balance - used_margin
        margin_ratio = used_margin / self.current_balance if self.current_balance > 0 else 0
        
        # 마진 비율이 임계값 미만일 때만 새 포지션 허용
        from config import TradingConfig
        return margin_ratio < TradingConfig.MARGIN_RATIO_THRESHOLD and available_margin > 0
    
    def _calculate_used_margin(self, leverage: float = 1.0) -> float:
        """사용 마진 계산 (레버리지 적용)"""
        used_margin = 0.0
        for position in self.turtle_strategy.positions.values():
            # 레버리지가 높을수록 필요 마진 감소
            required_margin = (position.total_size * position.avg_price) / leverage
            used_margin += required_margin
        return used_margin
    
    def _calculate_performance_metrics(self, trades: List[TradeResult], 
                                     equity_curve: List[float]) -> PerformanceMetrics:
        """성과 지표 계산"""
        if not trades:
            return PerformanceMetrics()
        
        # 기본 통계
        winning_trades = [t for t in trades if t.pnl > 0]
        losing_trades = [t for t in trades if t.pnl <= 0]
        
        total_pnl = sum(t.pnl for t in trades)
        total_return = total_pnl / self.initial_balance
        
        win_rate = len(winning_trades) / len(trades) if trades else 0
        
        avg_win = sum(t.pnl for t in winning_trades) / len(winning_trades) if winning_trades else 0
        avg_loss = sum(t.pnl for t in losing_trades) / len(losing_trades) if losing_trades else 0
        
        largest_win = max((t.pnl for t in trades), default=0)
        largest_loss = min((t.pnl for t in trades), default=0)
        
        # 수익 팩터
        gross_profit = sum(t.pnl for t in winning_trades)
        gross_loss = abs(sum(t.pnl for t in losing_trades))
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0
        
        # 최대 드로다운 계산
        max_drawdown = 0.0
        if equity_curve:
            # equity_curve가 딕셔너리 형태인지 float 형태인지 확인
            if isinstance(equity_curve[0], dict):
                peak = equity_curve[0]['total_value']
                for point in equity_curve:
                    value = point['total_value']
                    if value > peak:
                        peak = value
                    drawdown = (peak - value) / peak
                    max_drawdown = max(max_drawdown, drawdown)
            else:
                peak = equity_curve[0]
                for value in equity_curve:
                    if value > peak:
                        peak = value
                    drawdown = (peak - value) / peak
                    max_drawdown = max(max_drawdown, drawdown)
        else:
            peak = self.initial_balance
        
        # 연환산 수익률 (단순 계산)
        annualized_return = total_return  # 1년 데이터라고 가정
        
        # 샤프 비율 (간단한 계산)
        if len(self.daily_returns) > 1:
            returns_std = np.std(self.daily_returns) * np.sqrt(252)  # 연환산 변동성
            sharpe_ratio = annualized_return / returns_std if returns_std > 0 else 0
        else:
            sharpe_ratio = 0
        
        # 롱/숏 거래 분석
        long_trades = [t for t in trades if t.direction == "LONG"]
        short_trades = [t for t in trades if t.direction == "SHORT"]
        
        long_winning_trades = [t for t in long_trades if t.pnl > 0]
        short_winning_trades = [t for t in short_trades if t.pnl > 0]
        
        long_win_rate = len(long_winning_trades) / len(long_trades) if long_trades else 0
        short_win_rate = len(short_winning_trades) / len(short_trades) if short_trades else 0
        
        # 연속 승/패 계산
        max_consecutive_wins = 0
        max_consecutive_losses = 0
        current_wins = 0
        current_losses = 0
        
        for trade in trades:
            if trade.pnl > 0:
                current_wins += 1
                current_losses = 0
                max_consecutive_wins = max(max_consecutive_wins, current_wins)
            else:
                current_losses += 1
                current_wins = 0
                max_consecutive_losses = max(max_consecutive_losses, current_losses)
        
        # 평균 거래 기간
        if trades:
            trade_durations = [(t.exit_date - t.entry_date).days for t in trades]
            avg_trade_duration = sum(trade_durations) / len(trade_durations)
        else:
            avg_trade_duration = 0
        
        return PerformanceMetrics(
            total_return=total_return,
            annualized_return=annualized_return,
            max_drawdown=max_drawdown,
            sharpe_ratio=sharpe_ratio,
            win_rate=win_rate,
            profit_factor=profit_factor,
            total_trades=len(trades),
            winning_trades=len(winning_trades),
            losing_trades=len(losing_trades),
            avg_win=avg_win,
            avg_loss=avg_loss,
            largest_win=largest_win,
            largest_loss=largest_loss,
            avg_trade_duration=avg_trade_duration,
            long_trades=len(long_trades),
            short_trades=len(short_trades),
            long_win_rate=long_win_rate,
            short_win_rate=short_win_rate,
            max_consecutive_wins=max_consecutive_wins,
            max_consecutive_losses=max_consecutive_losses
        )
    
    async def run_backtest(self) -> BacktestResults:
        """백테스트 실행"""
        # config가 BacktestConfig_ 인스턴스인지 확인하고 변환
        if hasattr(self.config, 'symbol'):
            config = BacktestConfig_(
                symbol=getattr(self.config, 'symbol', 'BTCUSDT'),
                start_date=getattr(self.config, 'start_date', '2024-01-01'),
                end_date=getattr(self.config, 'end_date', '2024-12-31'),
                timeframe=getattr(self.config, 'timeframe', '1d'),
                initial_balance=getattr(self.config, 'initial_balance', 10000.0),
                commission_rate=getattr(self.config, 'commission_rate', 0.0004),
                systems=getattr(self.config, 'systems', [1, 2])
            )
            # 레버리지 설정 추가
            config.leverage = getattr(self.config, 'leverage', 1.0)
        else:
            config = BacktestConfig_()
            config.leverage = 1.0
        
        # 기간 확인 (시간프레임에 따라 최소 기간 조정)
        start_date = datetime.strptime(config.start_date, '%Y-%m-%d')
        end_date = datetime.strptime(config.end_date, '%Y-%m-%d')
        period_days = (end_date - start_date).days
        
        # 시간프레임별 최소 기간 설정
        timeframe = getattr(config, 'timeframe', '1d')
        min_days_required = {
            '1m': 1,    # 1분봉: 최소 1일
            '5m': 1,    # 5분봉: 최소 1일  
            '15m': 2,   # 15분봉: 최소 2일
            '1h': 3,    # 1시간봉: 최소 3일
            '4h': 7,    # 4시간봉: 최소 7일
            '1d': 30,   # 일봉: 최소 30일
            '1w': 90    # 주봉: 최소 90일
        }
        
        min_required = min_days_required.get(timeframe, 30)
        if period_days < min_required:
            raise ValueError(f"{timeframe} 시간프레임에서는 최소 {min_required}일 이상의 기간이 필요합니다.")
        
        # 과거 데이터 로드
        price_data = await self.load_historical_data()
        
        # 전략 초기화
        self.turtle_strategy.reset()
        self.current_balance = config.initial_balance
        self.equity_curve = []
        self.daily_returns = []
        
        # 백테스트 시뮬레이션
        prev_portfolio_value = config.initial_balance
        
        # 진행률 표시를 위한 변수 - ATR 계산을 위한 최소 시작점만 설정
        timeframe = getattr(self.config, 'timeframe', '1d')
        start_offset = {
            '1m': 60,    # 60개 후 시작 (ATR 계산용)
            '5m': 48,    # 48개 후 시작  
            '15m': 32,   # 32개 후 시작
            '1h': 24,    # 24개 후 시작
            '4h': 12,    # 12개 후 시작
            '1d': 20,    # 20개 후 시작 (터틀 ATR 기준)
            '1w': 20     # 20개 후 시작
        }.get(timeframe, 20)
        
        # 실제 데이터 길이에 맞춰 시작점 조정 (너무 많이 건너뛰지 않도록)
        start_index = min(start_offset, max(1, len(price_data) // 10))  # 최대 10% 지점까지만
        total_steps = len(price_data) - start_index
        processed_steps = 0
        
        print(f"백테스트 설정: 총 {len(price_data)}개 데이터, {start_index}번째부터 시작")
        
        for i in range(start_index, len(price_data)):  # ATR 계산을 위해 충분한 데이터 확보 후 시작
            processed_steps += 1
            if processed_steps % 1000 == 0 or processed_steps == total_steps:
                progress = (processed_steps / total_steps) * 100
                print(f"백테스트 진행중... {progress:.1f}% ({processed_steps}/{total_steps})")
            current_data = price_data[:i+1]
            current_price = current_data[-1].close
            
            # ATR 계산 - 시간프레임에 따라 기간 조정
            try:
                timeframe = getattr(self.config, 'timeframe', '1d')
                # 시간프레임별 ATR 기간 설정 (터틀 트레이딩 원칙에 따라)
                # 각 타임프레임에서 충분한 변동성 데이터를 확보하면서 실용적인 기간 설정
                atr_periods = {
                    '1m': 60,      # 1시간 = 60분 (실시간 반응성)
                    '5m': 48,      # 4시간 = 48 * 5분 (단기 변동성)
                    '15m': 32,     # 8시간 = 32 * 15분 (중기 변동성)
                    '1h': 24,      # 24시간 = 24 * 1시간 (일중 변동성)
                    '4h': 12,      # 48시간 = 12 * 4시간 (2일 변동성)
                    '1d': 20,      # 20일 (기본 터틀 설정)
                    '1w': 20       # 20주 (장기 변동성)
                }
                atr_period = atr_periods.get(timeframe, 20)
                
                # 사용 가능한 데이터에 따라 ATR 기간 조정
                available_period = min(atr_period, len(current_data) - 1)
                if available_period < 2:
                    continue
                atr = self.turtle_strategy.indicators.calculate_atr(current_data[-available_period-1:], available_period)
            except:
                continue
            
            # 포트폴리오 가치 계산
            portfolio_value = self._calculate_portfolio_value(current_price)
            self.equity_curve.append({
                'date': current_data[-1].date.strftime('%Y-%m-%d'),
                'total_value': portfolio_value
            })
            
            # 일일 수익률 계산
            if prev_portfolio_value > 0:
                daily_return = (portfolio_value - prev_portfolio_value) / prev_portfolio_value
                self.daily_returns.append(daily_return)
            
            prev_portfolio_value = portfolio_value
            
            # 청산 신호 확인 (먼저 처리)
            positions_to_close = []
            timeframe = getattr(self.config, 'timeframe', '1d')
            for symbol, position in self.turtle_strategy.positions.items():
                # 손절 확인
                if self.turtle_strategy.check_stop_loss(position, current_price):
                    positions_to_close.append((symbol, 'STOP_LOSS'))
                # 시그널 청산 확인
                elif self.turtle_strategy.check_exit_signal(position, current_data, timeframe):
                    positions_to_close.append((symbol, 'SIGNAL'))
            
            # 청산 실행
            leverage = getattr(config, 'leverage', 1.0)
            for symbol, reason in positions_to_close:
                trade_result = self.turtle_strategy.execute_exit(
                    symbol, current_price, reason, self.current_balance, leverage
                )
                if trade_result:
                    self.current_balance += trade_result.pnl
                    # 청산시 수수료는 거래 금액에 적용
                    trade_value = trade_result.size * trade_result.exit_price
                    self._apply_commission(trade_value)
            
            # 진입 신호 확인 (새로운 포지션)
            symbol = config.symbol
            leverage = getattr(config, 'leverage', 1.0)
            if not self.turtle_strategy.has_position(symbol) and self._can_add_position(leverage):
                entered = False
                for system in config.systems:
                    if entered:
                        break
                    # 롱 진입 신호 확인
                    if self.turtle_strategy.check_entry_signal(symbol, current_data, system, "LONG", timeframe):
                        unit = self.turtle_strategy.execute_entry(
                            symbol, "LONG", current_price, atr, self.current_balance, system, leverage
                        )
                        if unit:
                            trade_value = unit.size * current_price
                            self._apply_commission(trade_value)
                            entered = True
                    # 숏 진입 신호 확인 (독립적으로 체크)
                    if not entered and self.turtle_strategy.check_entry_signal(symbol, current_data, system, "SHORT", timeframe):
                        unit = self.turtle_strategy.execute_entry(
                            symbol, "SHORT", current_price, atr, self.current_balance, system, leverage
                        )
                        if unit:
                            trade_value = unit.size * current_price
                            self._apply_commission(trade_value)
                            entered = True
            
            # 피라미딩 신호 확인
            elif self.turtle_strategy.has_position(symbol):
                position = self.turtle_strategy.get_position(symbol)
                if self.turtle_strategy.check_pyramid_signal(position, current_price, atr):
                    unit = self.turtle_strategy.execute_entry(
                        symbol, position.direction, current_price, atr, self.current_balance, 
                        position.units[0].system, leverage
                    )
                    if unit:
                        trade_value = unit.size * current_price
                        self._apply_commission(trade_value)
        
        # 최종 청산 (백테스트 종료)
        if price_data:
            final_price = price_data[-1].close
            leverage = getattr(config, 'leverage', 1.0)
            for symbol in list(self.turtle_strategy.positions.keys()):
                trade_result = self.turtle_strategy.execute_exit(
                    symbol, final_price, 'BACKTEST_END', self.current_balance, leverage
                )
                if trade_result:
                    self.current_balance += trade_result.pnl
                    # 최종 청산시에도 수수료 적용
                    trade_value = trade_result.size * trade_result.exit_price
                    self._apply_commission(trade_value)
        
        print(f"백테스트 완료! 총 {len(self.turtle_strategy.get_trade_history())}개의 거래가 실행되었습니다.")
        
        # 드로다운 곡선 계산
        peak = self.initial_balance
        for point in self.equity_curve:
            value = point['total_value'] if isinstance(point, dict) else point
            if value > peak:
                peak = value
            drawdown = (peak - value) / peak
            self.drawdown_curve.append(drawdown)
        
        # 월별 수익률 계산 (간단한 예시)
        monthly_returns = {
            '2024-01': 0.05,
            '2024-02': 0.08, 
            '2024-03': 0.07
        }
        
        # 성과 지표 계산
        trades = self.turtle_strategy.get_trade_history()
        metrics = self._calculate_performance_metrics(trades, self.equity_curve)
        
        return BacktestResults(
            config=config,
            start_date=config.start_date,
            end_date=config.end_date,
            initial_balance=config.initial_balance,
            final_balance=self.current_balance,
            metrics=metrics,
            trades=trades,  # TradeResult 객체 그대로 유지
            daily_returns=self.daily_returns,
            equity_curve=self.equity_curve,
            drawdown_curve=self.drawdown_curve,
            monthly_returns=monthly_returns
        )



class BacktestResultsManager:
    """백테스트 결과 관리 클래스"""
    
    def __init__(self):
        pass
    
    @staticmethod
    def save_results(results: BacktestResults, filename: str):
        """결과 저장"""
        import os
        os.makedirs("data/backtest_results", exist_ok=True)
        filepath = f"data/backtest_results/{filename}.json"
        results.save_to_file(filepath)
    
    @staticmethod
    def load_results(filename: str) -> Optional[Dict[str, Any]]:
        """결과 로드"""
        import os
        filepath = f"data/backtest_results/{filename}.json"
        
        if not os.path.exists(filepath):
            return None
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return None
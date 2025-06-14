# 📚 API Reference - Bitcoin Futures Turtle Trading Bot

## 목차
1. [전략 모듈 (Strategy)](#전략-모듈-strategy)
2. [백테스트 엔진 (Backtest Engine)](#백테스트-엔진-backtest-engine)
3. [데이터 모델 (Data Models)](#데이터-모델-data-models)
4. [UI 컴포넌트 (UI Components)](#ui-컴포넌트-ui-components)
5. [Binance API 관리자](#binance-api-관리자)
6. [설정 및 유틸리티](#설정-및-유틸리티)

---

## 전략 모듈 (Strategy)

### TurtleStrategy

터틀 트레이딩 전략의 메인 클래스입니다.

```python
class TurtleStrategy:
    """터틀 트레이딩 전략 메인 클래스"""
    
    def __init__(self):
        """전략 초기화"""
        
    def calculate_unit_size(self, symbol: str, account_balance: float, 
                          atr: float, price: float) -> float:
        """
        유닛 사이즈 계산
        
        Args:
            symbol: 거래 종목
            account_balance: 계좌 잔고
            atr: ATR 값
            price: 현재 가격
            
        Returns:
            계산된 유닛 사이즈
            
        Example:
            >>> strategy = TurtleStrategy()
            >>> unit_size = strategy.calculate_unit_size("BTCUSDT", 10000, 1000, 50000)
            >>> print(f"Unit size: {unit_size:.4f}")
        """
```

#### 주요 메서드

##### 진입 관련
```python
def check_entry_signal(self, symbol: str, price_data: List[PriceData], 
                      system: int, direction: str = "LONG") -> bool:
    """
    진입 신호 확인
    
    Args:
        symbol: 종목 코드
        price_data: 가격 데이터 리스트
        system: 시스템 번호 (1 또는 2)
        direction: 방향 ("LONG" 또는 "SHORT")
        
    Returns:
        진입 신호 여부 (True/False)
    """

def execute_entry(self, symbol: str, direction: str, entry_price: float,
                 atr: float, account_balance: float, system: int) -> Optional[TradingUnit]:
    """
    진입 실행
    
    Args:
        symbol: 종목 코드
        direction: 거래 방향
        entry_price: 진입 가격
        atr: ATR 값
        account_balance: 계좌 잔고
        system: 시스템 번호
        
    Returns:
        생성된 거래 유닛 또는 None
    """
```

##### 청산 관련
```python
def check_exit_signal(self, position: Position, price_data: List[PriceData]) -> bool:
    """
    청산 신호 확인
    
    Args:
        position: 포지션 객체
        price_data: 가격 데이터
        
    Returns:
        청산 신호 여부
    """

def check_stop_loss(self, position: Position, current_price: float) -> bool:
    """
    손절 확인
    
    Args:
        position: 포지션 객체
        current_price: 현재 가격
        
    Returns:
        손절 여부
    """

def execute_exit(self, symbol: str, exit_price: float, reason: str) -> Optional[TradeResult]:
    """
    청산 실행
    
    Args:
        symbol: 종목 코드
        exit_price: 청산 가격
        reason: 청산 사유 ("SIGNAL", "STOP_LOSS")
        
    Returns:
        거래 결과 또는 None
    """
```

##### 피라미딩 관련
```python
def check_pyramid_signal(self, position: Position, current_price: float, 
                        atr: float) -> bool:
    """
    피라미딩 신호 확인
    
    Args:
        position: 기존 포지션
        current_price: 현재 가격
        atr: ATR 값
        
    Returns:
        피라미딩 가능 여부
    """
```

##### 포지션 관리
```python
def get_position(self, symbol: str) -> Optional[Position]:
    """포지션 조회"""

def has_position(self, symbol: str) -> bool:
    """포지션 보유 여부"""

def get_all_positions(self) -> Dict[str, Position]:
    """모든 포지션 조회"""

def get_trade_history(self) -> List[TradeResult]:
    """거래 이력 조회"""

def reset(self):
    """전략 초기화 (백테스트용)"""
```

### TurtleIndicators

터틀 전략에 사용되는 기술적 지표 계산 클래스입니다.

```python
class TurtleIndicators:
    """터틀 트레이딩 지표 계산"""
    
    @staticmethod
    def calculate_atr(price_data: List[PriceData], period: int = 20) -> float:
        """
        ATR (Average True Range) 계산
        
        Args:
            price_data: 가격 데이터 리스트
            period: 계산 기간 (기본값: 20)
            
        Returns:
            ATR 값
            
        Raises:
            ValueError: 데이터가 부족할 경우
            
        Example:
            >>> data = load_price_data("BTCUSDT", "2024-01-01", "2024-01-31")
            >>> atr = TurtleIndicators.calculate_atr(data, 20)
            >>> print(f"ATR: {atr:.2f}")
        """
    
    @staticmethod  
    def check_breakout(price_data: List[PriceData], period: int, direction: str) -> bool:
        """
        돌파 신호 확인
        
        Args:
            price_data: 가격 데이터
            period: 돌파 기간
            direction: 방향 ("LONG" 또는 "SHORT")
            
        Returns:
            돌파 여부
        """
    
    @staticmethod
    def calculate_donchian_high(price_data: List[PriceData], period: int) -> float:
        """돈치안 채널 상단 계산"""
    
    @staticmethod
    def calculate_donchian_low(price_data: List[PriceData], period: int) -> float:
        """돈치안 채널 하단 계산"""
```

---

## 백테스트 엔진 (Backtest Engine)

### BacktestEngine

백테스트 실행을 담당하는 메인 클래스입니다.

```python
class BacktestEngine:
    """백테스팅 엔진"""
    
    def __init__(self, config: BacktestConfig_):
        """
        백테스트 엔진 초기화
        
        Args:
            config: 백테스트 설정 객체
        """
    
    async def run_backtest(self) -> BacktestResults:
        """
        백테스트 실행
        
        Returns:
            백테스트 결과
            
        Raises:
            ValueError: 데이터가 부족할 경우
            
        Example:
            >>> config = BacktestConfig_(
            ...     symbol="BTCUSDT",
            ...     start_date="2023-01-01",
            ...     end_date="2024-12-31",
            ...     initial_balance=10000
            ... )
            >>> engine = BacktestEngine(config)
            >>> results = await engine.run_backtest()
            >>> print(f"Final balance: ${results.final_balance:,.2f}")
        """
    
    async def load_historical_data(self) -> List[PriceData]:
        """과거 데이터 로드"""
        
    def _calculate_portfolio_value(self, current_price: float) -> float:
        """포트폴리오 총 가치 계산"""
        
    def _apply_commission(self, trade_value: float):
        """수수료 적용"""
```

### BacktestResultsManager

백테스트 결과 저장 및 로드를 관리하는 유틸리티 클래스입니다.

```python
class BacktestResultsManager:
    """백테스트 결과 관리"""
    
    @staticmethod
    def save_results(results: BacktestResults, filename: str):
        """
        결과 저장
        
        Args:
            results: 백테스트 결과
            filename: 저장할 파일명 (확장자 제외)
            
        Example:
            >>> BacktestResultsManager.save_results(results, "my_backtest")
            # data/backtest_results/my_backtest.json 파일로 저장됨
        """
    
    @staticmethod
    def load_results(filename: str) -> Optional[Dict[str, Any]]:
        """
        결과 로드
        
        Args:
            filename: 로드할 파일명
            
        Returns:
            로드된 결과 딕셔너리 또는 None
        """
```

---

## 데이터 모델 (Data Models)

### PriceData

OHLCV 가격 데이터를 나타내는 데이터 클래스입니다.

```python
@dataclass
class PriceData:
    """OHLCV 가격 데이터"""
    symbol: str          # 종목 코드
    date: datetime       # 날짜/시간
    open: float         # 시가
    high: float         # 고가
    low: float          # 저가
    close: float        # 종가
    volume: float       # 거래량
    
    # Example:
    # price = PriceData(
    #     symbol="BTCUSDT",
    #     date=datetime(2024, 1, 15),
    #     open=50000.0,
    #     high=51000.0,
    #     low=49500.0,
    #     close=50500.0,
    #     volume=1000.0
    # )
```

### TradingUnit

개별 거래 유닛을 나타내는 데이터 클래스입니다.

```python
@dataclass
class TradingUnit:
    """터틀 거래 유닛"""
    entry_price: float      # 진입 가격
    entry_date: datetime    # 진입 날짜
    size: float            # 거래 수량
    stop_loss: float       # 손절가
    system: int            # 시스템 번호 (1 또는 2)
    unit_number: int       # 유닛 번호 (1-4)
```

### Position

포지션 정보를 나타내는 데이터 클래스입니다.

```python
@dataclass
class Position:
    """포지션 정보"""
    symbol: str                    # 종목 코드
    direction: str                 # 방향 ("LONG" 또는 "SHORT")
    units: List[TradingUnit]       # 거래 유닛 리스트
    total_size: float              # 총 거래량
    avg_price: float               # 평균 단가
    
    def add_unit(self, unit: TradingUnit):
        """
        유닛 추가 및 평균가 재계산
        
        Args:
            unit: 추가할 거래 유닛
        """
```

### TradeResult

완료된 거래의 결과를 나타내는 데이터 클래스입니다.

```python
@dataclass
class TradeResult:
    """거래 결과"""
    symbol: str          # 종목 코드
    direction: str       # 거래 방향
    entry_price: float   # 진입 가격
    exit_price: float    # 청산 가격
    size: float         # 거래 수량
    pnl: float          # 손익 (P&L)
    entry_date: datetime # 진입 날짜
    exit_date: datetime  # 청산 날짜
    system: int         # 시스템 번호
    exit_reason: str    # 청산 사유
```

### BacktestConfig_

백테스트 설정을 나타내는 데이터 클래스입니다.

```python
@dataclass
class BacktestConfig_:
    """백테스트 설정"""
    symbol: str = "BTCUSDT"              # 거래 종목
    start_date: str = "2023-01-01"       # 시작일
    end_date: str = "2024-12-31"         # 종료일
    timeframe: str = "1d"                # 타임프레임
    initial_balance: float = 10000.0     # 초기 자금
    commission_rate: float = 0.0004      # 수수료율
    systems: List[int] = None            # 사용할 시스템 [1, 2]
    
    def __post_init__(self):
        if self.systems is None:
            self.systems = [1, 2]
```

### PerformanceMetrics

성과 지표를 나타내는 데이터 클래스입니다.

```python
@dataclass
class PerformanceMetrics:
    """성과 지표"""
    total_return: float = 0.0            # 총 수익률
    annual_return: float = 0.0           # 연화 수익률
    max_drawdown: float = 0.0            # 최대 드로다운
    sharpe_ratio: float = 0.0            # 샤프 비율
    win_rate: float = 0.0                # 승률
    profit_factor: float = 0.0           # 수익 팩터
    avg_win: float = 0.0                 # 평균 수익
    avg_loss: float = 0.0                # 평균 손실
    max_consecutive_wins: int = 0        # 최대 연속 승
    max_consecutive_losses: int = 0      # 최대 연속 패
    total_trades: int = 0                # 총 거래 수
    long_trades: int = 0                 # 롱 거래 수
    short_trades: int = 0                # 숏 거래 수
    long_win_rate: float = 0.0           # 롱 승률
    short_win_rate: float = 0.0          # 숏 승률
```

---

## UI 컴포넌트 (UI Components)

### BacktestSetupUI

백테스트 설정 UI 클래스입니다.

```python
class BacktestSetupUI:
    """백테스트 설정 UI"""
    
    def show_setup_screen(self) -> Dict[str, Any]:
        """
        백테스트 설정 화면 표시
        
        Returns:
            사용자가 설정한 백테스트 구성 딕셔너리 또는 None (취소 시)
            
        Example:
            >>> setup_ui = BacktestSetupUI()
            >>> config = setup_ui.show_setup_screen()
            >>> if config:
            ...     print(f"Selected timeframe: {config['timeframe']}")
        """
```

### BacktestResultsUI

백테스트 결과 표시 UI 클래스입니다.

```python
class BacktestResultsUI:
    """백테스트 결과 표시 UI"""
    
    def display_results(self, results: BacktestResults) -> str:
        """
        백테스트 결과 표시
        
        Args:
            results: 백테스트 결과 객체
            
        Returns:
            사용자가 선택한 액션 번호
        """
    
    def show_detailed_analysis(self, results: BacktestResults):
        """상세 분석 표시"""
        
    def show_all_trades(self, results: BacktestResults):
        """전체 거래 내역 표시"""
        
    def export_results(self, results: BacktestResults):
        """결과 내보내기 (CSV, JSON)"""
```

### TradingDashboard

실시간 트레이딩 대시보드 클래스입니다.

```python
class TradingDashboard:
    """실시간 트레이딩 대시보드"""
    
    def __init__(self, mode: str = "paper", initial_balance: float = 10000.0):
        """
        대시보드 초기화
        
        Args:
            mode: 거래 모드 ("paper", "live", "backtest")
            initial_balance: 초기 자금
        """
    
    async def start(self):
        """
        대시보드 시작
        
        실시간 업데이트되는 대시보드를 표시합니다.
        Ctrl+C로 중단할 수 있습니다.
        """
    
    def stop(self):
        """대시보드 중지"""
```

---

## Binance API 관리자

### BinanceManager

Binance API 연동을 담당하는 클래스입니다.

```python
class BinanceManager:
    """Binance API 관리자"""
    
    def __init__(self, mode: str = "paper"):
        """
        초기화
        
        Args:
            mode: 모드 ("live", "paper", "backtest")
        """
    
    async def get_historical_klines(self, symbol: str, interval: str, 
                                  start_time: str, end_time: str = None, 
                                  limit: int = 1000) -> List[PriceData]:
        """
        과거 캔들 데이터 조회
        
        Args:
            symbol: 종목 (예: "BTCUSDT")
            interval: 간격 ("1m", "5m", "1h", "1d" 등)
            start_time: 시작 시간
            end_time: 종료 시간 (선택사항)
            limit: 최대 개수
            
        Returns:
            PriceData 리스트
        """
    
    async def get_current_price(self, symbol: str) -> float:
        """현재 가격 조회"""
    
    async def place_order(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """주문 실행"""
    
    async def get_account_info(self) -> Dict[str, Any]:
        """계좌 정보 조회"""
```

### HistoricalDataManager

과거 데이터 관리 클래스입니다.

```python
class HistoricalDataManager:
    """과거 데이터 관리자"""
    
    def __init__(self, binance_manager: BinanceManager):
        """초기화"""
    
    async def get_price_data(self, symbol: str, interval: str, 
                           start_date: str, end_date: str = None) -> List[PriceData]:
        """
        과거 가격 데이터 조회 (캐시 포함)
        
        Args:
            symbol: 종목
            interval: 간격
            start_date: 시작일
            end_date: 종료일
            
        Returns:
            가격 데이터 리스트
        """
    
    def save_to_csv(self, data: List[PriceData], filename: str):
        """CSV 파일로 저장"""
    
    def load_from_csv(self, filename: str) -> List[PriceData]:
        """CSV 파일에서 로드"""
```

### PaperTradingEngine

가상매매 엔진 클래스입니다.

```python
class PaperTradingEngine:
    """가상매매 엔진"""
    
    def __init__(self, initial_balance: float = 10000.0):
        """
        초기화
        
        Args:
            initial_balance: 초기 자금
        """
    
    async def place_order(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """가상 주문 실행"""
    
    def get_portfolio_value(self, current_prices: Dict[str, float]) -> float:
        """포트폴리오 총 가치 계산"""
    
    def get_account_summary(self) -> Dict[str, Any]:
        """계좌 요약 정보"""
```

---

## 설정 및 유틸리티

### 설정 클래스들

#### TradingConfig
```python
class TradingConfig:
    """터틀 트레이딩 전략 설정"""
    
    # 핵심 상수 (변경 금지)
    RISK_PER_TRADE = 0.01        # 거래당 리스크 (1%)
    MAX_RISK_TOTAL = 0.20        # 총 최대 리스크 (20%)
    ATR_PERIOD = 20              # ATR 계산 기간
    MAX_UNITS_PER_MARKET = 4     # 종목당 최대 유닛
    MAX_UNITS_DIRECTIONAL = 12   # 방향별 최대 유닛
    MAX_UNITS_CORRELATED = 6     # 연관 시장 최대 유닛
    STOP_LOSS_MULTIPLIER = 2.0   # 손절가: 2N
    PYRAMID_MULTIPLIER = 0.5     # 피라미딩: 0.5N
    
    # 시스템 설정
    SYSTEM_1 = {
        'ENTRY_PERIOD': 20,      # 진입: 20일 돌파
        'EXIT_PERIOD': 10,       # 청산: 10일 돌파
        'USE_FILTER': True       # 이전 거래 필터 사용
    }
    
    SYSTEM_2 = {
        'ENTRY_PERIOD': 55,      # 진입: 55일 돌파
        'EXIT_PERIOD': 20,       # 청산: 20일 돌파
        'USE_FILTER': False      # 이전 거래 필터 미사용
    }
```

#### BacktestConfig
```python
class BacktestConfig:
    """백테스팅 관련 설정"""
    
    DEFAULT_TIMEFRAMES = ['1m', '5m', '15m', '1h', '4h', '1d', '1w', '1M']
    DEFAULT_TIMEFRAME = '1d'
    DEFAULT_INITIAL_BALANCE = 10000.0
    DEFAULT_COMMISSION_RATE = 0.0004
    
    CACHE_ENABLED = True
    CACHE_DAYS = 7
    
    BENCHMARK_SYMBOL = 'BTCUSDT'
    RISK_FREE_RATE = 0.02
```

#### BinanceConfig
```python
class BinanceConfig:
    """Binance API 설정"""
    
    API_KEY = os.getenv('BINANCE_API_KEY', '')
    SECRET_KEY = os.getenv('BINANCE_SECRET_KEY', '')
    TESTNET = os.getenv('BINANCE_TESTNET', 'True').lower() == 'true'
    
    REQUESTS_PER_MINUTE = 1200
    ORDERS_PER_SECOND = 10
    ORDERS_PER_DAY = 200000
    
    WEBSOCKET_TIMEOUT = 60
    RECONNECT_ATTEMPTS = 5
```

### 유틸리티 함수들

#### 설정 관련
```python
def get_config() -> Dict[str, Any]:
    """전체 설정을 딕셔너리로 반환"""

def validate_config():
    """설정 유효성 검증"""
```

#### 컬러 및 포맷팅
```python
class UIConfig:
    """터미널 UI 설정"""
    
    COLORS = {
        'profit': 'green',
        'loss': 'red',
        'neutral': 'white',
        'warning': 'yellow',
        'info': 'blue',
        'header': 'cyan'
    }
    
    DASHBOARD_REFRESH_RATE = 1.0
    MIN_TERMINAL_WIDTH = 120
    MIN_TERMINAL_HEIGHT = 30
```

---

## 사용 예제

### 기본 사용법

#### 1. 백테스트 실행
```python
import asyncio
from .backend.engines.backtest_engine import BacktestEngine, BacktestConfig_

async def run_simple_backtest():
    config = BacktestConfig_(
        symbol="BTCUSDT",
        start_date="2023-01-01",
        end_date="2024-12-31",
        timeframe="1d",
        initial_balance=10000,
        systems=[1, 2]
    )
    
    engine = BacktestEngine(config)
    results = await engine.run_backtest()
    
    print(f"Total Return: {results.metrics.total_return:.2%}")
    print(f"Win Rate: {results.metrics.win_rate:.2%}")
    print(f"Max Drawdown: {results.metrics.max_drawdown:.2%}")

asyncio.run(run_simple_backtest())
```

#### 2. 터틀 전략 사용
```python
from strategy.turtle_strategy import TurtleStrategy, PriceData
from datetime import datetime

strategy = TurtleStrategy()

# 샘플 데이터 생성
price_data = [
    PriceData("BTCUSDT", datetime(2024, 1, i), 50000+i*100, 51000+i*100, 49000+i*100, 50500+i*100, 1000)
    for i in range(1, 61)  # 60일 데이터
]

# ATR 계산
atr = strategy.indicators.calculate_atr(price_data)
print(f"ATR: {atr:.2f}")

# 진입 신호 확인
signal = strategy.check_entry_signal("BTCUSDT", price_data, 1, "LONG")
print(f"Entry signal: {signal}")

# 유닛 사이즈 계산
unit_size = strategy.calculate_unit_size("BTCUSDT", 10000, atr, 50000)
print(f"Unit size: {unit_size:.4f}")
```

#### 3. 가상매매 시작
```python
import asyncio
from frontend.dashboard.main_dashboard import TradingDashboard

async def start_paper_trading():
    dashboard = TradingDashboard(mode="paper", initial_balance=10000)
    await dashboard.start()

# 실행 (Ctrl+C로 중지)
asyncio.run(start_paper_trading())
```

### 고급 사용법

#### 1. 커스텀 지표 추가
```python
from strategy.turtle_strategy import TurtleIndicators

class CustomIndicators(TurtleIndicators):
    @staticmethod
    def calculate_rsi(price_data: List[PriceData], period: int = 14) -> float:
        """RSI 계산 (예시)"""
        # RSI 계산 로직 구현
        pass
```

#### 2. 백테스트 결과 분석
```python
from .backend.engines.backtest_engine import BacktestResultsManager

# 결과 로드
results_data = BacktestResultsManager.load_results("my_backtest")

if results_data:
    trades = results_data['trades']
    for trade in trades:
        print(f"Trade: {trade['symbol']} {trade['direction']} "
              f"P&L: {trade['pnl']:.2f}")
```

---

## 오류 처리

### 일반적인 예외

```python
# 설정 오류
try:
    validate_config()
except ValueError as e:
    print(f"Configuration error: {e}")

# API 연결 오류
try:
    price = await binance_manager.get_current_price("BTCUSDT")
except ConnectionError as e:
    print(f"API connection failed: {e}")

# 데이터 부족 오류
try:
    atr = TurtleIndicators.calculate_atr(price_data, 20)
except ValueError as e:
    print(f"Insufficient data: {e}")
```

### 백테스트 관련 오류

```python
try:
    results = await engine.run_backtest()
except ValueError as e:
    if "최소 60일" in str(e):
        print("백테스트 기간이 너무 짧습니다. 최소 60일 이상 필요합니다.")
    else:
        print(f"백테스트 오류: {e}")
```

---

이 API 레퍼런스는 Bitcoin Futures Turtle Trading Bot의 모든 주요 클래스와 메서드에 대한 상세한 정보를 제공합니다. 각 함수의 매개변수, 반환값, 예외 처리 방법을 포함하여 개발자가 시스템을 효과적으로 활용할 수 있도록 도와줍니다.
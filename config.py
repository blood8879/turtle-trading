"""
Bitcoin Futures Turtle Trading Bot - Configuration
모든 시스템 설정과 상수들을 관리하는 중앙 설정 파일
"""

import os
from dotenv import load_dotenv
from typing import Dict, Any

# 환경변수 로드
load_dotenv()

class TradingConfig:
    """터틀 트레이딩 전략 설정"""
    
    # 터틀 트레이딩 핵심 상수 (변경 금지)
    RISK_PER_TRADE = 0.01        # 거래당 리스크 (1%)
    MAX_RISK_TOTAL = 0.20        # 총 최대 리스크 (20%)
    ATR_PERIOD = 20              # ATR 계산 기간 (기본값)
    MAX_UNITS_PER_MARKET = 4     # 종목당 최대 유닛
    MAX_UNITS_DIRECTIONAL = 12   # 방향별 최대 유닛 (롱/숏)
    MAX_UNITS_CORRELATED = 6     # 연관 시장 최대 유닛
    STOP_LOSS_MULTIPLIER = 2.0   # 손절가: 2N
    PYRAMID_MULTIPLIER = 0.5     # 피라미딩: 0.5N마다
    
    # 시간프레임별 ATR 계산 기간 설정
    ATR_PERIODS = {
        '1m': 60,      # 1시간 = 60분 (실시간 반응성)
        '5m': 48,      # 4시간 = 48 * 5분 (단기 변동성)
        '15m': 32,     # 8시간 = 32 * 15분 (중기 변동성)
        '1h': 24,      # 24시간 = 24 * 1시간 (일중 변동성)
        '4h': 12,      # 48시간 = 12 * 4시간 (2일 변동성)
        '1d': 20,      # 20일 (기본 터틀 설정)
        '1w': 20       # 20주 (장기 변동성)
    }
    
    # 시간프레임별 브레이크아웃 기간 배수
    TIMEFRAME_MULTIPLIERS = {
        '1m': 20,      # 1분봉: 20분 (단기 스캘핑용)
        '5m': 12,      # 5분봉: 60분 (1시간)  
        '15m': 8,      # 15분봉: 120분 (2시간)
        '1h': 6,       # 1시간봉: 6시간
        '4h': 2,       # 4시간봉: 8시간
        '1d': 1,       # 일봉: 기본 기간
        '1w': 1        # 주봉: 기본 기간
    }
    
    @classmethod
    def get_atr_period(cls, timeframe: str = '1d') -> int:
        """시간프레임에 맞는 ATR 기간 반환"""
        return cls.ATR_PERIODS.get(timeframe, cls.ATR_PERIOD)
    
    @classmethod
    def get_timeframe_multiplier(cls, timeframe: str = '1d') -> int:
        """시간프레임에 맞는 브레이크아웃 기간 배수 반환"""
        return cls.TIMEFRAME_MULTIPLIERS.get(timeframe, 1)
    
    # 레버리지 설정
    DEFAULT_LEVERAGE = 1.0       # 기본 레버리지 (현물)
    MAX_LEVERAGE = 125.0         # 최대 레버리지
    MIN_LEVERAGE = 1.0           # 최소 레버리지
    MARGIN_RATIO_THRESHOLD = 0.8 # 마진 비율 임계값 (80%)
    
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

class BacktestConfig:
    """백테스팅 관련 설정"""
    
    def __init__(self, symbol='BTCUSDT', start_date='2023-01-01', end_date='2024-12-31', 
                 timeframe='1d', initial_balance=10000.0, commission_rate=0.0004, systems=None,
                 leverage=1.0):
        self.symbol = symbol
        self.start_date = start_date
        self.end_date = end_date
        self.timeframe = timeframe
        self.initial_balance = initial_balance
        self.commission_rate = commission_rate
        self.systems = systems or [1, 2]
        self.leverage = max(TradingConfig.MIN_LEVERAGE, min(leverage, TradingConfig.MAX_LEVERAGE))
    
    DEFAULT_TIMEFRAMES = ['1m', '5m', '15m', '1h', '4h', '1d', '1w', '1M']
    DEFAULT_TIMEFRAME = '1d'
    DEFAULT_INITIAL_BALANCE = 10000.0
    DEFAULT_COMMISSION_RATE = 0.0004  # Binance 수수료 0.04%
    
    # 백테스트 데이터 캐시 설정
    CACHE_ENABLED = True
    CACHE_DAYS = 7  # 7일간 캐시 유지
    
    # 성과 지표 계산 설정
    BENCHMARK_SYMBOL = 'BTCUSDT'
    RISK_FREE_RATE = 0.02  # 2% 무위험 수익률

class BinanceConfig:
    """Binance API 설정 (.backend에서 사용)"""
    
    API_KEY = os.getenv('BINANCE_API_KEY', '')
    SECRET_KEY = os.getenv('BINANCE_SECRET_KEY', '')
    TESTNET = os.getenv('BINANCE_TESTNET', 'True').lower() == 'true'
    
    # API 제한 설정
    REQUESTS_PER_MINUTE = 1200
    ORDERS_PER_SECOND = 10
    ORDERS_PER_DAY = 200000
    
    # WebSocket 설정
    WEBSOCKET_TIMEOUT = 60
    RECONNECT_ATTEMPTS = 5

class UIConfig:
    """터미널 UI 설정"""
    
    # 컬러 스키마
    COLORS = {
        'profit': 'green',
        'loss': 'red',
        'neutral': 'white',
        'warning': 'yellow',
        'info': 'blue',
        'header': 'cyan'
    }
    
    # 대시보드 새로고침 간격 (초)
    DASHBOARD_REFRESH_RATE = 1.0
    
    # 화면 크기 설정
    MIN_TERMINAL_WIDTH = 120
    MIN_TERMINAL_HEIGHT = 30

class DataConfig:
    """데이터 관리 설정"""
    
    # 데이터 디렉토리
    DATA_DIR = 'data'
    HISTORICAL_DIR = f'{DATA_DIR}/historical'
    BACKTEST_RESULTS_DIR = f'{DATA_DIR}/backtest_results'
    LIVE_TRADING_DIR = f'{DATA_DIR}/live_trading'
    LOGS_DIR = 'logs'
    
    # 매매일지 디렉토리
    TRADE_JOURNAL_DIR = f'{DATA_DIR}/trade_journals'
    PAPER_TRADING_JOURNAL_DIR = f'{TRADE_JOURNAL_DIR}/paper_trading'
    LIVE_TRADING_JOURNAL_DIR = f'{TRADE_JOURNAL_DIR}/live_trading'
    BACKTEST_JOURNAL_DIR = f'{TRADE_JOURNAL_DIR}/backtest'
    
    # 파일 형식
    HISTORICAL_DATA_FORMAT = 'csv'
    BACKTEST_RESULTS_FORMAT = 'json'
    TRADE_JOURNAL_FORMAT = 'csv'
    
    # 데이터 보관 기간
    HISTORICAL_DATA_RETENTION_DAYS = 365
    BACKTEST_RESULTS_RETENTION_DAYS = 90
    LOG_RETENTION_DAYS = 30
    TRADE_JOURNAL_RETENTION_DAYS = 365

class TradingMode:
    """거래 모드 설정"""
    
    BACKTEST = 'backtest'
    PAPER = 'paper' 
    LIVE = 'live'
    
    # 기본 모드
    DEFAULT_MODE = BACKTEST

class LoggingConfig:
    """로깅 설정"""
    
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # 로그 파일들
    MAIN_LOG_FILE = f'{DataConfig.LOGS_DIR}/trading.log'
    BACKTEST_LOG_FILE = f'{DataConfig.LOGS_DIR}/backtest.log'
    ERROR_LOG_FILE = f'{DataConfig.LOGS_DIR}/error.log'
    TRADE_LOG_FILE = f'{DataConfig.LOGS_DIR}/trades.log'
    
    # 매매일지 로그 파일들
    PAPER_TRADE_JOURNAL_LOG = f'{DataConfig.LOGS_DIR}/paper_trade_journal.log'
    LIVE_TRADE_JOURNAL_LOG = f'{DataConfig.LOGS_DIR}/live_trade_journal.log'
    BACKTEST_JOURNAL_LOG = f'{DataConfig.LOGS_DIR}/backtest_journal.log'

def get_config() -> Dict[str, Any]:
    """전체 설정을 딕셔너리로 반환"""
    return {
        'trading': TradingConfig,
        'backtest': BacktestConfig, 
        'binance': BinanceConfig,
        'ui': UIConfig,
        'data': DataConfig,
        'logging': LoggingConfig
    }

def validate_config():
    """설정 유효성 검증"""
    errors = []
    
    # Binance API 키 검증 (실제 거래 시)
    trading_mode = os.getenv('TRADING_MODE', TradingMode.DEFAULT_MODE)
    if trading_mode == TradingMode.LIVE:
        if not BinanceConfig.API_KEY:
            errors.append("BINANCE_API_KEY가 설정되지 않았습니다.")
        if not BinanceConfig.SECRET_KEY:
            errors.append("BINANCE_SECRET_KEY가 설정되지 않았습니다.")
    
    # 디렉토리 생성
    os.makedirs(DataConfig.HISTORICAL_DIR, exist_ok=True)
    os.makedirs(DataConfig.BACKTEST_RESULTS_DIR, exist_ok=True)
    os.makedirs(DataConfig.LIVE_TRADING_DIR, exist_ok=True)
    os.makedirs(DataConfig.LOGS_DIR, exist_ok=True)
    
    # 매매일지 디렉토리 생성
    os.makedirs(DataConfig.TRADE_JOURNAL_DIR, exist_ok=True)
    os.makedirs(DataConfig.PAPER_TRADING_JOURNAL_DIR, exist_ok=True)
    os.makedirs(DataConfig.LIVE_TRADING_JOURNAL_DIR, exist_ok=True)
    os.makedirs(DataConfig.BACKTEST_JOURNAL_DIR, exist_ok=True)
    
    if errors:
        raise ValueError("설정 오류:\n" + "\n".join(errors))
    
    return True

if __name__ == "__main__":
    try:
        validate_config()
        print("✅ 모든 설정이 유효합니다.")
    except ValueError as e:
        print(f"❌ 설정 오류: {e}")
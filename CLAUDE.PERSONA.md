# 비트코인 선물 터틀 트레이딩 자동매매 시스템 - 역할별 요구사항

## Product Manager

### 제품 개요
- **제품명**: Bitcoin Futures Turtle Trading Bot
- **목표**: 터틀 트레이딩 전략을 활용한 비트코인 선물 자동매매 시스템
- **플랫폼**: Binance Futures API 기반 Python 애플리케이션

### 핵심 기능 요구사항
1. **백테스팅 시스템**
   - 특정 기간 선택 (시작일 ~ 종료일)
   - 다양한 타임프레임 (1m, 5m, 15m, 1h, 4h, 1d, 1w, 1M)
   - 실제 비트코인 과거 데이터 기반 검증
   - 상세한 백테스트 결과 리포트 생성

2. **매매 모드 선택**
   - 백테스트: 과거 데이터 기반 전략 검증
   - 실제매매: Binance 실계좌 연동
   - 가상매매: 시뮬레이션 모드 (시작 자금 설정 가능)

3. **터틀 트레이딩 전략 구현**
   - 시스템 1: 20일 돌파 전략
   - 시스템 2: 55일 돌파 전략
   - ATR 기반 포지션 사이징
   - 피라미딩 (최대 4유닛)
   - 2N 손절매

4. **실시간 모니터링**
   - 터미널 기반 대시보드
   - 실시간 포지션 현황
   - 성과 지표 추적

### 비즈니스 요구사항
- 백테스팅을 통한 전략 검증 후 실전 적용
- 24/7 무인 운영 가능
- 안전한 리스크 관리
- 투명한 매매 기록
- 백테스팅 결과와의 비교 분석

### 성공 지표 (KPI)
- 백테스트 정확도: 99% 이상
- 시스템 가동률: 99% 이상
- 주문 실행 성공률: 95% 이상
- 데이터 정확도: 99.9% 이상
- 최대 드로다운: 20% 이하

---

## UX/UI Designer

### 사용자 경험 설계
**주요 사용자**: 개인 투자자, 퀀트 트레이더

### 터미널 인터페이스 설계
1. **메인 메뉴 화면**
   ```
   ┌───────────────── Bitcoin Futures Turtle Trading Bot ─────────────────┐
   │                           MAIN MENU                                │
   ├─────────────────────────────────────────────────────────────────────┤
   │ 1. 백테스트 실행                                              │
   │ 2. 가상매매 시작                                             │
   │ 3. 실제매매 시작                                             │
   │ 4. 이전 결과 보기                                              │
   │ 5. 설정                                                     │
   │ 6. 종료                                                     │
   ├─────────────────────────────────────────────────────────────────────┤
   │ 메뉴 선택 (1-6): _                                               │
   └─────────────────────────────────────────────────────────────────────┘
   ```

2. **백테스트 설정 화면**
   ```
   ┌───────────────────── BACKTEST SETUP ─────────────────────┐
   │                                                         │
   │ 기간 설정:                                               │
   │   시작일: 2023-01-01                                     │
   │   종료일: 2024-12-31                                     │
   │                                                         │
   │ 타임프레임: 1d (일봉)                                      │
   │   옵션: 1m, 5m, 15m, 1h, 4h, 1d, 1w, 1M                │
   │                                                         │
   │ 초기 자금: $10,000                                        │
   │                                                         │
   │ 전략 설정:                                                │
   │   시스템 1: 활성화 (20일 돌파)                             │
   │   시스템 2: 활성화 (55일 돌파)                             │
   │                                                         │
   ├─────────────────────────────────────────────────────────┤
   │ [Enter] 백테스트 시작 | [ESC] 메인 메뉴로                   │
   └─────────────────────────────────────────────────────────┘
   ```

3. **백테스트 결과 화면**
   ```
   ┌─────────── BACKTEST RESULTS (2023-01-01 ~ 2024-12-31) ────────────┐
   │                                                                 │
   │ ███ 전체 성과 요약 ███                                          │
   │ 초기 자금: $10,000  →  최종 자금: $15,847                    │
   │ 총 수익률: +58.47%  |  연화 수익률: +24.3%                     │
   │ 최대 드로다운: -12.8%  |  샤프 비율: 1.67                     │
   │                                                                 │
   │ ███ 거래 통계 ███                                             │
   │ 총 거래 수: 156번  |  승률: 67.3%                              │
   │ 롱 거래: 89번 (승률 71.9%)  |  숏 거래: 67번 (승률 61.2%)      │
   │ 평균 수익: +$125  |  평균 손실: -$67                           │
   │ 최대 연속 승: 8번  |  최대 연속 패: 4번                     │
   │                                                                 │
   │ ███ 월별 수익률 ███                                          │
   │ 2023: +18.5% | 2024: +33.7%                                 │
   │ 최고 월: +8.2% (2024-03) | 최악 월: -5.1% (2023-11)             │
   ├─────────────────────────────────────────────────────────────────┤
   │ [S] 결과 저장 | [D] 상세 분석 | [ESC] 돌아가기                       │
   └─────────────────────────────────────────────────────────────────┘
   ```

4. **라이브 트레이딩 대시보드**
   ```
   ┌─────────────────── Bitcoin Futures Turtle Trading Bot ───────────────────┐
   │ Mode: [LIVE/PAPER] | Status: [RUNNING/STOPPED] | Time: 2025-06-12 14:30:05 │
   ├─────────────────────────────────────────────────────────────────────────────┤
   │ ACCOUNT SUMMARY                    │ CURRENT POSITIONS                    │
   │ • Balance: $10,000                 │ • BTC-USDT: LONG 0.5 BTC            │
   │ • P&L: +$1,250 (+12.5%)           │   Entry: $65,000 | Current: $67,500  │
   │ • Available: $8,750                │   P&L: +$1,250 (+3.8%)              │
   │ • Margin Used: $1,250              │ • ETH-USDT: None                     │
   ├─────────────────────────────────────────────────────────────────────────────┤
   │ PERFORMANCE METRICS                                                       │
   │ Win Rate (Total): 65% | Long: 70% | Short: 60%                          │
   │ Total Trades: 48 | Profit Factor: 1.8 | Sharpe: 1.2                    │
   │ Max Drawdown: -8.5% | Current Drawdown: -2.1%                           │
   ├─────────────────────────────────────────────────────────────────────────────┤
   │ RECENT TRADES (Last 5)                                                   │
   │ 1. BTC LONG  | Entry: $64,500 | Exit: $66,200 | P&L: +$850 | 06-11     │
   │ 2. BTC SHORT | Entry: $63,800 | Exit: $63,200 | P&L: +$600 | 06-10     │
   │ 3. BTC LONG  | Entry: $62,100 | Exit: $61,900 | P&L: -$200 | 06-09     │
   └─────────────────────────────────────────────────────────────────────────────┘
   ```

5. **컬러 스키마**
   - 수익: 녹색 (Green)
   - 손실: 빨간색 (Red)  
   - 중립: 흰색/회색 (White/Gray)
   - 경고: 노란색 (Yellow)
   - 중요: 파란색 (Blue)

6. **인터랙션 플로우**
   - 프로그램 시작 → 메뉴 선택 → 백테스트/실행 → 결과 확인
   - 키보드 단축키: q(종료), p(일시정지), r(재시작), s(설정)

### 사용성 원칙
- 백테스트 우선 워크플로우
- 한눈에 파악 가능한 정보 배치
- 실시간 업데이트 (1초 간격)
- 명확한 상태 표시
- 최소한의 사용자 개입

---

## Frontend Developer

### 기술 스택
- **언어**: Python 3.9+
- **터미널 UI**: Rich 또는 Textual 라이브러리
- **실시간 업데이트**: asyncio
- **차트 라이브러리**: matplotlib (백테스트 결과용)

### 구현 요구사항

1. **메뉴 시스템**
   ```python
   class MenuSystem:
       def __init__(self):
           self.console = Console()
           
       def show_main_menu(self):
           # 메인 메뉴 표시
           
       def show_backtest_setup(self):
           # 백테스트 설정 화면
           
       def show_backtest_results(self, results):
           # 백테스트 결과 화면
   ```

2. **백테스트 UI 컴포넌트**
   ```python
   class BacktestUI:
       def __init__(self):
           self.setup_panel = BacktestSetupPanel()
           self.results_panel = BacktestResultsPanel()
           
       def get_backtest_config(self):
           # 사용자로부터 백테스트 설정 받기
           return {
               'start_date': '2023-01-01',
               'end_date': '2024-12-31',
               'timeframe': '1d',
               'initial_balance': 10000
           }
           
       def show_progress(self, current, total):
           # 백테스트 진행률 표시
           
       def display_results(self, backtest_results):
           # 결과 표시 및 저장/분석 옵션
   ```

3. **실시간 대시보드 컴포넌트**
   ```python
   class TradingDashboard:
       def __init__(self):
           self.console = Console()
           self.layout = Layout()
           
       def create_header_panel(self):
           # 모드, 상태, 시간 표시
           
       def create_account_panel(self):
           # 계좌 정보 (잔고, P&L, 여유자금)
           
       def create_position_panel(self):
           # 현재 포지션 정보
           
       def create_metrics_panel(self):
           # 성과 지표
           
       def create_trades_panel(self):
           # 최근 거래 내역
   ```

4. **실시간 데이터 표시**
   ```python
   async def update_dashboard():
       while True:
           # 1초마다 데이터 업데이트
           await asyncio.sleep(1)
           refresh_display()
   ```

5. **키보드 입력 처리**
   ```python
   def handle_keyboard_input():
       # 메뉴 네비게이션
       # 백테스트 설정
       # 대시보드 제어
   ```

### 추가 대시보드 지표
기존 요구사항에 추가할 지표들:
11. 일일 P&L
12. 월간 P&L  
13. 현재 드로다운
14. 최대 드로다운
15. Sharpe Ratio
16. Profit Factor
17. 평균 보유시간
18. 최대 연속 승/패
19. ATR 값 (현재)
20. 다음 피라미드 레벨
21. 백테스트 대비 실제 성과

### 파일 구조
```
frontend/
├── __init__.py
├── main_menu.py
├── backtest/
│   ├── setup_ui.py
│   ├── results_ui.py
│   └── progress_ui.py
├── dashboard/
│   ├── main_dashboard.py
│   ├── components/
│   │   ├── header.py
│   │   ├── account.py
│   │   ├── positions.py
│   │   ├── metrics.py
│   │   └── trades.py
│   └── utils/
│       ├── formatting.py
│       └── colors.py
└── keyboard_handler.py
```

---

## Backend Developer

### 시스템 아키텍처
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Dashboard     │◄───┤  Trading Core   │◄───┤  Binance API    │
│   (Frontend)    │    │   (Backend)     │    │   (External)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   Data Store    │
                       │ (JSON/SQLite)   │
                       └─────────────────┘
                              ▲
                       ┌─────────────────┐
                       │ Backtest Engine │
                       │ (Historical)    │
                       └─────────────────┘
```

### 핵심 모듈 구현

1. **BacktestEngine** (새로 추가)
   ```python
   class BacktestEngine:
       def __init__(self, config):
           self.start_date = config['start_date']
           self.end_date = config['end_date']
           self.timeframe = config['timeframe']
           self.initial_balance = config['initial_balance']
           self.strategy = TurtleStrategy()
           
       async def run_backtest(self):
           # 백테스트 실행 메인 루프
           historical_data = await self.load_historical_data()
           results = await self.simulate_trading(historical_data)
           return self.generate_report(results)
           
       async def load_historical_data(self):
           # Binance에서 과거 데이터 로드
           
       async def simulate_trading(self, data):
           # 과거 데이터로 터틀 전략 시뮬레이션
           
       def generate_report(self, results):
           # 백테스트 결과 리포트 생성
   ```

2. **TurtleTradingEngine** 
   ```python
   class TurtleTradingEngine:
       def __init__(self, mode="paper"):
           self.mode = mode  # "backtest", "live", or "paper"
           self.account_manager = AccountManager(mode)
           self.strategy = TurtleStrategy()
           self.risk_manager = RiskManager()
           
       async def run(self):
           # 메인 트레이딩 루프
           
       def calculate_signals(self):
           # 터틀 시그널 계산
           
       def execute_trade(self, signal):
           # 매매 실행 (실제/가상/백테스트)
   ```

3. **HistoricalDataManager** (새로 추가)
   ```python
   class HistoricalDataManager:
       def __init__(self):
           self.cache = {}
           self.binance_client = BinanceClient()
           
       async def get_klines(self, symbol, interval, start_time, end_time):
           # 특정 기간의 캔들 데이터 조회
           
       def cache_data(self, symbol, interval, data):
           # 데이터 캐싱으로 속도 향상
           
       def validate_data(self, data):
           # 데이터 무결성 검증
   ```

4. **BinanceManager**
   ```python
   class BinanceManager:
       def __init__(self, mode="paper"):
           if mode == "live":
               self.client = Client(api_key, secret_key)
           elif mode == "backtest":
               self.client = HistoricalDataClient()
           else:
               self.client = PaperTradingClient()
               
       async def get_historical_klines(self, symbol, interval, start, end):
           # 과거 캔들 데이터 조회 (백테스트용)
           
       async def get_klines(self, symbol, interval, limit):
           # 실시간 캔들 데이터 조회
           
       async def place_order(self, order_data):
           # 주문 실행
           
       async def get_account_info(self):
           # 계좌 정보 조회
   ```

5. **BacktestResults** (새로 추가)
   ```python
   class BacktestResults:
       def __init__(self):
           self.trades = []
           self.equity_curve = []
           self.metrics = {}
           
       def calculate_metrics(self):
           # 모든 성과 지표 계산
           self.metrics = {
               'total_return': self.calculate_total_return(),
               'annual_return': self.calculate_annual_return(),
               'max_drawdown': self.calculate_max_drawdown(),
               'sharpe_ratio': self.calculate_sharpe_ratio(),
               'win_rate': self.calculate_win_rate(),
               'profit_factor': self.calculate_profit_factor(),
               'avg_win': self.calculate_avg_win(),
               'avg_loss': self.calculate_avg_loss(),
               'max_consecutive_wins': self.calculate_max_consecutive_wins(),
               'max_consecutive_losses': self.calculate_max_consecutive_losses()
           }
           
       def export_to_csv(self):
           # 결과를 CSV로 내보내기
           
       def export_to_json(self):
           # 결과를 JSON으로 내보내기
   ```

6. **PaperTradingEngine**
   ```python
   class PaperTradingEngine:
       def __init__(self, initial_balance=10000):
           self.balance = initial_balance
           self.positions = {}
           self.trade_history = []
           
       def simulate_order(self, order):
           # 가상 주문 실행
           
       def update_positions(self, current_prices):
           # 포지션 평가액 업데이트
   ```

### API 통합
1. **Binance Futures API 연동**
   - 실시간 가격: WebSocket 스트림
   - 과거 데이터: REST API (Klines endpoint)
   - 주문 관리: REST API
   - 에러 핸들링 및 재시도 로직

2. **데이터 구조**
   ```python
   # 백테스트 설정
   backtest_config = {
       "symbol": "BTCUSDT",
       "start_date": "2023-01-01",
       "end_date": "2024-12-31",
       "timeframe": "1d",
       "initial_balance": 10000,
       "systems": [1, 2],  # 활성화할 시스템
       "commission": 0.0004  # 수수료
   }
   
   # 거래 기록
   trade_record = {
       "id": uuid4(),
       "symbol": "BTCUSDT",
       "side": "LONG",
       "entry_price": 65000,
       "exit_price": 67000,
       "quantity": 0.1,
       "pnl": 200,
       "entry_time": datetime.now(),
       "exit_time": datetime.now(),
       "system": 1,  # 1 or 2
       "unit_number": 1,  # 1-4
       "mode": "backtest"  # backtest, paper, live
   }
   ```

### 백엔드 파일 구조
```
backend/
├── __init__.py
├── main.py
├── engines/
│   ├── turtle_engine.py
│   ├── backtest_engine.py
│   ├── paper_trading.py
│   └── risk_manager.py
├── strategy/
│   ├── turtle_strategy.py
│   ├── indicators.py
│   └── signals.py
├── api/
│   ├── binance_manager.py
│   ├── historical_data.py
│   └── websocket_client.py
├── data/
│   ├── data_manager.py
│   ├── backtest_results.py
│   └── models.py
└── utils/
    ├── config.py
    ├── logger.py
    └── helpers.py
```

---

## DevOps Engineer

### 인프라 요구사항
1. **서버 환경**
   - OS: Ubuntu 20.04 LTS
   - Python: 3.9+
   - 메모리: 최소 4GB RAM (백테스트용)
   - 스토리지: 50GB (과거 데이터 저장용)

2. **배포 및 운영**
   ```dockerfile
   # Dockerfile
   FROM python:3.9-slim
   
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   
   COPY . .
   CMD ["python", "main.py"]
   ```

3. **모니터링 및 로깅**
   ```python
   # 로그 설정
   logging.basicConfig(
       level=logging.INFO,
       format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
       handlers=[
           logging.FileHandler('trading.log'),
           logging.FileHandler('backtest.log'),  # 백테스트 전용 로그
           logging.StreamHandler()
       ]
   )
   ```

### 데이터 관리
1. **과거 데이터 캐싱**
   ```bash
   # 데이터 디렉토리 구조
   data/
   ├── historical/
   │   ├── BTCUSDT_1m_2023.csv
   │   ├── BTCUSDT_1d_2023.csv
   │   └── BTCUSDT_1w_2023.csv
   ├── backtest_results/
   │   ├── backtest_20250612_143005.json
   │   └── backtest_20250611_091234.json
   └── live_trading/
       └── positions.json
   ```

2. **데이터 백업 스크립트**
   ```bash
   #!/bin/bash
   # backup_data.sh
   DATE=$(date +%Y%m%d_%H%M%S)
   tar -czf "backup_${DATE}.tar.gz" data/ logs/
   aws s3 cp "backup_${DATE}.tar.gz" s3://trading-backups/
   ```

### CI/CD 파이프라인
```yaml
# .github/workflows/deploy.yml
name: Deploy Trading Bot
on:
  push:
    branches: [main]
    
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run backtest validation
        run: python -m pytest tests/test_backtest.py
      - name: Run strategy tests
        run: python -m pytest tests/test_strategy.py
        
  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to server
        run: |
          ssh user@server 'cd trading-bot && git pull && docker-compose restart'
```

### 보안 요구사항
1. **API 키 관리**
   ```python
   # .env 파일 사용
   BINANCE_API_KEY=your_api_key
   BINANCE_SECRET_KEY=your_secret_key
   TRADING_MODE=backtest  # backtest, paper, live
   ```

2. **네트워크 보안**
   - VPN 연결 권장
   - 방화벽 설정 (필요한 포트만 개방)
   - SSL/TLS 인증서 적용

### 성능 최적화
```python
# 백테스트 성능 최적화
import multiprocessing as mp

def parallel_backtest(symbol_chunks):
    # 여러 심볼 동시 백테스트
    with mp.Pool() as pool:
        results = pool.map(run_single_backtest, symbol_chunks)
    return results
```

---

## QA Engineer

### 테스트 전략
1. **백테스트 검증 테스트**
   ```python
   class TestBacktestEngine:
       def test_historical_data_accuracy(self):
           # 과거 데이터 정확성 검증
           
       def test_backtest_calculation(self):
           # 백테스트 계산 정확성 검증
           
       def test_performance_metrics(self):
           # 성과 지표 계산 정확성
           
       def test_timeframe_consistency(self):
           # 다른 타임프레임 간 일관성 확인
   ```

2. **단위 테스트 (Unit Tests)**
   ```python
   class TestTurtleStrategy:
       def test_atr_calculation(self):
           # ATR 계산 정확성 검증
           
       def test_breakout_signal(self):
           # 돌파 신호 정확성 검증
           
       def test_position_sizing(self):
           # 포지션 사이즈 계산 검증
           
       def test_stop_loss_calculation(self):
           # 손절가 계산 검증
   ```

3. **통합 테스트 (Integration Tests)**
   ```python
   class TestBinanceIntegration:
       def test_historical_data_download(self):
           # 과거 데이터 다운로드 테스트
           
       def test_api_connection(self):
           # API 연결 테스트
           
       def test_order_execution(self):
           # 주문 실행 테스트 (테스트넷)
           
       def test_data_retrieval(self):
           # 시장 데이터 조회 테스트
   ```

4. **백테스트 검증 시나리오**
   ```python
   def test_known_period_backtest():
       # 알려진 기간의 백테스트 결과 검증
       # 예: 2020년 비트코인 강세장 기간
       config = {
           'start_date': '2020-01-01',
           'end_date': '2020-12-31',
           'timeframe': '1d',
           'initial_balance': 10000
       }
       results = run_backtest(config)
       assert results['total_return'] > 0  # 강세장에서 수익 예상
   ```

### 테스트 시나리오
1. **정상 시나리오**
   - 백테스트 실행 → 결과 생성 → 리포트 출력
   - 매매 신호 발생 → 주문 실행 → 포지션 관리
   - 손절/익절 신호 → 청산 실행
   - 피라미딩 조건 충족 → 추가 진입

2. **예외 시나리오**
   - 과거 데이터 부족
   - 잘못된 날짜 범위
   - API 연결 실패
   - 주문 실행 실패
   - 잘못된 시장 데이터
   - 계좌 잔고 부족

3. **성능 테스트**
   - 대용량 백테스트 (3년 이상 데이터)
   - 메모리 사용량 모니터링
   - CPU 사용률 확인
   - 응답 시간 측정

### 테스트 자동화
```python
# conftest.py
@pytest.fixture
def mock_binance_client():
    with patch('binance.Client') as mock:
        yield mock

@pytest.fixture  
def sample_historical_data():
    return load_sample_data('BTCUSDT_2023_1d.csv')

@pytest.fixture
def backtest_config():
    return {
        'start_date': '2023-01-01',
        'end_date': '2023-12-31',
        'timeframe': '1d',
        'initial_balance': 10000
    }
```

### 백테스트 결과 검증 기준
```python
def validate_backtest_results(results):
    """백테스트 결과 유효성 검증"""
    assert results['initial_balance'] > 0
    assert results['final_balance'] > 0
    assert 0 <= results['win_rate'] <= 1
    assert results['total_trades'] >= 0
    assert -1 <= results['max_drawdown'] <= 0
    assert results['sharpe_ratio'] is not None
```

---

## Technical Writer

### 문서화 요구사항

1. **사용자 매뉴얼**
   ```markdown
   # Bitcoin Futures Turtle Trading Bot - 사용 가이드
   
   ## 설치 방법
   1. Python 3.9+ 설치
   2. 의존성 패키지 설치: `pip install -r requirements.txt`
   3. 설정 파일 작성: `.env` 파일 생성
   
   ## 백테스팅 실행
   ### 1. 백테스트 설정
   - 기간: 분석하고자 하는 시작일과 종료일 설정
   - 타임프레임: 1m, 5m, 15m, 1h, 4h, 1d, 1w, 1M 중 선택
   - 초기 자금: 시뮬레이션할 초기 투자금 설정
   
   ### 2. 백테스트 실행
   ```bash
   python main.py
   # 메뉴에서 "1. 백테스트 실행" 선택
   ```
   
   ### 3. 결과 해석
   - 총 수익률: 전체 기간 동안의 수익률
   - 샤프 비율: 위험 대비 수익률 (1.0 이상 권장)
   - 최대 드로다운: 최대 손실폭 (낮을수록 좋음)
   
   ## 실제 트레이딩
   ### 1. 가상매매 시작
   ```bash
   python main.py
   # 메뉴에서 "2. 가상매매 시작" 선택
   ```
   
   ### 2. 실제매매 시작  
   ```bash
   python main.py
   # 메뉴에서 "3. 실제매매 시작" 선택
   ```
   ```

2. **백테스트 가이드**
   ```markdown
   # 백테스트 완전 가이드
   
   ## 백테스트란?
   백테스트는 과거 데이터를 사용하여 트레이딩 전략의 성과를 검증하는 과정입니다.
   
   ## 기간 선택 가이드
   - **단기 테스트**: 3-6개월 (빠른 검증)
   - **중기 테스트**: 1-2년 (계절성 고려)
   - **장기 테스트**: 3년 이상 (여러 시장 사이클 포함)
   
   ## 타임프레임별 특징
   - **1m, 5m**: 스캘핑, 높은 거래 빈도
   - **15m, 1h**: 데이 트레이딩
   - **4h, 1d**: 스윙 트레이딩 (터틀 전략에 최적)
   - **1w, 1M**: 장기 투자
   
   ## 결과 해석 방법
   ### 수익성 지표
   - 총 수익률 > 20% (연간)
   - 샤프 비율 > 1.0
   - 승률 > 50%
   
   ### 위험 지표
   - 최대 드로다운 < 20%
   - 연속 손실 < 5회
   ```

3. **API 문서**
   ```python
   class BacktestEngine:
       """
       터틀 트레이딩 백테스트 엔진
       
       Args:
           config (dict): 백테스트 설정
               - start_date (str): 시작일 (YYYY-MM-DD)
               - end_date (str): 종료일 (YYYY-MM-DD)
               - timeframe (str): 타임프레임 (1m, 5m, 15m, 1h, 4h, 1d, 1w, 1M)
               - initial_balance (float): 초기 자금
               
       Example:
           >>> config = {
           ...     'start_date': '2023-01-01',
           ...     'end_date': '2024-12-31',
           ...     'timeframe': '1d',
           ...     'initial_balance': 10000
           ... }
           >>> engine = BacktestEngine(config)
           >>> results = await engine.run_backtest()
       """
   ```

4. **설정 가이드**
   ```yaml
   # config.yaml
   backtest:
     default_timeframe: "1d"
     default_initial_balance: 10000
     commission_rate: 0.0004
     
   trading:
     symbols: ["BTCUSDT"]
     risk_per_trade: 0.01
     
   systems:
     system1:
       entry_period: 20
       exit_period: 10
       use_filter: true
     system2:
       entry_period: 55
       exit_period: 20
       use_filter: false
   ```

5. **트러블슈팅 가이드**
   ```markdown
   # 트러블슈팅 가이드
   
   ## 백테스트 관련 문제
   
   ### Q1: 백테스트가 너무 오래 걸려요
   A1: 
   - 더 짧은 기간으로 테스트해보세요
   - 더 긴 타임프레임 사용 (1h → 1d)
   - 캐시된 데이터가 있는지 확인하세요
   
   ### Q2: 백테스트 결과가 이상해요
   A2:
   - 데이터 기간이 충분한지 확인 (최소 55일 이상)
   - 수수료가 포함되었는지 확인
   - 로그 파일에서 에러 메시지 확인
   
   ### Q3: 과거 데이터를 불러올 수 없어요
   A3:
   - 인터넷 연결 상태 확인
   - Binance API 제한에 걸렸는지 확인
   - 날짜 형식이 올바른지 확인 (YYYY-MM-DD)
   ```

### 코드 주석 표준
```python
def run_backtest(config: Dict[str, Any]) -> BacktestResults:
    """
    터틀 트레이딩 전략 백테스트 실행
    
    과거 데이터를 사용하여 터틀 트레이딩 전략의 성과를 검증합니다.
    시스템 1(20일)과 시스템 2(55일) 돌파 전략을 모두 적용하며,
    ATR 기반 포지션 사이징과 피라미딩을 포함합니다.
    
    Args:
        config: 백테스트 설정 딕셔너리
            start_date (str): 백테스트 시작일 (YYYY-MM-DD 형식)
            end_date (str): 백테스트 종료일 (YYYY-MM-DD 형식)
            timeframe (str): 캔들 타임프레임 (1m/5m/15m/1h/4h/1d/1w/1M)
            initial_balance (float): 초기 투자 자금 (USD)
            
    Returns:
        BacktestResults: 백테스트 결과 객체
            - total_return: 총 수익률 (%)
            - sharpe_ratio: 샤프 비율
            - max_drawdown: 최대 드로다운 (%)
            - win_rate: 승률 (%)
            - total_trades: 총 거래 수
            - profit_factor: 수익 팩터
            
    Raises:
        ValueError: 시작일이 종료일보다 늦을 경우
        ConnectionError: Binance API 연결 실패 시
        DataError: 과거 데이터 로드 실패 시
        
    Example:
        >>> config = {
        ...     'start_date': '2023-01-01',
        ...     'end_date': '2024-12-31',
        ...     'timeframe': '1d',
        ...     'initial_balance': 10000
        ... }
        >>> results = run_backtest(config)
        >>> print(f"총 수익률: {results.total_return:.2f}%")
        총 수익률: 58.47%
    """
```

---

## Project Manager

### 프로젝트 개요
- **프로젝트명**: Bitcoin Futures Turtle Trading Bot
- **기간**: 8주 (기획 1주 + 백테스트 개발 3주 + 라이브 트레이딩 3주 + 테스트 1주)
- **팀 구성**: 7명 (각 역할별 1명)

### 일정 계획

#### Week 1: 기획 및 설계
- [x] 요구사항 정의 및 분석
- [ ] 백테스팅 시스템 아키텍처 설계
- [ ] UI/UX 설계 (메뉴 + 백테스트 + 라이브)
- [ ] 기술 스택 결정
- [ ] 프로젝트 셋업

#### Week 2-3: 백테스팅 시스템 개발
- [ ] 과거 데이터 수집 모듈 구현
- [ ] 백테스트 엔진 개발
- [ ] 터틀 트레이딩 전략 구현
- [ ] 성과 지표 계산 모듈
- [ ] 백테스트 UI 구현

#### Week 3-4: 백테스팅 완성 및 검증
- [ ] 백테스트 결과 리포트 생성
- [ ] 다양한 타임프레임 지원
- [ ] 백테스트 정확성 검증
- [ ] 성능 최적화
- [ ] 백테스트 문서화

#### Week 5-6: 라이브 트레이딩 개발
- [ ] Binance API 연동
- [ ] 실시간 데이터 처리
- [ ] 가상매매 시스템 구현
- [ ] 실제매매 시스템 구현
- [ ] 라이브 대시보드 구현

#### Week 7: 통합 및 고급 기능
- [ ] 백테스트 ↔ 라이브 연동
- [ ] 리스크 관리 시스템
- [ ] 알림 및 로깅 시스템
- [ ] 설정 관리 시스템
- [ ] 성과 비교 분석

#### Week 8: 테스트 및 배포
- [ ] 통합 테스트
- [ ] 백테스트 검증 테스트
- [ ] 사용자 테스트
- [ ] 성능 최적화
- [ ] 최종 문서화 및 배포

### 마일스톤

#### Milestone 1: 백테스팅 시스템 완성 (Week 4)
- 성공 기준:
  - [ ] 1년 이상 기간의 백테스트 실행 가능
  - [ ] 모든 타임프레임 지원 (1m ~ 1M)
  - [ ] 정확한 성과 지표 계산
  - [ ] 직관적인 백테스트 UI

#### Milestone 2: 라이브 트레이딩 시스템 완성 (Week 7)
- 성공 기준:
  - [ ] 가상매매 정상 동작
  - [ ] 실제매매 연동 완료
  - [ ] 실시간 대시보드 구현
  - [ ] 백테스트 대비 실제 성과 추적

#### Milestone 3: 최종 배포 (Week 8)
- 성공 기준:
  - [ ] 모든 기능 통합 테스트 통과
  - [ ] 문서화 100% 완료
  - [ ] 배포 환경 구축 완료

### 위험 관리
1. **기술적 위험**
   - 백테스트 정확성 문제
   - Binance API 제한사항
   - 대용량 과거 데이터 처리 성능
   - 실시간 데이터 처리 지연

2. **일정 위험**
   - 백테스트 엔진 복잡도 과소평가
   - 과거 데이터 품질 문제
   - API 연동 복잡도
   - 성능 최적화 시간 부족

3. **완화 방안**
   - 백테스트 프로토타입 우선 개발
   - 샘플 데이터로 초기 검증
   - 단계별 배포 전략
   - 충분한 테스트 기간 확보

### 성공 기준
1. **백테스팅 요구사항**
   - 다양한 기간/타임프레임 백테스트 지원
   - 99% 이상 계산 정확도
   - 직관적인 결과 해석 UI
   - 상세한 성과 분석 리포트

2. **라이브 트레이딩 요구사항**
   - 터틀 트레이딩 전략 정확한 구현
   - 실제/가상매매 모드 정상 동작
   - 실시간 대시보드 구현
   - 백테스트 대비 실제 성과 추적

3. **품질 요구사항**
   - 95% 이상 코드 커버리지
   - 제로 크리티컬 버그
   - 완전한 문서화
   - 사용자 친화적 인터페이스

### 커뮤니케이션 계획
- **일일 스탠드업**: 매일 오전 9시
- **주간 리뷰**: 매주 금요일 오후 2시
- **마일스톤 리뷰**: 각 마일스톤 완료 시
- **백테스트 검증 회의**: Week 4 (특별 세션)
- **도구**: Slack, GitHub, Notion

### 품질 관리
- 백테스트 결과 검증 프로세스
- 코드 리뷰 의무화
- 자동화된 테스트 실행
- 성능 벤치마크 모니터링
- 사용자 피드백 수집 및 반영
# 🐢 Bitcoin Futures Turtle Trading Bot

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Active-brightgreen)](https://github.com)

Professional algorithmic trading system based on the original Turtle Trading Rules, specifically designed for Bitcoin futures trading on Binance.

## ✨ 주요 기능

- 🔄 **이중 시스템 지원**: 20일 및 55일 돌파 전략
- 📊 **포괄적인 백테스팅**: 다양한 기간과 타임프레임으로 전략 검증
- 🎯 **고급 위험 관리**: ATR 기반 포지션 사이징 및 손절매
- 📈 **실시간 대시보드**: Rich 라이브러리 기반 터미널 인터페이스
- 🔄 **피라미딩**: 유리한 가격 움직임에 따른 자동 포지션 추가
- 💰 **가상/실제 매매**: 위험 없는 모의 거래부터 실제 자금 거래까지
- 📋 **상세한 성과 분석**: 수익률, 드로다운, 샤프 비율 등 전문적 지표

## 🚀 빠른 시작

### 설치

1. **저장소 클론**
   ```bash
   git clone https://github.com/your-username/turtle-trading.git
   cd turtle-trading
   ```

2. **의존성 설치**
   ```bash
   pip install -r requirements.txt
   ```

3. **환경 설정**
   ```bash
   cp .env.example .env
   # .env 파일을 편집하여 필요한 설정값 입력
   ```

### 사용법

#### 1. 프로그램 실행
```bash
python main.py
```

#### 2. 메뉴 선택
- **백테스트 실행**: 과거 데이터로 전략 검증
- **가상매매**: 실시간 데이터로 모의 거래
- **실제매매**: Binance 실계좌 연동 거래

#### 3. 백테스트 예시
```python
# 백테스트 설정
설정 = {
    '종목': 'BTCUSDT',
    '시작일': '2023-01-01',
    '종료일': '2024-12-31', 
    '타임프레임': '1d',
    '초기자금': 10000,
    '시스템': [1, 2]  # 시스템 1과 2 모두 사용
}
```

## 📖 터틀 트레이딩 전략

### 시스템 개요

| 구분 | 시스템 1 | 시스템 2 |
|------|----------|----------|
| **진입 신호** | 20일 최고가 돌파 | 55일 최고가 돌파 |
| **청산 신호** | 10일 최저가 돌파 | 20일 최저가 돌파 |
| **필터** | 손실 거래 후 대기 | 필터 없음 |
| **특징** | 빈번한 거래 | 큰 추세만 포착 |

### 위험 관리 규칙

- **포지션 사이징**: 계좌의 1% 위험 (ATR 기반)
- **손절매**: 진입가 기준 2N (N = ATR)
- **피라미딩**: 0.5N마다 최대 4유닛까지 추가
- **최대 위험**: 총 계좌의 20%

### 핵심 공식

```python
# ATR 계산
True Range = max(High - Low, |High - Prev_Close|, |Low - Prev_Close|)
ATR = 20일 True Range 평균

# 포지션 사이즈
Unit Size = (계좌잔고 × 0.01) / ATR

# 손절가
손절가_롱 = 진입가 - (2 × ATR)
손절가_숏 = 진입가 + (2 × ATR)
```

## 🎛️ 설정

### 환경 변수 (.env)
```bash
# Binance API (실제 거래 시 필요)
BINANCE_API_KEY=your_api_key_here
BINANCE_SECRET_KEY=your_secret_key_here
BINANCE_TESTNET=True

# 거래 모드
TRADING_MODE=backtest  # backtest, paper, live

# 로그 설정
LOG_LEVEL=INFO
```

### 주요 설정 파일
- `config.py`: 전체 시스템 설정
- `.env`: 환경 변수 및 API 키
- `CLAUDE.md`: Claude Code 개발 가이드

## 📊 백테스트 결과 예시

```
📊 전체 성과 요약
초기 자금: $10,000  →  최종 자금: $15,847
총 수익률: +58.47%  |  연화 수익률: +24.3%
최대 드로다운: -12.8%  |  샤프 비율: 1.67

📈 거래 통계
총 거래 수: 156번  |  승률: 67.3%
롱 거래: 89번 (승률 71.9%)  |  숏 거래: 67번 (승률 61.2%)
평균 수익: +$125  |  평균 손실: -$67
수익 팩터: 1.8
```

## 🏗️ 프로젝트 구조

```
turtle-trading/
├── main.py                    # 메인 실행 파일
├── config.py                  # 전체 설정
├── strategy/                  # 터틀 전략 구현
│   └── turtle_strategy.py
├── frontend/                  # 사용자 인터페이스
│   ├── main_menu.py
│   ├── backtest/             # 백테스트 UI
│   └── dashboard/            # 실시간 대시보드
├── .backend/                 # 백엔드 시스템
│   ├── engines/              # 백테스트/거래 엔진
│   └── api/                  # Binance API 연동
├── tests/                    # 테스트 코드
├── data/                     # 데이터 저장소
│   ├── historical/           # 과거 데이터
│   ├── backtest_results/     # 백테스트 결과
│   └── live_trading/         # 실거래 데이터
└── docs/                     # 문서
```

## 🔧 개발 및 테스트

### 테스트 실행
```bash
# 전체 테스트
pytest tests/ -v

# 특정 테스트만
pytest tests/test_turtle_strategy.py -v

# 느린 테스트 제외
pytest tests/ -v -m "not slow"
```

### 코딩 스타일
```bash
# 코드 포맷팅
black .

# 린트 검사
flake8 .

# 타입 검사
mypy strategy/
```

## ⚠️ 중요 주의사항

### 🔴 위험 고지
- **투자 위험**: 암호화폐 거래는 높은 위험을 수반합니다
- **손실 가능성**: 투자 원금의 전액 손실이 가능합니다
- **시장 변동성**: 급격한 가격 변동으로 예상과 다른 결과가 발생할 수 있습니다
- **기술적 위험**: 시스템 오류, 네트워크 문제 등으로 인한 손실 가능성

### 🛡️ 안전 수칙
1. **소액으로 시작**: 처음에는 작은 금액으로 테스트
2. **백테스트 필수**: 실제 거래 전 충분한 백테스트 수행
3. **가상매매 연습**: 실제 자금 투입 전 가상매매로 연습
4. **리스크 관리**: 절대 감당할 수 없는 금액 투자 금지
5. **지속적 모니터링**: 거래 중 정기적인 시스템 점검

### 📋 사전 요구사항
- Python 3.9 이상
- 안정적인 인터넷 연결
- Binance 계정 (실제 거래 시)
- 터미널/명령프롬프트 기본 사용법

## 📞 지원 및 문의

### 문제 해결
1. **로그 확인**: `logs/` 디렉토리의 로그 파일 점검
2. **설정 검증**: `python config.py` 실행으로 설정 확인
3. **테스트 실행**: `pytest tests/` 로 시스템 무결성 확인

### 일반적인 문제

#### Q: 백테스트가 너무 오래 걸려요
A: 더 짧은 기간이나 더 긴 타임프레임(1h → 1d) 사용을 권장합니다.

#### Q: Binance API 연결이 안 돼요
A: .env 파일의 API 키 설정과 네트워크 연결을 확인하세요.

#### Q: 백테스트 결과가 이상해요
A: 최소 55일 이상의 데이터 기간과 수수료 설정을 확인하세요.

### 기여하기
1. Fork 저장소
2. 새 기능 브랜치 생성 (`git checkout -b feature/amazing-feature`)
3. 변경사항 커밋 (`git commit -m 'Add amazing feature'`)
4. 브랜치에 푸시 (`git push origin feature/amazing-feature`)
5. Pull Request 생성

## 📜 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

## 🙏 감사의 말

- **Richard Dennis & William Eckhardt**: 원조 터틀 트레이딩 시스템 개발
- **Binance**: 암호화폐 거래 API 제공
- **Rich 라이브러리**: 아름다운 터미널 인터페이스
- **Python 커뮤니티**: 훌륭한 오픈소스 생태계

---

**⚠️ 면책조항**: 이 소프트웨어는 교육 및 연구 목적으로 제공됩니다. 실제 거래에 사용할 경우 발생하는 모든 손실에 대해 개발자는 책임을 지지 않습니다. 투자는 신중히 결정하시기 바랍니다.

**🚀 Made with [Claude Code](https://claude.ai/code)**# turtle-trading

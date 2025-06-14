# 터틀 트레이딩 자동매매 시스템 로직

## 1. 시스템 초기 설정

### 전역 변수
```
ACCOUNT_BALANCE = 초기_계좌잔고        # 계좌 총 자금
RISK_PER_TRADE = 0.01                 # 거래당 리스크 (1%)
MAX_RISK_TOTAL = 0.20                 # 총 최대 리스크 (20%)
ATR_PERIOD = 20                       # ATR 계산 기간
MAX_UNITS_PER_MARKET = 4              # 종목당 최대 유닛
MAX_UNITS_DIRECTIONAL = 12            # 방향별 최대 유닛 (롱/숏)
MAX_UNITS_CORRELATED = 6              # 연관 시장 최대 유닛
```

### 시스템 구분
```
SYSTEM_1 = {
    ENTRY_PERIOD: 20,     # 진입: 20일 돌파
    EXIT_PERIOD: 10,      # 청산: 10일 돌파
    USE_FILTER: true      # 이전 거래 필터 사용
}

SYSTEM_2 = {
    ENTRY_PERIOD: 55,     # 진입: 55일 돌파
    EXIT_PERIOD: 20,      # 청산: 20일 돌파
    USE_FILTER: false     # 이전 거래 필터 미사용
}
```

## 2. 데이터 구조 정의

### 가격 데이터
```
PriceData = {
    symbol: 종목코드,
    date: 날짜,
    open: 시가,
    high: 고가,
    low: 저가,
    close: 종가,
    volume: 거래량
}
```

### 포지션 데이터
```
Position = {
    symbol: 종목코드,
    direction: "LONG" | "SHORT",
    units: [
        {
            entry_price: 진입가격,
            entry_date: 진입날짜,
            size: 수량,
            stop_loss: 손절가,
            system: 1 | 2,
            unit_number: 1~4
        }
    ],
    total_size: 총수량,
    avg_price: 평균단가
}
```

## 3. 핵심 계산 함수

### ATR 계산
```
function calculate_ATR(price_data, period):
    true_ranges = []
    
    for i in range(1, len(price_data)):
        current = price_data[i]
        previous = price_data[i-1]
        
        tr1 = current.high - current.low
        tr2 = abs(current.high - previous.close)
        tr3 = abs(current.low - previous.close)
        
        true_range = max(tr1, tr2, tr3)
        true_ranges.append(true_range)
    
    return average(true_ranges[-period:])
```

### 유닛 사이즈 계산
```
function calculate_unit_size(symbol, account_balance):
    N = calculate_ATR(symbol, ATR_PERIOD)
    dollar_volatility = N * contract_size * price_multiplier
    unit_size = (account_balance * RISK_PER_TRADE) / dollar_volatility
    
    return floor(unit_size)  # 소수점 이하 버림
```

### 돌파 확인
```
function check_breakout(price_data, period, direction):
    if direction == "LONG":
        current_price = price_data[-1].close
        highest_high = max([p.high for p in price_data[-period-1:-1]])
        return current_price > highest_high
    
    elif direction == "SHORT":
        current_price = price_data[-1].close
        lowest_low = min([p.low for p in price_data[-period-1:-1]])
        return current_price < lowest_low
```

## 4. 진입 로직

### 진입 신호 확인
```
function check_entry_signal(symbol, system):
    price_data = get_price_data(symbol, days=100)
    
    # 시스템별 진입 조건
    if system == 1:
        breakout = check_breakout(price_data, 20, "LONG")
        filter_check = not last_trade_was_loss(symbol) if SYSTEM_1.USE_FILTER else True
        return breakout and filter_check
    
    elif system == 2:
        return check_breakout(price_data, 55, "LONG")
```

### 진입 실행
```
function execute_entry(symbol, direction, system):
    # 1. 리스크 검증
    if not check_risk_limits():
        return False
    
    # 2. 유닛 사이즈 계산
    unit_size = calculate_unit_size(symbol, ACCOUNT_BALANCE)
    
    # 3. 진입가 설정 (다음날 시가)
    entry_price = get_next_open_price(symbol)
    
    # 4. 손절가 계산
    N = calculate_ATR(symbol, ATR_PERIOD)
    if direction == "LONG":
        stop_loss = entry_price - (2 * N)
    else:
        stop_loss = entry_price + (2 * N)
    
    # 5. 주문 실행
    order = {
        symbol: symbol,
        direction: direction,
        size: unit_size,
        price: entry_price,
        stop_loss: stop_loss,
        system: system
    }
    
    return place_order(order)
```

## 5. 피라미딩 로직

### 추가 진입 조건
```
function check_pyramid_signal(position):
    current_price = get_current_price(position.symbol)
    first_entry = position.units[0]
    N = calculate_ATR(position.symbol, ATR_PERIOD)
    
    # 현재 유닛 수 확인
    current_units = len(position.units)
    if current_units >= MAX_UNITS_PER_MARKET:
        return False
    
    # 가격 상승폭 계산
    if position.direction == "LONG":
        price_move = current_price - first_entry.entry_price
        required_move = 0.5 * N * current_units
        return price_move >= required_move
    
    else:  # SHORT
        price_move = first_entry.entry_price - current_price
        required_move = 0.5 * N * current_units
        return price_move >= required_move
```

### 피라미딩 실행
```
function execute_pyramid(position):
    unit_size = calculate_unit_size(position.symbol, ACCOUNT_BALANCE)
    entry_price = get_current_price(position.symbol)
    N = calculate_ATR(position.symbol, ATR_PERIOD)
    
    # 새 유닛 손절가 설정
    if position.direction == "LONG":
        stop_loss = entry_price - (2 * N)
    else:
        stop_loss = entry_price + (2 * N)
    
    # 기존 유닛들의 손절가도 업데이트
    update_all_stop_losses(position, stop_loss)
    
    new_unit = {
        entry_price: entry_price,
        entry_date: get_current_date(),
        size: unit_size,
        stop_loss: stop_loss,
        system: position.units[0].system,
        unit_number: len(position.units) + 1
    }
    
    position.units.append(new_unit)
```

## 6. 청산 로직

### 청산 신호 확인
```
function check_exit_signal(position):
    price_data = get_price_data(position.symbol, days=50)
    system = position.units[0].system
    
    if system == 1:
        exit_period = SYSTEM_1.EXIT_PERIOD
    else:
        exit_period = SYSTEM_2.EXIT_PERIOD
    
    if position.direction == "LONG":
        return check_breakout(price_data, exit_period, "SHORT")
    else:
        return check_breakout(price_data, exit_period, "LONG")
```

### 손절 확인
```
function check_stop_loss(position):
    current_price = get_current_price(position.symbol)
    
    for unit in position.units:
        if position.direction == "LONG":
            if current_price <= unit.stop_loss:
                return True
        else:  # SHORT
            if current_price >= unit.stop_loss:
                return True
    
    return False
```

### 청산 실행
```
function execute_exit(position, reason):
    total_size = sum([unit.size for unit in position.units])
    current_price = get_current_price(position.symbol)
    
    exit_order = {
        symbol: position.symbol,
        direction: "SELL" if position.direction == "LONG" else "BUY",
        size: total_size,
        price: current_price,
        reason: reason  # "SIGNAL" or "STOP_LOSS"
    }
    
    result = place_order(exit_order)
    
    if result.success:
        record_trade_result(position, current_price, reason)
        remove_position(position.symbol)
    
    return result
```

## 7. 리스크 관리

### 리스크 한도 확인
```
function check_risk_limits():
    # 1. 총 손실 한도 확인
    total_loss = calculate_total_unrealized_loss()
    if total_loss > (ACCOUNT_BALANCE * MAX_RISK_TOTAL):
        emergency_exit_all_positions()
        return False
    
    # 2. 방향별 유닛 한도 확인
    long_units = count_units_by_direction("LONG")
    short_units = count_units_by_direction("SHORT")
    
    if long_units >= MAX_UNITS_DIRECTIONAL or short_units >= MAX_UNITS_DIRECTIONAL:
        return False
    
    # 3. 연관 시장 한도 확인
    correlated_units = count_correlated_units()
    if correlated_units >= MAX_UNITS_CORRELATED:
        return False
    
    return True
```

## 8. 메인 실행 루프

### 일일 처리 프로세스
```
function daily_process():
    # 1. 시장 데이터 업데이트
    update_market_data()
    
    # 2. 기존 포지션 관리
    for position in get_all_positions():
        # 손절 확인
        if check_stop_loss(position):
            execute_exit(position, "STOP_LOSS")
            continue
        
        # 청산 신호 확인
        if check_exit_signal(position):
            execute_exit(position, "SIGNAL")
            continue
        
        # 피라미딩 확인
        if check_pyramid_signal(position):
            execute_pyramid(position)
    
    # 3. 새로운 진입 기회 스캔
    for symbol in get_watchlist():
        if not has_position(symbol):
            # 시스템 1 확인
            if check_entry_signal(symbol, 1):
                execute_entry(symbol, "LONG", 1)
            
            # 시스템 2 확인
            if check_entry_signal(symbol, 2):
                execute_entry(symbol, "LONG", 2)
    
    # 4. 리스크 점검
    if not check_risk_limits():
        log_warning("Risk limits exceeded")
    
    # 5. 일일 보고서 생성
    generate_daily_report()
```

## 9. 에러 처리

### 예외 상황 처리
```
function handle_errors():
    try:
        daily_process()
    except MarketDataError:
        log_error("Market data unavailable - skipping today")
        return
    except OrderExecutionError as e:
        log_error(f"Order execution failed: {e}")
        # 재시도 로직 또는 수동 개입 알림
    except RiskLimitError:
        emergency_exit_all_positions()
        send_alert("Emergency exit triggered")
    except Exception as e:
        log_error(f"Unexpected error: {e}")
        send_alert("System error - manual check required")
```

## 10. 백테스팅 및 성능 추적

### 성과 측정 지표
```
performance_metrics = {
    total_return: 총 수익률,
    max_drawdown: 최대 낙폭,
    sharpe_ratio: 샤프 비율,
    win_rate: 승률,
    avg_win: 평균 수익,
    avg_loss: 평균 손실,
    profit_factor: 수익 팩터
}
```

## 11. 클로드 코드 구현 시 주의사항

### 필수 구현 함수들
```
# 시장 데이터 관련
get_price_data(symbol, days)
get_current_price(symbol)
get_next_open_price(symbol)

# 주문 관리 관련
place_order(order)
cancel_order(order_id)
get_order_status(order_id)

# 포지션 관리 관련
get_all_positions()
has_position(symbol)
update_position(position)
remove_position(symbol)

# 계좌 관리 관련
get_account_balance()
calculate_total_unrealized_loss()
update_account_balance()

# 로깅 및 알림 관련
log_info(message)
log_warning(message)
log_error(message)
send_alert(message)
```

### 데이터 저장 구조
```
# JSON 파일로 저장
{
    "account": {
        "balance": 100000000,
        "initial_balance": 100000000,
        "current_risk": 0.05
    },
    "positions": [
        {
            "symbol": "삼성전자",
            "direction": "LONG",
            "units": [...],
            "total_size": 1000,
            "avg_price": 75000
        }
    ],
    "trade_history": [...],
    "market_data": {...}
}
```

이 문서는 터틀 트레이딩 시스템을 AI가 이해하고 구현할 수 있도록 구조화된 로직을 제공합니다. 각 함수와 조건문이 명확하게 정의되어 있어 프로그래밍 구현이 용이합니다.
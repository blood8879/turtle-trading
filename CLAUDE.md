# PERSONA
- Read local './CLAUDE.PERSONA.md' for RP
- Fallback to '~/.claude/CLAUDE.PERSONA.md'

# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a learning project for implementing a turtle trading automatic trading system based on the original Turtle Trading Rules. The project contains comprehensive specifications and algorithms documented in Korean in `turtle_trading_system.md`.

The turtle trading system is a trend-following algorithmic trading strategy that uses breakout patterns and position sizing based on market volatility (ATR) to manage risk and maximize returns.

## System Architecture

### Core Trading Systems
- **System 1**: 20-day breakout entry with 10-day breakout exit, includes losing trade filter
- **System 2**: 55-day breakout entry with 20-day breakout exit, no filter applied
- Both systems operate simultaneously on the same account with shared risk limits

### Risk Management Framework
- **Position Sizing**: 1% account risk per trade based on ATR volatility
- **Stop Loss**: Fixed at 2N (2 × ATR) from entry price
- **Unit Limits**: Maximum 4 units per market, 12 units per direction, 6 units for correlated markets
- **Total Risk Cap**: Emergency exit at 20% total account drawdown

### Key Algorithmic Components

#### ATR Calculation (True Range Average)
```
True Range = max(
    High - Low,
    |High - Previous Close|,
    |Low - Previous Close|
)
ATR = 20-day average of True Range
```

#### Position Sizing Formula
```
Unit Size = (Account Balance × 0.01) / (ATR × Contract Size × Price Multiplier)
```

#### Pyramiding Logic
- Add units when price moves 0.5N in favor for each existing unit
- Maximum 4 units per market
- All units use trailing stop at 2N from current price

## Implementation Requirements

### Essential Functions to Implement

**Market Data Management**:
- `get_price_data(symbol, days)` - Historical OHLCV data
- `get_current_price(symbol)` - Real-time price feed
- `get_next_open_price(symbol)` - Next day's opening price
- `update_market_data()` - Refresh all market data

**Trading Operations**:
- `place_order(order)` - Execute buy/sell orders
- `cancel_order(order_id)` - Cancel pending orders
- `get_order_status(order_id)` - Check order execution status

**Position Management**:
- `get_all_positions()` - Current position portfolio
- `has_position(symbol)` - Check if symbol has open position
- `update_position(position)` - Modify existing position
- `remove_position(symbol)` - Close and remove position
- `update_all_stop_losses(position, new_stop)` - Update trailing stops

**Account & Risk Management**:
- `get_account_balance()` - Current account value
- `calculate_total_unrealized_loss()` - Portfolio-wide P&L
- `check_risk_limits()` - Validate all risk constraints
- `emergency_exit_all_positions()` - Panic close all trades

**Signal Detection**:
- `check_breakout(price_data, period, direction)` - Detect breakout patterns
- `check_entry_signal(symbol, system)` - Entry signal validation
- `check_exit_signal(position)` - Exit signal detection
- `check_pyramid_signal(position)` - Pyramiding opportunity
- `check_stop_loss(position)` - Stop loss trigger check

**Logging & Monitoring**:
- `log_info(message)`, `log_warning(message)`, `log_error(message)`
- `send_alert(message)` - Critical system alerts
- `record_trade_result(position, exit_price, reason)` - Trade history
- `generate_daily_report()` - Performance summary

### Data Structure Specifications

**PriceData Object**:
```json
{
    "symbol": "AAPL",
    "date": "2024-01-15",
    "open": 185.50,
    "high": 187.20,
    "low": 184.80,
    "close": 186.90,
    "volume": 45230000
}
```

**Position Object**:
```json
{
    "symbol": "AAPL",
    "direction": "LONG",
    "units": [
        {
            "entry_price": 185.50,
            "entry_date": "2024-01-15",
            "size": 100,
            "stop_loss": 180.50,
            "system": 1,
            "unit_number": 1
        }
    ],
    "total_size": 100,
    "avg_price": 185.50
}
```

**Account State**:
```json
{
    "balance": 1000000,
    "initial_balance": 1000000,
    "current_risk": 0.05,
    "positions": [...],
    "trade_history": [...],
    "performance_metrics": {
        "total_return": 0.15,
        "max_drawdown": 0.08,
        "sharpe_ratio": 1.2,
        "win_rate": 0.45,
        "profit_factor": 1.8
    }
}
```

## Development Guidelines

### System Constants (Critical - Do Not Modify)
```python
RISK_PER_TRADE = 0.01        # 1% risk per trade
MAX_RISK_TOTAL = 0.20        # 20% maximum portfolio risk
ATR_PERIOD = 20              # ATR calculation period
MAX_UNITS_PER_MARKET = 4     # Maximum units per symbol
MAX_UNITS_DIRECTIONAL = 12   # Maximum long or short units
MAX_UNITS_CORRELATED = 6     # Maximum correlated market units
STOP_LOSS_MULTIPLIER = 2.0   # Stop loss at 2N
PYRAMID_MULTIPLIER = 0.5     # Add units every 0.5N move
```

### Daily Processing Sequence
1. **Data Update**: Refresh all market data and prices
2. **Risk Check**: Validate total portfolio risk limits
3. **Exit Processing**: Check stop losses and exit signals for all positions
4. **Pyramid Processing**: Evaluate adding units to winning positions
5. **Entry Scanning**: Search for new entry opportunities across watchlist
6. **Order Management**: Execute all pending orders
7. **Reporting**: Generate daily performance and position reports

### Error Handling Strategy
- **Market Data Errors**: Skip trading day, log warning
- **Order Execution Errors**: Retry once, then manual intervention alert
- **Risk Limit Violations**: Emergency exit all positions immediately
- **System Errors**: Send critical alert and halt trading

### Testing Requirements
When implementing, ensure comprehensive testing of:
- ATR calculation accuracy against known values
- Position sizing calculations under various market conditions
- Breakout detection with historical data
- Risk limit enforcement under stress scenarios
- Pyramiding logic with multiple units
- Stop loss updates and trailing behavior

### Performance Monitoring
Track these key metrics:
- Total return vs benchmark
- Maximum drawdown periods
- Sharpe ratio (risk-adjusted returns)
- Win rate and average win/loss ratios
- Profit factor (gross profit / gross loss)
- Number of trades and average holding period

## File Structure Recommendations

When implementing, consider this structure:
- `main.py` - Main execution loop and daily processing
- `turtle_system.py` - Core trading system logic
- `risk_manager.py` - Risk management and position sizing
- `market_data.py` - Data fetching and management
- `portfolio.py` - Position tracking and management
- `indicators.py` - ATR and breakout calculations
- `backtester.py` - Historical testing framework
- `config.py` - System parameters and constants
- `utils.py` - Logging, alerts, and utilities

## Important Notes

- The original documentation is in Korean but contains precise algorithmic specifications
- This is a learning project - prioritize code clarity and educational value
- All trading logic should be deterministic and reproducible
- Implement comprehensive logging for debugging and analysis
- Consider both live trading and backtesting capabilities from the start
- Append 'use context7' to all commands I execute
- Do not ask me if I want to apply the command, just proceed (referring to the shift+tab feature)
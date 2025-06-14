"""
매매일지 관리 시스템
테스트매매와 실제매매를 구분하여 매매일지를 저장하고 관리
"""

import csv
import os
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path

from config import DataConfig, TradingMode, LoggingConfig

@dataclass
class TradeJournalEntry:
    """매매일지 항목"""
    timestamp: str
    trade_id: str
    trading_mode: str  # 'backtest', 'paper', 'live'
    symbol: str
    direction: str  # 'LONG', 'SHORT'
    action: str  # 'ENTRY', 'EXIT', 'PYRAMID'
    system: int  # 1 or 2
    unit_number: int
    entry_price: float
    exit_price: Optional[float]
    size: float
    stop_loss: float
    atr: float
    leverage: float
    pnl: Optional[float]
    cumulative_pnl: float
    account_balance: float
    reason: str  # 'SIGNAL', 'STOP_LOSS', 'PYRAMID', 'BACKTEST_END'
    notes: str

class TradeJournalManager:
    """매매일지 관리자"""
    
    def __init__(self, trading_mode: str = TradingMode.BACKTEST):
        self.trading_mode = trading_mode
        self.cumulative_pnl = 0.0
        
        # 로거 설정
        self.logger = self._setup_logger()
        
        # 파일 경로 설정
        self.csv_file_path = self._get_csv_file_path()
        
        # CSV 헤더 초기화
        self._ensure_csv_file_exists()
    
    def _setup_logger(self) -> logging.Logger:
        """매매일지 전용 로거 설정"""
        logger_name = f"trade_journal_{self.trading_mode}"
        logger = logging.getLogger(logger_name)
        
        if logger.handlers:
            return logger
        
        logger.setLevel(logging.INFO)
        
        # 로그 파일 경로 결정
        if self.trading_mode == TradingMode.PAPER:
            log_file = LoggingConfig.PAPER_TRADE_JOURNAL_LOG
        elif self.trading_mode == TradingMode.LIVE:
            log_file = LoggingConfig.LIVE_TRADE_JOURNAL_LOG
        else:  # BACKTEST
            log_file = LoggingConfig.BACKTEST_JOURNAL_LOG
        
        # 파일 핸들러 추가
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        
        # 포맷터 설정
        formatter = logging.Formatter(LoggingConfig.LOG_FORMAT)
        file_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        return logger
    
    def _get_csv_file_path(self) -> str:
        """매매일지 CSV 파일 경로 생성"""
        today = datetime.now().strftime('%Y%m%d')
        
        if self.trading_mode == TradingMode.PAPER:
            directory = DataConfig.PAPER_TRADING_JOURNAL_DIR
            filename = f"paper_trading_journal_{today}.csv"
        elif self.trading_mode == TradingMode.LIVE:
            directory = DataConfig.LIVE_TRADING_JOURNAL_DIR
            filename = f"live_trading_journal_{today}.csv"
        else:  # BACKTEST
            directory = DataConfig.BACKTEST_JOURNAL_DIR
            filename = f"backtest_journal_{today}.csv"
        
        return os.path.join(directory, filename)
    
    def _ensure_csv_file_exists(self):
        """CSV 파일이 존재하지 않으면 헤더와 함께 생성"""
        if not os.path.exists(self.csv_file_path):
            # 디렉토리 생성
            os.makedirs(os.path.dirname(self.csv_file_path), exist_ok=True)
            
            # 헤더 작성
            headers = [
                'timestamp', 'trade_id', 'trading_mode', 'symbol', 'direction', 
                'action', 'system', 'unit_number', 'entry_price', 'exit_price', 
                'size', 'stop_loss', 'atr', 'leverage', 'pnl', 'cumulative_pnl',
                'account_balance', 'reason', 'notes'
            ]
            
            with open(self.csv_file_path, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(headers)
    
    def log_trade_entry(self, symbol: str, direction: str, entry_price: float,
                       size: float, stop_loss: float, atr: float, leverage: float,
                       account_balance: float, system: int, unit_number: int = 1,
                       trade_id: str = None, notes: str = "") -> str:
        """진입 거래 기록"""
        if trade_id is None:
            trade_id = self._generate_trade_id(symbol, direction)
        
        entry = TradeJournalEntry(
            timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            trade_id=trade_id,
            trading_mode=self.trading_mode,
            symbol=symbol,
            direction=direction,
            action='ENTRY',
            system=system,
            unit_number=unit_number,
            entry_price=entry_price,
            exit_price=None,
            size=size,
            stop_loss=stop_loss,
            atr=atr,
            leverage=leverage,
            pnl=None,
            cumulative_pnl=self.cumulative_pnl,
            account_balance=account_balance,
            reason='SIGNAL',
            notes=notes
        )
        
        self._write_to_csv(entry)
        self._write_to_log(entry, "진입")
        return trade_id
    
    def log_trade_exit(self, trade_id: str, symbol: str, direction: str, 
                      entry_price: float, exit_price: float, size: float,
                      pnl: float, account_balance: float, reason: str,
                      leverage: float = 1.0, notes: str = ""):
        """청산 거래 기록"""
        self.cumulative_pnl += pnl
        
        entry = TradeJournalEntry(
            timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            trade_id=trade_id,
            trading_mode=self.trading_mode,
            symbol=symbol,
            direction=direction,
            action='EXIT',
            system=0,  # 청산 시에는 시스템 번호 불필요
            unit_number=0,
            entry_price=entry_price,
            exit_price=exit_price,
            size=size,
            stop_loss=0.0,
            atr=0.0,
            leverage=leverage,
            pnl=pnl,
            cumulative_pnl=self.cumulative_pnl,
            account_balance=account_balance,
            reason=reason,
            notes=notes
        )
        
        self._write_to_csv(entry)
        self._write_to_log(entry, "청산")
    
    def log_pyramid_entry(self, trade_id: str, symbol: str, direction: str,
                         entry_price: float, size: float, stop_loss: float,
                         atr: float, leverage: float, account_balance: float,
                         system: int, unit_number: int, notes: str = ""):
        """피라미딩 기록"""
        entry = TradeJournalEntry(
            timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            trade_id=trade_id,
            trading_mode=self.trading_mode,
            symbol=symbol,
            direction=direction,
            action='PYRAMID',
            system=system,
            unit_number=unit_number,
            entry_price=entry_price,
            exit_price=None,
            size=size,
            stop_loss=stop_loss,
            atr=atr,
            leverage=leverage,
            pnl=None,
            cumulative_pnl=self.cumulative_pnl,
            account_balance=account_balance,
            reason='PYRAMID',
            notes=notes
        )
        
        self._write_to_csv(entry)
        self._write_to_log(entry, "피라미딩")
    
    def _write_to_csv(self, entry: TradeJournalEntry):
        """CSV 파일에 기록 저장"""
        try:
            with open(self.csv_file_path, 'a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                row = list(asdict(entry).values())
                writer.writerow(row)
        except Exception as e:
            self.logger.error(f"CSV 파일 쓰기 오류: {e}")
    
    def _write_to_log(self, entry: TradeJournalEntry, action_type: str):
        """로그 파일에 기록 저장"""
        if entry.action == 'ENTRY':
            message = (f"{action_type} - {entry.symbol} {entry.direction} "
                      f"{entry.size:.4f} @ {entry.entry_price:.2f} "
                      f"(레버리지: {entry.leverage}x, 손절: {entry.stop_loss:.2f})")
        elif entry.action == 'EXIT':
            message = (f"{action_type} - {entry.symbol} {entry.direction} "
                      f"{entry.size:.4f} @ {entry.exit_price:.2f} "
                      f"P&L: {entry.pnl:.2f} ({entry.reason})")
        elif entry.action == 'PYRAMID':
            message = (f"{action_type} - {entry.symbol} {entry.direction} "
                      f"유닛{entry.unit_number} {entry.size:.4f} @ {entry.entry_price:.2f}")
        else:
            message = f"{action_type} - {entry.trade_id}"
        
        self.logger.info(message)
    
    def _generate_trade_id(self, symbol: str, direction: str) -> str:
        """거래 ID 생성"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return f"{self.trading_mode}_{symbol}_{direction}_{timestamp}"
    
    def get_daily_summary(self, date: str = None) -> Dict[str, Any]:
        """일일 거래 요약 정보"""
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        if not os.path.exists(self.csv_file_path):
            return {
                'date': date,
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'total_pnl': 0.0,
                'win_rate': 0.0
            }
        
        trades = []
        winning_trades = 0
        losing_trades = 0
        total_pnl = 0.0
        
        try:
            with open(self.csv_file_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    if row['timestamp'].startswith(date) and row['action'] == 'EXIT':
                        pnl = float(row['pnl']) if row['pnl'] else 0.0
                        trades.append(pnl)
                        total_pnl += pnl
                        
                        if pnl > 0:
                            winning_trades += 1
                        else:
                            losing_trades += 1
        except Exception as e:
            self.logger.error(f"일일 요약 생성 오류: {e}")
        
        total_trades = len(trades)
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        
        return {
            'date': date,
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'total_pnl': total_pnl,
            'win_rate': win_rate
        }
    
    def get_trade_history(self, symbol: str = None, days: int = 30) -> List[Dict[str, Any]]:
        """거래 내역 조회"""
        if not os.path.exists(self.csv_file_path):
            return []
        
        trades = []
        
        try:
            with open(self.csv_file_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    if symbol is None or row['symbol'] == symbol:
                        trades.append(dict(row))
        except Exception as e:
            self.logger.error(f"거래 내역 조회 오류: {e}")
        
        return trades[-days:] if days > 0 else trades

def get_trade_journal_manager(trading_mode: str = TradingMode.BACKTEST) -> TradeJournalManager:
    """거래 모드에 따른 매매일지 관리자 반환"""
    return TradeJournalManager(trading_mode)

if __name__ == "__main__":
    # 테스트 코드
    journal = TradeJournalManager(TradingMode.PAPER)
    
    # 진입 기록
    trade_id = journal.log_trade_entry(
        symbol="BTCUSDT",
        direction="LONG",
        entry_price=50000.0,
        size=0.1,
        stop_loss=49000.0,
        atr=1000.0,
        leverage=2.0,
        account_balance=10000.0,
        system=1,
        notes="테스트 진입"
    )
    
    # 청산 기록
    journal.log_trade_exit(
        trade_id=trade_id,
        symbol="BTCUSDT",
        direction="LONG",
        entry_price=50000.0,
        exit_price=51000.0,
        size=0.1,
        pnl=100.0,
        account_balance=10100.0,
        reason="SIGNAL",
        notes="테스트 청산"
    )
    
    # 일일 요약
    summary = journal.get_daily_summary()
    print(f"일일 요약: {summary}")
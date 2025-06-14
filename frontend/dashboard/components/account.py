"""
계좌 정보 컴포넌트
"""

from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from typing import Dict, Any, Optional
from datetime import datetime

class AccountComponent:
    """계좌 정보 컴포넌트"""
    
    def __init__(self, initial_balance: float = 10000.0):
        self.initial_balance = initial_balance
        self.current_balance = initial_balance
        self.unrealized_pnl = 0.0
        self.margin_used = 0.0
        self.daily_pnl = 0.0
        self.daily_start_balance = initial_balance
        
        # 일일 시작 잔고 설정 (자정에 리셋)
        self._reset_daily_if_needed()
    
    async def update_data(self, current_prices: Dict[str, float], positions: Dict[str, Any]):
        """계좌 데이터 업데이트"""
        self._reset_daily_if_needed()
        
        # 미실현 손익 계산
        total_unrealized = 0.0
        total_margin = 0.0
        
        for symbol, position in positions.items():
            if symbol in current_prices:
                current_price = current_prices[symbol]
                
                # 미실현 손익
                if position.direction == "LONG":
                    unrealized = (current_price - position.avg_price) * position.total_size
                else:  # SHORT
                    unrealized = (position.avg_price - current_price) * position.total_size
                
                total_unrealized += unrealized
                
                # 마진 사용량 (포지션 가치의 10%로 가정)
                position_value = position.total_size * current_price
                total_margin += position_value * 0.1
        
        self.unrealized_pnl = total_unrealized
        self.margin_used = total_margin
        
        # 일일 손익 계산
        total_value = self.current_balance + self.unrealized_pnl
        self.daily_pnl = total_value - self.daily_start_balance
    
    def get_account_data(self) -> Dict[str, Any]:
        """계좌 데이터 반환"""
        total_value = self.current_balance + self.unrealized_pnl
        available_balance = max(0, self.current_balance - self.margin_used)
        
        # 수익률 계산
        total_pnl = total_value - self.initial_balance
        total_pnl_pct = (total_pnl / self.initial_balance) * 100
        daily_pnl_pct = (self.daily_pnl / self.daily_start_balance) * 100
        
        return {
            'balance': self.current_balance,
            'total_value': total_value,
            'unrealized_pnl': self.unrealized_pnl,
            'pnl': total_pnl,
            'pnl_pct': total_pnl_pct,
            'daily_pnl': self.daily_pnl,
            'daily_pnl_pct': daily_pnl_pct,
            'available': available_balance,
            'margin_used': self.margin_used,
            'margin_ratio': (self.margin_used / self.current_balance) * 100 if self.current_balance > 0 else 0
        }
    
    def create_account_panel(self) -> Panel:
        """계좌 정보 패널 생성"""
        data = self.get_account_data()
        
        account_table = Table.grid()
        account_table.add_column(style="cyan", width=14)
        account_table.add_column(style="bold", width=16)
        
        # 현재 잔고
        balance_color = "green" if data['balance'] > 0 else "red"
        account_table.add_row(
            "Balance:",
            f"[{balance_color}]${data['balance']:,.2f}[/{balance_color}]"
        )
        
        # 총 포트폴리오 가치
        total_color = "green" if data['total_value'] > self.initial_balance else "red"
        account_table.add_row(
            "Total Value:",
            f"[{total_color}]${data['total_value']:,.2f}[/{total_color}]"
        )
        
        # 미실현 손익
        unrealized_color = "green" if data['unrealized_pnl'] >= 0 else "red"
        unrealized_sign = "+" if data['unrealized_pnl'] >= 0 else ""
        account_table.add_row(
            "Unrealized:",
            f"[{unrealized_color}]{unrealized_sign}${data['unrealized_pnl']:,.2f}[/{unrealized_color}]"
        )
        
        # 총 손익
        pnl_color = "green" if data['pnl'] >= 0 else "red"
        pnl_sign = "+" if data['pnl'] >= 0 else ""
        account_table.add_row(
            "Total P&L:",
            f"[{pnl_color}]{pnl_sign}${data['pnl']:,.2f} ({data['pnl_pct']:+.1f}%)[/{pnl_color}]"
        )
        
        # 일일 손익
        daily_color = "green" if data['daily_pnl'] >= 0 else "red"
        daily_sign = "+" if data['daily_pnl'] >= 0 else ""
        account_table.add_row(
            "Daily P&L:",
            f"[{daily_color}]{daily_sign}${data['daily_pnl']:,.2f} ({data['daily_pnl_pct']:+.1f}%)[/{daily_color}]"
        )
        
        # 사용 가능 자금
        account_table.add_row(
            "Available:",
            f"[green]${data['available']:,.2f}[/green]"
        )
        
        # 마진 사용량
        margin_color = self._get_margin_color(data['margin_ratio'])
        account_table.add_row(
            "Margin Used:",
            f"[{margin_color}]${data['margin_used']:,.2f} ({data['margin_ratio']:.1f}%)[/{margin_color}]"
        )
        
        return Panel(
            account_table,
            title="💰 Account Summary",
            title_align="left",
            style="green"
        )
    
    def update_balance(self, realized_pnl: float):
        """실현 손익으로 잔고 업데이트"""
        self.current_balance += realized_pnl
    
    def reset(self):
        """계좌 초기화"""
        self.current_balance = self.initial_balance
        self.unrealized_pnl = 0.0
        self.margin_used = 0.0
        self.daily_pnl = 0.0
        self.daily_start_balance = self.initial_balance
    
    def _reset_daily_if_needed(self):
        """자정에 일일 수익률 리셋"""
        current_date = datetime.now().date()
        if not hasattr(self, '_last_date') or self._last_date != current_date:
            self.daily_start_balance = self.current_balance + self.unrealized_pnl
            self.daily_pnl = 0.0
            self._last_date = current_date
    
    def _get_margin_color(self, margin_ratio: float) -> str:
        """마진 비율에 따른 색상 반환"""
        if margin_ratio > 80:
            return "red"
        elif margin_ratio > 60:
            return "yellow"
        elif margin_ratio > 40:
            return "blue"
        else:
            return "green"
    
    def get_risk_metrics(self) -> Dict[str, float]:
        """리스크 지표 반환"""
        data = self.get_account_data()
        
        return {
            'account_risk': abs(data['pnl']) / self.initial_balance if data['pnl'] < 0 else 0,
            'margin_ratio': data['margin_ratio'],
            'available_ratio': (data['available'] / self.current_balance) * 100 if self.current_balance > 0 else 0,
            'leverage': data['margin_used'] / data['available'] if data['available'] > 0 else 0
        }
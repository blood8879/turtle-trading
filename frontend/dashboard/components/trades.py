"""
거래 내역 컴포넌트
"""

from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from typing import List, Any, Dict, Optional
from datetime import datetime, timedelta

class TradesComponent:
    """거래 내역 컴포넌트"""
    
    def __init__(self, max_display: int = 5):
        self.max_display = max_display
        self.trade_history = []
    
    def update_trades(self, trade_history: List[Any]):
        """거래 내역 업데이트"""
        self.trade_history = trade_history
    
    def create_recent_trades_panel(self, trade_history: List[Any], max_trades: int = None) -> Panel:
        """최근 거래 내역 패널 생성"""
        display_count = max_trades or self.max_display
        recent_trades = trade_history[-display_count:] if trade_history else []
        
        if not recent_trades:
            no_trades = Text("No completed trades yet", style="dim italic")
            return Panel(
                Align.center(no_trades),
                title=f"📋 Recent Trades (Last {display_count})",
                title_align="left",
                style="magenta"
            )
        
        trades_table = Table()
        trades_table.add_column("Date", style="cyan", width=10)
        trades_table.add_column("Symbol", style="white", width=8)
        trades_table.add_column("Side", style="bold", width=5)
        trades_table.add_column("Entry", style="blue", width=8)
        trades_table.add_column("Exit", style="blue", width=8)
        trades_table.add_column("P&L", style="bold", width=10)
        trades_table.add_column("System", style="yellow", width=6)
        trades_table.add_column("Reason", style="dim", width=8)
        
        for trade in recent_trades:
            direction_color = "green" if trade.direction == "LONG" else "red"
            pnl_color = "green" if trade.pnl > 0 else "red"
            
            trades_table.add_row(
                trade.exit_date.strftime("%m-%d"),
                trade.symbol[:8],
                f"[{direction_color}]{trade.direction[:4]}[/{direction_color}]",
                f"${trade.entry_price:,.0f}",
                f"${trade.exit_price:,.0f}",
                f"[{pnl_color}]{trade.pnl:+.0f}[/{pnl_color}]",
                f"S{trade.system}",
                trade.exit_reason[:8]
            )
        
        return Panel(
            trades_table,
            title=f"📋 Recent Trades (Last {len(recent_trades)})",
            title_align="left",
            style="magenta"
        )
    
    def create_trade_summary_panel(self, trade_history: List[Any]) -> Panel:
        """거래 요약 패널"""
        if not trade_history:
            return Panel(
                Text("No trade data", style="dim"),
                title="📊 Trade Summary"
            )
        
        # 기본 통계
        total_trades = len(trade_history)
        winning_trades = [t for t in trade_history if t.pnl > 0]
        losing_trades = [t for t in trade_history if t.pnl <= 0]
        
        # 시스템별 분석
        system1_trades = [t for t in trade_history if t.system == 1]
        system2_trades = [t for t in trade_history if t.system == 2]
        
        # 방향별 분석
        long_trades = [t for t in trade_history if t.direction == "LONG"]
        short_trades = [t for t in trade_history if t.direction == "SHORT"]
        
        summary_table = Table.grid()
        summary_table.add_column(style="cyan", width=18)
        summary_table.add_column(style="bold", width=12)
        summary_table.add_column(style="cyan", width=18)
        summary_table.add_column(style="bold", width=12)
        
        # 기본 통계
        win_rate = len(winning_trades) / total_trades if total_trades > 0 else 0
        win_rate_color = "green" if win_rate > 0.5 else "yellow" if win_rate > 0.4 else "red"
        
        summary_table.add_row(
            "Total Trades:",
            f"{total_trades}",
            "Win Rate:",
            f"[{win_rate_color}]{win_rate:.1%}[/{win_rate_color}]"
        )
        
        # 손익 통계
        total_profit = sum(t.pnl for t in winning_trades)
        total_loss = sum(t.pnl for t in losing_trades)
        
        summary_table.add_row(
            "Total Profit:",
            f"[green]${total_profit:+.0f}[/green]",
            "Total Loss:",
            f"[red]${total_loss:+.0f}[/red]"
        )
        
        # 평균 손익
        avg_win = total_profit / len(winning_trades) if winning_trades else 0
        avg_loss = total_loss / len(losing_trades) if losing_trades else 0
        
        summary_table.add_row(
            "Avg Win:",
            f"[green]${avg_win:+.0f}[/green]",
            "Avg Loss:",
            f"[red]${avg_loss:+.0f}[/red]"
        )
        
        # 시스템별 성과
        s1_count = len(system1_trades)
        s2_count = len(system2_trades)
        
        summary_table.add_row(
            "System 1 Trades:",
            f"{s1_count}",
            "System 2 Trades:",
            f"{s2_count}"
        )
        
        # 방향별 성과
        summary_table.add_row(
            "Long Trades:",
            f"{len(long_trades)}",
            "Short Trades:",
            f"{len(short_trades)}"
        )
        
        return Panel(
            summary_table,
            title="📊 Trade Summary",
            style="blue"
        )
    
    def create_daily_trades_panel(self, trade_history: List[Any]) -> Panel:
        """일일 거래 분석 패널"""
        if not trade_history:
            return Panel(
                Text("No trade data", style="dim"),
                title="📅 Daily Analysis"
            )
        
        # 오늘 거래
        today = datetime.now().date()
        today_trades = [t for t in trade_history if t.exit_date.date() == today]
        
        # 최근 7일 거래
        week_ago = datetime.now() - timedelta(days=7)
        week_trades = [t for t in trade_history if t.exit_date >= week_ago]
        
        # 일일 통계
        daily_table = Table.grid()
        daily_table.add_column(style="cyan", width=15)
        daily_table.add_column(style="bold", width=15)
        
        # 오늘 통계
        today_pnl = sum(t.pnl for t in today_trades)
        today_pnl_color = "green" if today_pnl >= 0 else "red"
        
        daily_table.add_row(
            "Today's Trades:",
            f"{len(today_trades)}"
        )
        daily_table.add_row(
            "Today's P&L:",
            f"[{today_pnl_color}]${today_pnl:+.0f}[/{today_pnl_color}]"
        )
        
        # 주간 통계
        week_pnl = sum(t.pnl for t in week_trades)
        week_pnl_color = "green" if week_pnl >= 0 else "red"
        
        daily_table.add_row(
            "Week Trades:",
            f"{len(week_trades)}"
        )
        daily_table.add_row(
            "Week P&L:",
            f"[{week_pnl_color}]${week_pnl:+.0f}[/{week_pnl_color}]"
        )
        
        # 평균 거래 빈도
        if trade_history:
            trading_days = (trade_history[-1].exit_date - trade_history[0].exit_date).days + 1
            avg_trades_per_day = len(trade_history) / max(trading_days, 1)
            
            daily_table.add_row(
                "Avg Trades/Day:",
                f"{avg_trades_per_day:.1f}"
            )
        
        return Panel(
            daily_table,
            title="📅 Daily Analysis",
            style="cyan"
        )
    
    def create_trade_timing_panel(self, trade_history: List[Any]) -> Panel:
        """거래 타이밍 분석 패널"""
        if not trade_history:
            return Panel(
                Text("No trade data", style="dim"),
                title="⏰ Timing Analysis"
            )
        
        # 거래 지속 기간 분석
        durations = []
        for trade in trade_history:
            if hasattr(trade, 'entry_date') and hasattr(trade, 'exit_date'):
                duration = trade.exit_date - trade.entry_date
                durations.append(duration.total_seconds() / 3600)  # 시간 단위
        
        if durations:
            avg_duration = sum(durations) / len(durations)
            min_duration = min(durations)
            max_duration = max(durations)
        else:
            avg_duration = min_duration = max_duration = 0
        
        # 요일별 분석
        weekday_stats = self._analyze_weekday_performance(trade_history)
        
        timing_table = Table.grid()
        timing_table.add_column(style="cyan", width=18)
        timing_table.add_column(style="bold", width=15)
        
        timing_table.add_row(
            "Avg Hold Time:",
            f"{avg_duration:.1f}h"
        )
        timing_table.add_row(
            "Min Hold Time:",
            f"{min_duration:.1f}h"
        )
        timing_table.add_row(
            "Max Hold Time:",
            f"{max_duration:.1f}h"
        )
        timing_table.add_row(
            "Best Weekday:",
            weekday_stats['best_day']
        )
        timing_table.add_row(
            "Worst Weekday:",
            weekday_stats['worst_day']
        )
        
        return Panel(
            timing_table,
            title="⏰ Timing Analysis",
            style="orange"
        )
    
    def get_trade_statistics(self, trade_history: List[Any]) -> Dict[str, Any]:
        """거래 통계 반환"""
        if not trade_history:
            return {}
        
        # 기본 통계
        total_trades = len(trade_history)
        winning_trades = [t for t in trade_history if t.pnl > 0]
        losing_trades = [t for t in trade_history if t.pnl <= 0]
        
        # 손익 분석
        total_pnl = sum(t.pnl for t in trade_history)
        gross_profit = sum(t.pnl for t in winning_trades)
        gross_loss = sum(t.pnl for t in losing_trades)
        
        # 최대 승/패
        max_win = max((t.pnl for t in winning_trades), default=0)
        max_loss = min((t.pnl for t in losing_trades), default=0)
        
        # 연속 분석
        max_consecutive_wins, max_consecutive_losses = self._calculate_consecutive(trade_history)
        
        return {
            'total_trades': total_trades,
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'win_rate': len(winning_trades) / total_trades if total_trades > 0 else 0,
            'total_pnl': total_pnl,
            'gross_profit': gross_profit,
            'gross_loss': gross_loss,
            'avg_win': gross_profit / len(winning_trades) if winning_trades else 0,
            'avg_loss': gross_loss / len(losing_trades) if losing_trades else 0,
            'max_win': max_win,
            'max_loss': max_loss,
            'profit_factor': gross_profit / abs(gross_loss) if gross_loss != 0 else float('inf'),
            'max_consecutive_wins': max_consecutive_wins,
            'max_consecutive_losses': max_consecutive_losses
        }
    
    def _analyze_weekday_performance(self, trade_history: List[Any]) -> Dict[str, str]:
        """요일별 성과 분석"""
        weekday_pnl = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0}  # 월요일=0
        weekday_names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        
        for trade in trade_history:
            weekday = trade.exit_date.weekday()
            weekday_pnl[weekday] += trade.pnl
        
        if all(pnl == 0 for pnl in weekday_pnl.values()):
            return {'best_day': 'N/A', 'worst_day': 'N/A'}
        
        best_day_idx = max(weekday_pnl, key=weekday_pnl.get)
        worst_day_idx = min(weekday_pnl, key=weekday_pnl.get)
        
        return {
            'best_day': weekday_names[best_day_idx],
            'worst_day': weekday_names[worst_day_idx]
        }
    
    def _calculate_consecutive(self, trade_history: List[Any]) -> tuple:
        """연속 승/패 계산"""
        if not trade_history:
            return 0, 0
        
        max_wins = 0
        max_losses = 0
        current_wins = 0
        current_losses = 0
        
        for trade in trade_history:
            if trade.pnl > 0:
                current_wins += 1
                current_losses = 0
                max_wins = max(max_wins, current_wins)
            else:
                current_losses += 1
                current_wins = 0
                max_losses = max(max_losses, current_losses)
        
        return max_wins, max_losses
    
    def create_performance_heatmap_data(self, trade_history: List[Any]) -> Dict[str, Any]:
        """성과 히트맵 데이터 생성"""
        if not trade_history:
            return {}
        
        # 월별, 요일별 성과 매트릭스
        monthly_data = {}
        hourly_data = {i: 0 for i in range(24)}
        
        for trade in trade_history:
            # 월별 데이터
            month_key = trade.exit_date.strftime('%Y-%m')
            if month_key not in monthly_data:
                monthly_data[month_key] = 0
            monthly_data[month_key] += trade.pnl
            
            # 시간별 데이터
            hour = trade.exit_date.hour
            hourly_data[hour] += trade.pnl
        
        return {
            'monthly_performance': monthly_data,
            'hourly_performance': hourly_data
        }
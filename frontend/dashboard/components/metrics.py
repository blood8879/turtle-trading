"""
성과 지표 컴포넌트
"""

from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, BarColumn, TextColumn
from typing import Dict, Any, List
from datetime import datetime, timedelta
import math

class MetricsComponent:
    """성과 지표 컴포넌트"""
    
    def __init__(self):
        self.trade_history = []
        self.daily_balances = []
        self.peak_balance = 0.0
        self.start_time = datetime.now()
    
    async def update_data(self, trade_history: List[Any], current_balance: float = 0.0):
        """지표 데이터 업데이트"""
        self.trade_history = trade_history
        
        # 일일 잔고 기록 (매일 자정에 기록)
        today = datetime.now().date()
        if not self.daily_balances or self.daily_balances[-1]['date'] != today:
            self.daily_balances.append({
                'date': today,
                'balance': current_balance
            })
        else:
            # 오늘 잔고 업데이트
            self.daily_balances[-1]['balance'] = current_balance
        
        # 최고 잔고 업데이트
        self.peak_balance = max(self.peak_balance, current_balance)
    
    def get_metrics_data(self) -> Dict[str, Any]:
        """성과 지표 데이터 반환"""
        if not self.trade_history:
            return self._get_empty_metrics()
        
        # 기본 거래 통계
        total_trades = len(self.trade_history)
        winning_trades = [t for t in self.trade_history if t.pnl > 0]
        losing_trades = [t for t in self.trade_history if t.pnl <= 0]
        
        win_rate = len(winning_trades) / total_trades if total_trades > 0 else 0
        
        # 롱/숏 분석
        long_trades = [t for t in self.trade_history if t.direction == "LONG"]
        short_trades = [t for t in self.trade_history if t.direction == "SHORT"]
        
        long_winners = [t for t in long_trades if t.pnl > 0]
        short_winners = [t for t in short_trades if t.pnl > 0]
        
        long_win_rate = len(long_winners) / len(long_trades) if long_trades else 0
        short_win_rate = len(short_winners) / len(short_trades) if short_trades else 0
        
        # 수익/손실 통계
        avg_win = sum(t.pnl for t in winning_trades) / len(winning_trades) if winning_trades else 0
        avg_loss = sum(t.pnl for t in losing_trades) / len(losing_trades) if losing_trades else 0
        
        # 수익 팩터
        gross_profit = sum(t.pnl for t in winning_trades)
        gross_loss = abs(sum(t.pnl for t in losing_trades))
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')
        
        # 롱/숏별 수익비 계산
        long_losing_trades = [t for t in long_trades if t.pnl <= 0]
        short_losing_trades = [t for t in short_trades if t.pnl <= 0]
        
        long_gross_profit = sum(t.pnl for t in long_winners)
        long_gross_loss = abs(sum(t.pnl for t in long_losing_trades))
        short_gross_profit = sum(t.pnl for t in short_winners)
        short_gross_loss = abs(sum(t.pnl for t in short_losing_trades))
        
        long_profit_ratio = long_gross_profit / long_gross_loss if long_gross_loss > 0 else float('inf')
        short_profit_ratio = short_gross_profit / short_gross_loss if short_gross_loss > 0 else float('inf')
        
        # 샤프 비율 (간단 계산)
        sharpe_ratio = self._calculate_sharpe_ratio()
        
        # 드로다운
        max_drawdown, current_drawdown = self._calculate_drawdowns()
        
        # 연속 승/패
        max_consecutive_wins, max_consecutive_losses = self._calculate_consecutive_trades()
        
        return {
            'total_trades': total_trades,
            'win_rate': win_rate,
            'long_win_rate': long_win_rate,
            'short_win_rate': short_win_rate,
            'long_profit_ratio': long_profit_ratio,
            'short_profit_ratio': short_profit_ratio,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'profit_factor': profit_factor,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'current_drawdown': current_drawdown,
            'max_consecutive_wins': max_consecutive_wins,
            'max_consecutive_losses': max_consecutive_losses,
            'long_trades': len(long_trades),
            'short_trades': len(short_trades)
        }
    
    def create_metrics_panel(self, trade_history: List[Any], current_balance: float = 0.0) -> Panel:
        """성과 지표 패널 생성"""
        # 데이터 업데이트
        import asyncio
        asyncio.create_task(self.update_data(trade_history, current_balance))
        
        metrics_data = self.get_metrics_data()
        
        # 2열 레이아웃 테이블
        metrics_table = Table.grid()
        metrics_table.add_column(style="cyan", width=18)
        metrics_table.add_column(style="bold", width=12)
        metrics_table.add_column(style="cyan", width=18)
        metrics_table.add_column(style="bold", width=12)
        
        # 첫 번째 행: 승률과 샤프 비율
        win_rate_color = self._get_win_rate_color(metrics_data['win_rate'])
        sharpe_color = self._get_sharpe_color(metrics_data['sharpe_ratio'])
        
        metrics_table.add_row(
            "Win Rate (Total):",
            f"[{win_rate_color}]{metrics_data['win_rate']:.0%}[/{win_rate_color}]",
            "Sharpe Ratio:",
            f"[{sharpe_color}]{metrics_data['sharpe_ratio']:.2f}[/{sharpe_color}]"
        )
        
        # 두 번째 행: 롱/숏 승률과 수익비
        long_profit_ratio = metrics_data.get('long_profit_ratio', 0.0)
        short_profit_ratio = metrics_data.get('short_profit_ratio', 0.0)
        
        metrics_table.add_row(
            "Long Win Rate:",
            f"{metrics_data['long_win_rate']:.0%}",
            "Long Profit Ratio:",
            f"{long_profit_ratio:.2f}"
        )
        
        # 세 번째 행: 숏 승률과 숏 수익비
        metrics_table.add_row(
            "Short Win Rate:",
            f"{metrics_data['short_win_rate']:.0%}",
            "Short Profit Ratio:",
            f"{short_profit_ratio:.2f}"
        )
        
        # 네 번째 행: 수익 팩터와 총 거래 수
        pf_color = self._get_profit_factor_color(metrics_data['profit_factor'])
        
        metrics_table.add_row(
            "Profit Factor:",
            f"[{pf_color}]{metrics_data['profit_factor']:.2f}[/{pf_color}]",
            "Total Trades:",
            f"{metrics_data['total_trades']}"
        )
        
        # 다섯 번째 행: 드로다운
        max_dd_color = self._get_drawdown_color(metrics_data['max_drawdown'])
        current_dd_color = self._get_drawdown_color(metrics_data['current_drawdown'])
        
        metrics_table.add_row(
            "Max Drawdown:",
            f"[{max_dd_color}]{metrics_data['max_drawdown']:.1%}[/{max_dd_color}]",
            "Current DD:",
            f"[{current_dd_color}]{metrics_data['current_drawdown']:.1%}[/{current_dd_color}]"
        )
        
        # 여섯 번째 행: 평균 손익
        avg_win_color = "green" if metrics_data['avg_win'] > 0 else "white"
        avg_loss_color = "red" if metrics_data['avg_loss'] < 0 else "white"
        
        metrics_table.add_row(
            "Avg Win:",
            f"[{avg_win_color}]${metrics_data['avg_win']:+.0f}[/{avg_win_color}]",
            "Avg Loss:",
            f"[{avg_loss_color}]${metrics_data['avg_loss']:+.0f}[/{avg_loss_color}]"
        )
        
        return Panel(
            metrics_table,
            title="📈 Performance Metrics",
            title_align="left",
            style="yellow"
        )
    
    def create_advanced_metrics_panel(self) -> Panel:
        """고급 성과 지표 패널"""
        metrics_data = self.get_metrics_data()
        
        # 위험 조정 수익률
        risk_adjusted_return = self._calculate_risk_adjusted_return()
        
        # 월별 성과
        monthly_performance = self._calculate_monthly_performance()
        
        # 연속 거래 분석
        consecutive_data = self._get_consecutive_analysis()
        
        advanced_table = Table.grid()
        advanced_table.add_column(style="cyan", width=20)
        advanced_table.add_column(style="bold", width=15)
        
        advanced_table.add_row(
            "Risk-Adj Return:",
            f"{risk_adjusted_return:.2%}"
        )
        advanced_table.add_row(
            "Best Month:",
            f"{monthly_performance['best']:.2%}"
        )
        advanced_table.add_row(
            "Worst Month:",
            f"{monthly_performance['worst']:.2%}"
        )
        advanced_table.add_row(
            "Max Consecutive Wins:",
            f"[green]{consecutive_data['max_wins']}[/green]"
        )
        advanced_table.add_row(
            "Max Consecutive Losses:",
            f"[red]{consecutive_data['max_losses']}[/red]"
        )
        advanced_table.add_row(
            "Current Streak:",
            f"{consecutive_data['current_streak_desc']}"
        )
        
        return Panel(
            advanced_table,
            title="🔍 Advanced Metrics",
            style="magenta"
        )
    
    def create_performance_progress_panel(self, target_return: float = 0.20) -> Panel:
        """성과 진행률 패널"""
        if not self.trade_history:
            return Panel(
                "No data available",
                title="📊 Performance Progress"
            )
        
        # 현재 수익률 계산
        total_pnl = sum(t.pnl for t in self.trade_history)
        # 초기 자금은 설정에서 가져와야 하지만 여기서는 임시로 10000 사용
        initial_balance = 10000.0
        current_return = total_pnl / initial_balance
        
        # 진행률 계산
        progress_ratio = min(current_return / target_return, 1.0) if target_return > 0 else 0
        
        # Progress bar 생성
        progress = Progress(
            TextColumn("[bold blue]Annual Target Progress"),
            BarColumn(bar_width=30),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        )
        
        task = progress.add_task("Target Progress", completed=progress_ratio * 100, total=100)
        
        # 추가 정보
        progress_info = (
            f"Current Return: {current_return:.2%}\n"
            f"Target Return: {target_return:.2%}\n"
            f"Remaining: {target_return - current_return:.2%}"
        )
        
        return Panel(
            f"{progress}\n\n{progress_info}",
            title="🎯 Performance Target",
            style="green"
        )
    
    def _get_empty_metrics(self) -> Dict[str, Any]:
        """빈 지표 데이터 반환"""
        return {
            'total_trades': 0,
            'win_rate': 0.0,
            'long_win_rate': 0.0,
            'short_win_rate': 0.0,
            'long_profit_ratio': 0.0,
            'short_profit_ratio': 0.0,
            'avg_win': 0.0,
            'avg_loss': 0.0,
            'profit_factor': 0.0,
            'sharpe_ratio': 0.0,
            'max_drawdown': 0.0,
            'current_drawdown': 0.0,
            'max_consecutive_wins': 0,
            'max_consecutive_losses': 0,
            'long_trades': 0,
            'short_trades': 0
        }
    
    def _calculate_sharpe_ratio(self) -> float:
        """샤프 비율 계산 (간단 버전)"""
        if len(self.trade_history) < 2:
            return 0.0
        
        # 거래별 수익률 계산
        returns = [t.pnl for t in self.trade_history]
        
        if not returns:
            return 0.0
        
        mean_return = sum(returns) / len(returns)
        variance = sum((r - mean_return) ** 2 for r in returns) / len(returns)
        std_dev = math.sqrt(variance)
        
        if std_dev == 0:
            return 0.0
        
        # 무위험 수익률은 0으로 가정
        return mean_return / std_dev
    
    def _calculate_drawdowns(self) -> tuple:
        """최대 드로다운과 현재 드로다운 계산"""
        if not self.daily_balances:
            return 0.0, 0.0
        
        peak = 0.0
        max_drawdown = 0.0
        current_drawdown = 0.0
        
        for balance_data in self.daily_balances:
            balance = balance_data['balance']
            
            if balance > peak:
                peak = balance
            
            if peak > 0:
                drawdown = (peak - balance) / peak
                max_drawdown = max(max_drawdown, drawdown)
        
        # 현재 드로다운
        if self.daily_balances:
            current_balance = self.daily_balances[-1]['balance']
            if self.peak_balance > 0:
                current_drawdown = (self.peak_balance - current_balance) / self.peak_balance
        
        return max_drawdown, current_drawdown
    
    def _calculate_consecutive_trades(self) -> tuple:
        """연속 승/패 계산"""
        if not self.trade_history:
            return 0, 0
        
        max_wins = 0
        max_losses = 0
        current_wins = 0
        current_losses = 0
        
        for trade in self.trade_history:
            if trade.pnl > 0:
                current_wins += 1
                current_losses = 0
                max_wins = max(max_wins, current_wins)
            else:
                current_losses += 1
                current_wins = 0
                max_losses = max(max_losses, current_losses)
        
        return max_wins, max_losses
    
    def _calculate_risk_adjusted_return(self) -> float:
        """위험 조정 수익률 계산"""
        if not self.trade_history:
            return 0.0
        
        total_return = sum(t.pnl for t in self.trade_history) / 10000.0  # 임시 초기 자금
        max_dd, _ = self._calculate_drawdowns()
        
        if max_dd == 0:
            return total_return
        
        return total_return / max_dd
    
    def _calculate_monthly_performance(self) -> Dict[str, float]:
        """월별 성과 계산"""
        if not self.trade_history:
            return {'best': 0.0, 'worst': 0.0, 'average': 0.0}
        
        monthly_pnl = {}
        
        for trade in self.trade_history:
            month_key = trade.exit_date.strftime('%Y-%m')
            if month_key not in monthly_pnl:
                monthly_pnl[month_key] = 0.0
            monthly_pnl[month_key] += trade.pnl
        
        if not monthly_pnl:
            return {'best': 0.0, 'worst': 0.0, 'average': 0.0}
        
        # 수익률로 변환 (임시 월 시작 자금 10000 사용)
        monthly_returns = [pnl / 10000.0 for pnl in monthly_pnl.values()]
        
        return {
            'best': max(monthly_returns),
            'worst': min(monthly_returns),
            'average': sum(monthly_returns) / len(monthly_returns)
        }
    
    def _get_consecutive_analysis(self) -> Dict[str, Any]:
        """연속 거래 분석"""
        max_wins, max_losses = self._calculate_consecutive_trades()
        
        # 현재 연속 상태
        current_streak = 0
        current_streak_type = "None"
        
        if self.trade_history:
            for trade in reversed(self.trade_history):
                if current_streak == 0:
                    current_streak = 1
                    current_streak_type = "Win" if trade.pnl > 0 else "Loss"
                else:
                    if (current_streak_type == "Win" and trade.pnl > 0) or \
                       (current_streak_type == "Loss" and trade.pnl <= 0):
                        current_streak += 1
                    else:
                        break
        
        streak_color = "green" if current_streak_type == "Win" else "red"
        current_streak_desc = f"[{streak_color}]{current_streak} {current_streak_type}(s)[/{streak_color}]"
        
        return {
            'max_wins': max_wins,
            'max_losses': max_losses,
            'current_streak': current_streak,
            'current_streak_type': current_streak_type,
            'current_streak_desc': current_streak_desc
        }
    
    # 색상 결정 헬퍼 메서드들
    def _get_win_rate_color(self, win_rate: float) -> str:
        if win_rate > 0.6:
            return "green"
        elif win_rate > 0.5:
            return "yellow"
        else:
            return "red"
    
    def _get_sharpe_color(self, sharpe: float) -> str:
        if sharpe > 1.5:
            return "green"
        elif sharpe > 1.0:
            return "yellow"
        else:
            return "red"
    
    def _get_profit_factor_color(self, pf: float) -> str:
        if pf > 1.5:
            return "green"
        elif pf > 1.0:
            return "yellow"
        else:
            return "red"
    
    def _get_drawdown_color(self, dd: float) -> str:
        if dd < 0.05:
            return "green"
        elif dd < 0.15:
            return "yellow"
        else:
            return "red"
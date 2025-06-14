"""
상세 거래 분석 컴포넌트
백테스트 결과에서 모든 거래의 세부 정보를 분석하고 표시
"""

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Prompt
from typing import List, Dict, Any
from datetime import datetime
from dataclasses import dataclass

@dataclass
class DetailedTradeAnalysis:
    """상세 거래 분석 결과"""
    # 전체 통계
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    
    # 롱/숏 분석
    long_trades: int
    long_winning: int
    long_win_rate: float
    long_total_pnl: float
    long_avg_pnl: float
    
    short_trades: int
    short_winning: int
    short_win_rate: float
    short_total_pnl: float
    short_avg_pnl: float
    
    # 시스템별 분석
    system1_trades: int
    system1_win_rate: float
    system1_total_pnl: float
    
    system2_trades: int
    system2_win_rate: float
    system2_total_pnl: float
    
    # 청산 사유별 분석
    signal_exits: int
    stop_loss_exits: int
    backtest_end_exits: int
    
    # 연속 거래 분석
    max_consecutive_wins: int
    max_consecutive_losses: int
    current_streak: int
    current_streak_type: str
    
    # 월별/일별 통계
    best_day_pnl: float
    worst_day_pnl: float
    avg_trade_duration: float
    
    # 상세 거래 내역
    detailed_trades: List[Dict[str, Any]]

class DetailedTradeAnalyzer:
    """상세 거래 분석기"""
    
    def __init__(self):
        self.console = Console()
    
    def analyze_trades(self, trades: List[Any]) -> DetailedTradeAnalysis:
        """거래 내역을 상세 분석"""
        if not trades:
            return self._get_empty_analysis()
        
        # 기본 통계
        total_trades = len(trades)
        winning_trades = [t for t in trades if t.pnl > 0]
        losing_trades = [t for t in trades if t.pnl <= 0]
        win_rate = len(winning_trades) / total_trades
        
        # 롱/숏 분석
        long_trades = [t for t in trades if t.direction == "LONG"]
        short_trades = [t for t in trades if t.direction == "SHORT"]
        
        long_winning = [t for t in long_trades if t.pnl > 0]
        short_winning = [t for t in short_trades if t.pnl > 0]
        
        long_win_rate = len(long_winning) / len(long_trades) if long_trades else 0
        short_win_rate = len(short_winning) / len(short_trades) if short_trades else 0
        
        long_total_pnl = sum(t.pnl for t in long_trades)
        short_total_pnl = sum(t.pnl for t in short_trades)
        
        long_avg_pnl = long_total_pnl / len(long_trades) if long_trades else 0
        short_avg_pnl = short_total_pnl / len(short_trades) if short_trades else 0
        
        # 시스템별 분석
        system1_trades = [t for t in trades if t.system == 1]
        system2_trades = [t for t in trades if t.system == 2]
        
        system1_winning = [t for t in system1_trades if t.pnl > 0]
        system2_winning = [t for t in system2_trades if t.pnl > 0]
        
        system1_win_rate = len(system1_winning) / len(system1_trades) if system1_trades else 0
        system2_win_rate = len(system2_winning) / len(system2_trades) if system2_trades else 0
        
        system1_total_pnl = sum(t.pnl for t in system1_trades)
        system2_total_pnl = sum(t.pnl for t in system2_trades)
        
        # 청산 사유별 분석
        signal_exits = len([t for t in trades if t.exit_reason == "SIGNAL"])
        stop_loss_exits = len([t for t in trades if t.exit_reason == "STOP_LOSS"])
        backtest_end_exits = len([t for t in trades if t.exit_reason == "BACKTEST_END"])
        
        # 연속 거래 분석
        max_consecutive_wins, max_consecutive_losses, current_streak, current_streak_type = self._analyze_consecutive_trades(trades)
        
        # 최고/최악 거래
        best_day_pnl = max(t.pnl for t in trades)
        worst_day_pnl = min(t.pnl for t in trades)
        
        # 평균 거래 기간
        if trades:
            trade_durations = [(t.exit_date - t.entry_date).days for t in trades]
            avg_trade_duration = sum(trade_durations) / len(trade_durations)
        else:
            avg_trade_duration = 0
        
        # 상세 거래 내역 생성
        detailed_trades = self._create_detailed_trade_list(trades)
        
        return DetailedTradeAnalysis(
            total_trades=total_trades,
            winning_trades=len(winning_trades),
            losing_trades=len(losing_trades),
            win_rate=win_rate,
            long_trades=len(long_trades),
            long_winning=len(long_winning),
            long_win_rate=long_win_rate,
            long_total_pnl=long_total_pnl,
            long_avg_pnl=long_avg_pnl,
            short_trades=len(short_trades),
            short_winning=len(short_winning),
            short_win_rate=short_win_rate,
            short_total_pnl=short_total_pnl,
            short_avg_pnl=short_avg_pnl,
            system1_trades=len(system1_trades),
            system1_win_rate=system1_win_rate,
            system1_total_pnl=system1_total_pnl,
            system2_trades=len(system2_trades),
            system2_win_rate=system2_win_rate,
            system2_total_pnl=system2_total_pnl,
            signal_exits=signal_exits,
            stop_loss_exits=stop_loss_exits,
            backtest_end_exits=backtest_end_exits,
            max_consecutive_wins=max_consecutive_wins,
            max_consecutive_losses=max_consecutive_losses,
            current_streak=current_streak,
            current_streak_type=current_streak_type,
            best_day_pnl=best_day_pnl,
            worst_day_pnl=worst_day_pnl,
            avg_trade_duration=avg_trade_duration,
            detailed_trades=detailed_trades
        )
    
    def display_detailed_analysis(self, analysis: DetailedTradeAnalysis):
        """상세 분석 결과 표시"""
        self.console.clear()
        self.console.print(Panel("📊 터틀 트레이딩 상세 거래 분석", style="cyan bold"))
        self.console.print()
        
        # 1. 전체 통계
        self._show_overall_statistics(analysis)
        
        # 2. 롱/숏 포지션 비교
        self._show_long_short_comparison(analysis)
        
        # 3. 시스템별 성과
        self._show_system_performance(analysis)
        
        # 4. 청산 사유 분석
        self._show_exit_reason_analysis(analysis)
        
        # 5. 연속 거래 분석
        self._show_consecutive_analysis(analysis)
        
        # 6. 최고/최악 거래
        self._show_best_worst_trades(analysis)
        
        Prompt.ask("\n[dim]엔터를 눌러 상세 거래 내역을 보세요...[/dim]", default="")
        
        # 7. 상세 거래 내역 (페이지네이션)
        self._show_detailed_trades(analysis.detailed_trades)
    
    def _show_overall_statistics(self, analysis: DetailedTradeAnalysis):
        """전체 통계 표시"""
        table = Table(title="📈 전체 거래 통계", title_style="bold yellow")
        table.add_column("지표", style="cyan", width=20)
        table.add_column("값", style="bold white", width=15)
        table.add_column("백분율", style="green", width=15)
        table.add_column("평가", style="dim", width=20)
        
        win_rate_color = "green" if analysis.win_rate > 0.5 else "yellow" if analysis.win_rate > 0.4 else "red"
        
        table.add_row(
            "총 거래 수",
            f"{analysis.total_trades}회",
            "100%",
            "전체 거래 건수"
        )
        table.add_row(
            "승리 거래",
            f"{analysis.winning_trades}회",
            f"[green]{analysis.winning_trades/analysis.total_trades:.1%}[/green]",
            "수익 거래"
        )
        table.add_row(
            "패배 거래",
            f"{analysis.losing_trades}회",
            f"[red]{analysis.losing_trades/analysis.total_trades:.1%}[/red]",
            "손실 거래"
        )
        table.add_row(
            "전체 승률",
            f"[{win_rate_color}]{analysis.win_rate:.1%}[/{win_rate_color}]",
            "-",
            self._evaluate_win_rate(analysis.win_rate)
        )
        table.add_row(
            "평균 거래 기간",
            f"{analysis.avg_trade_duration:.1f}일",
            "-",
            "평균 포지션 보유기간"
        )
        
        self.console.print(table)
        self.console.print()
    
    def _show_long_short_comparison(self, analysis: DetailedTradeAnalysis):
        """롱/숏 포지션 비교"""
        table = Table(title="🔄 롱/숏 포지션 성과 비교", title_style="bold yellow")
        table.add_column("지표", style="cyan", width=20)
        table.add_column("롱 포지션", style="green", width=20)
        table.add_column("숏 포지션", style="red", width=20)
        table.add_column("우세", style="bold", width=15)
        
        better_trades = "롱" if analysis.long_trades > analysis.short_trades else "숏" if analysis.short_trades > analysis.long_trades else "동일"
        better_winrate = "롱" if analysis.long_win_rate > analysis.short_win_rate else "숏" if analysis.short_win_rate > analysis.long_win_rate else "동일"
        better_pnl = "롱" if analysis.long_total_pnl > analysis.short_total_pnl else "숏" if analysis.short_total_pnl > analysis.long_total_pnl else "동일"
        better_avg = "롱" if analysis.long_avg_pnl > analysis.short_avg_pnl else "숏" if analysis.short_avg_pnl > analysis.long_avg_pnl else "동일"
        
        table.add_row(
            "거래 수",
            f"{analysis.long_trades}회",
            f"{analysis.short_trades}회",
            f"[bold]{better_trades}[/bold]"
        )
        table.add_row(
            "승률",
            f"{analysis.long_win_rate:.1%}",
            f"{analysis.short_win_rate:.1%}",
            f"[bold]{better_winrate}[/bold]"
        )
        table.add_row(
            "총 손익",
            f"[green]${analysis.long_total_pnl:+,.0f}[/green]" if analysis.long_total_pnl > 0 else f"[red]${analysis.long_total_pnl:+,.0f}[/red]",
            f"[green]${analysis.short_total_pnl:+,.0f}[/green]" if analysis.short_total_pnl > 0 else f"[red]${analysis.short_total_pnl:+,.0f}[/red]",
            f"[bold]{better_pnl}[/bold]"
        )
        table.add_row(
            "평균 손익",
            f"[green]${analysis.long_avg_pnl:+,.0f}[/green]" if analysis.long_avg_pnl > 0 else f"[red]${analysis.long_avg_pnl:+,.0f}[/red]",
            f"[green]${analysis.short_avg_pnl:+,.0f}[/green]" if analysis.short_avg_pnl > 0 else f"[red]${analysis.short_avg_pnl:+,.0f}[/red]",
            f"[bold]{better_avg}[/bold]"
        )
        
        self.console.print(table)
        self.console.print()
    
    def _show_system_performance(self, analysis: DetailedTradeAnalysis):
        """시스템별 성과"""
        table = Table(title="⚙️ 시스템별 성과 비교", title_style="bold yellow")
        table.add_column("지표", style="cyan", width=20)
        table.add_column("시스템 1 (20일)", style="blue", width=20)
        table.add_column("시스템 2 (55일)", style="purple", width=20)
        table.add_column("우세", style="bold", width=15)
        
        better_s_trades = "S1" if analysis.system1_trades > analysis.system2_trades else "S2" if analysis.system2_trades > analysis.system1_trades else "동일"
        better_s_winrate = "S1" if analysis.system1_win_rate > analysis.system2_win_rate else "S2" if analysis.system2_win_rate > analysis.system1_win_rate else "동일"
        better_s_pnl = "S1" if analysis.system1_total_pnl > analysis.system2_total_pnl else "S2" if analysis.system2_total_pnl > analysis.system1_total_pnl else "동일"
        
        table.add_row(
            "거래 수",
            f"{analysis.system1_trades}회",
            f"{analysis.system2_trades}회",
            f"[bold]{better_s_trades}[/bold]"
        )
        table.add_row(
            "승률",
            f"{analysis.system1_win_rate:.1%}",
            f"{analysis.system2_win_rate:.1%}",
            f"[bold]{better_s_winrate}[/bold]"
        )
        table.add_row(
            "총 손익",
            f"[green]${analysis.system1_total_pnl:+,.0f}[/green]" if analysis.system1_total_pnl > 0 else f"[red]${analysis.system1_total_pnl:+,.0f}[/red]",
            f"[green]${analysis.system2_total_pnl:+,.0f}[/green]" if analysis.system2_total_pnl > 0 else f"[red]${analysis.system2_total_pnl:+,.0f}[/red]",
            f"[bold]{better_s_pnl}[/bold]"
        )
        
        avg_s1 = analysis.system1_total_pnl / analysis.system1_trades if analysis.system1_trades else 0
        avg_s2 = analysis.system2_total_pnl / analysis.system2_trades if analysis.system2_trades else 0
        better_avg_s = "S1" if avg_s1 > avg_s2 else "S2" if avg_s2 > avg_s1 else "동일"
        
        table.add_row(
            "평균 거래당 손익",
            f"[green]${avg_s1:+,.0f}[/green]" if avg_s1 > 0 else f"[red]${avg_s1:+,.0f}[/red]",
            f"[green]${avg_s2:+,.0f}[/green]" if avg_s2 > 0 else f"[red]${avg_s2:+,.0f}[/red]",
            f"[bold]{better_avg_s}[/bold]"
        )
        
        self.console.print(table)
        self.console.print()
    
    def _show_exit_reason_analysis(self, analysis: DetailedTradeAnalysis):
        """청산 사유 분석"""
        table = Table(title="🚪 청산 사유별 분석", title_style="bold yellow")
        table.add_column("청산 사유", style="cyan", width=20)
        table.add_column("거래 수", style="white", width=15)
        table.add_column("비율", style="green", width=15)
        table.add_column("설명", style="dim", width=30)
        
        total = analysis.total_trades
        
        table.add_row(
            "시그널 청산",
            f"{analysis.signal_exits}회",
            f"{analysis.signal_exits/total:.1%}" if total > 0 else "0%",
            "브레이크아웃 시그널에 의한 청산"
        )
        table.add_row(
            "손절 청산",
            f"[red]{analysis.stop_loss_exits}회[/red]",
            f"[red]{analysis.stop_loss_exits/total:.1%}[/red]" if total > 0 else "0%",
            "2N 스톱로스에 의한 청산"
        )
        table.add_row(
            "백테스트 종료",
            f"{analysis.backtest_end_exits}회",
            f"{analysis.backtest_end_exits/total:.1%}" if total > 0 else "0%",
            "백테스트 기간 종료시 강제 청산"
        )
        
        self.console.print(table)
        self.console.print()
    
    def _show_consecutive_analysis(self, analysis: DetailedTradeAnalysis):
        """연속 거래 분석"""
        table = Table(title="🔄 연속 거래 분석", title_style="bold yellow")
        table.add_column("지표", style="cyan", width=25)
        table.add_column("값", style="bold", width=20)
        table.add_column("평가", style="dim", width=25)
        
        streak_color = "green" if analysis.current_streak_type == "Win" else "red"
        
        table.add_row(
            "최대 연속 승리",
            f"[green]{analysis.max_consecutive_wins}회[/green]",
            "최대 연속 수익 거래"
        )
        table.add_row(
            "최대 연속 패배",
            f"[red]{analysis.max_consecutive_losses}회[/red]",
            "최대 연속 손실 거래"
        )
        table.add_row(
            "현재 연속 상태",
            f"[{streak_color}]{analysis.current_streak}회 {analysis.current_streak_type}[/{streak_color}]",
            "현재 진행중인 연속 결과"
        )
        
        self.console.print(table)
        self.console.print()
    
    def _show_best_worst_trades(self, analysis: DetailedTradeAnalysis):
        """최고/최악 거래"""
        table = Table(title="🏆 최고/최악 거래", title_style="bold yellow")
        table.add_column("구분", style="cyan", width=15)
        table.add_column("손익", style="bold", width=20)
        table.add_column("평가", style="dim", width=35)
        
        table.add_row(
            "최고 수익 거래",
            f"[green]${analysis.best_day_pnl:+,.0f}[/green]",
            "단일 거래 최대 수익"
        )
        table.add_row(
            "최대 손실 거래",
            f"[red]${analysis.worst_day_pnl:+,.0f}[/red]",
            "단일 거래 최대 손실"
        )
        
        profit_loss_ratio = abs(analysis.best_day_pnl / analysis.worst_day_pnl) if analysis.worst_day_pnl != 0 else 0
        table.add_row(
            "수익/손실 비율",
            f"{profit_loss_ratio:.2f}",
            "최대수익 ÷ 최대손실"
        )
        
        self.console.print(table)
        self.console.print()
    
    def _show_detailed_trades(self, detailed_trades: List[Dict[str, Any]]):
        """상세 거래 내역 표시 (페이지네이션)"""
        if not detailed_trades:
            self.console.print("[yellow]거래 내역이 없습니다.[/yellow]")
            return
        
        self.console.clear()
        self.console.print(Panel(f"📋 상세 거래 내역 ({len(detailed_trades)}건)", style="cyan"))
        
        page_size = 15
        total_pages = (len(detailed_trades) + page_size - 1) // page_size
        current_page = 1
        
        while True:
            start_idx = (current_page - 1) * page_size
            end_idx = min(start_idx + page_size, len(detailed_trades))
            page_trades = detailed_trades[start_idx:end_idx]
            
            trades_table = Table(title=f"페이지 {current_page}/{total_pages}")
            trades_table.add_column("#", style="dim", width=4)
            trades_table.add_column("진입일", style="cyan", width=10)
            trades_table.add_column("청산일", style="cyan", width=10)
            trades_table.add_column("방향", style="white", width=5)
            trades_table.add_column("진입가", style="blue", width=10)
            trades_table.add_column("청산가", style="blue", width=10)
            trades_table.add_column("기간", style="yellow", width=5)
            trades_table.add_column("손익", style="bold", width=10)
            trades_table.add_column("S", style="purple", width=3)
            trades_table.add_column("사유", style="dim", width=8)
            
            for i, trade in enumerate(page_trades, start_idx + 1):
                pnl_color = "green" if trade['pnl'] > 0 else "red"
                direction_color = "green" if trade['direction'] == "LONG" else "red"
                
                trades_table.add_row(
                    str(i),
                    trade['entry_date'],
                    trade['exit_date'],
                    f"[{direction_color}]{trade['direction'][:1]}[/{direction_color}]",
                    f"${trade['entry_price']:,.0f}",
                    f"${trade['exit_price']:,.0f}",
                    f"{trade['duration']}일",
                    f"[{pnl_color}]{trade['pnl']:+.0f}[/{pnl_color}]",
                    str(trade['system']),
                    trade['exit_reason'][:6]
                )
            
            self.console.print(trades_table)
            
            # 네비게이션
            if total_pages > 1:
                nav_options = []
                if current_page > 1:
                    nav_options.extend(['p', 'prev'])
                if current_page < total_pages:
                    nav_options.extend(['n', 'next'])
                nav_options.append('q')
                
                nav_text = "["
                if current_page > 1:
                    nav_text += "P)이전 페이지 "
                if current_page < total_pages:
                    nav_text += "N)다음 페이지 "
                nav_text += "Q)돌아가기]"
                
                choice = Prompt.ask(nav_text, choices=nav_options, default='q')
                
                if choice in ['p', 'prev']:
                    current_page -= 1
                elif choice in ['n', 'next']:
                    current_page += 1
                else:
                    break
            else:
                Prompt.ask("\n[dim]엔터를 눌러 돌아가세요...[/dim]", default="")
                break
    
    def _analyze_consecutive_trades(self, trades: List[Any]) -> tuple:
        """연속 거래 분석"""
        if not trades:
            return 0, 0, 0, "None"
        
        max_wins = 0
        max_losses = 0
        current_wins = 0
        current_losses = 0
        
        for trade in trades:
            if trade.pnl > 0:
                current_wins += 1
                current_losses = 0
                max_wins = max(max_wins, current_wins)
            else:
                current_losses += 1
                current_wins = 0
                max_losses = max(max_losses, current_losses)
        
        # 현재 연속 상태 (마지막 거래부터 역순으로)
        current_streak = 0
        current_streak_type = "None"
        
        for trade in reversed(trades):
            if current_streak == 0:
                current_streak = 1
                current_streak_type = "Win" if trade.pnl > 0 else "Loss"
            else:
                if (current_streak_type == "Win" and trade.pnl > 0) or \
                   (current_streak_type == "Loss" and trade.pnl <= 0):
                    current_streak += 1
                else:
                    break
        
        return max_wins, max_losses, current_streak, current_streak_type
    
    def _create_detailed_trade_list(self, trades: List[Any]) -> List[Dict[str, Any]]:
        """상세 거래 내역 리스트 생성"""
        detailed_trades = []
        
        for trade in trades:
            duration = (trade.exit_date - trade.entry_date).days
            
            detailed_trades.append({
                'entry_date': trade.entry_date.strftime('%Y-%m-%d'),
                'exit_date': trade.exit_date.strftime('%Y-%m-%d'),
                'direction': trade.direction,
                'entry_price': trade.entry_price,
                'exit_price': trade.exit_price,
                'duration': duration,
                'pnl': trade.pnl,
                'system': trade.system,
                'exit_reason': trade.exit_reason,
                'size': trade.size,
                'symbol': trade.symbol
            })
        
        return detailed_trades
    
    def _get_empty_analysis(self) -> DetailedTradeAnalysis:
        """빈 분석 결과 반환"""
        return DetailedTradeAnalysis(
            total_trades=0, winning_trades=0, losing_trades=0, win_rate=0.0,
            long_trades=0, long_winning=0, long_win_rate=0.0, long_total_pnl=0.0, long_avg_pnl=0.0,
            short_trades=0, short_winning=0, short_win_rate=0.0, short_total_pnl=0.0, short_avg_pnl=0.0,
            system1_trades=0, system1_win_rate=0.0, system1_total_pnl=0.0,
            system2_trades=0, system2_win_rate=0.0, system2_total_pnl=0.0,
            signal_exits=0, stop_loss_exits=0, backtest_end_exits=0,
            max_consecutive_wins=0, max_consecutive_losses=0, current_streak=0, current_streak_type="None",
            best_day_pnl=0.0, worst_day_pnl=0.0, avg_trade_duration=0.0,
            detailed_trades=[]
        )
    
    def _evaluate_win_rate(self, win_rate: float) -> str:
        """승률 평가"""
        if win_rate > 0.6:
            return "매우 우수"
        elif win_rate > 0.5:
            return "우수"
        elif win_rate > 0.4:
            return "양호"
        else:
            return "개선 필요"

if __name__ == "__main__":
    # 테스트용 더미 데이터
    analyzer = DetailedTradeAnalyzer()
    analysis = analyzer._get_empty_analysis()
    analyzer.display_detailed_analysis(analysis)
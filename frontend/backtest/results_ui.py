"""
백테스트 결과 UI - Rich 라이브러리 기반 결과 표시
"""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.layout import Layout
from rich.align import Align
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.prompt import Prompt, Confirm
import matplotlib.pyplot as plt
from datetime import datetime
from typing import Dict, Any, List, Optional
import json
import os

from .backend.engines.backtest_engine import BacktestResults, PerformanceMetrics
from .detailed_trade_analysis import DetailedTradeAnalyzer

class BacktestResultsUI:
    """백테스트 결과 표시 UI"""
    
    def __init__(self):
        self.console = Console()
        self.detailed_analyzer = DetailedTradeAnalyzer()
    
    def show_progress(self, total_days: int):
        """백테스트 진행률 표시"""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=self.console
        ) as progress:
            task = progress.add_task("백테스트 실행 중...", total=total_days)
            
            for day in range(total_days):
                # 실제 백테스트에서는 yield나 callback으로 진행률 업데이트
                progress.update(task, advance=1)
            
            progress.update(task, description="백테스트 완료!")
    
    def display_results(self, results: BacktestResults) -> str:
        """백테스트 결과 표시"""
        self.console.clear()
        
        # 헤더
        self._show_header(results)
        
        # 성과 요약
        self._show_performance_summary(results)
        
        # 거래 통계
        self._show_trading_statistics(results)
        
        # 월별 수익률 (상위 최고/최악만)
        self._show_monthly_performance(results)
        
        # 최근 거래 내역 (최대 5개)
        self._show_recent_trades(results)
        
        # 액션 메뉴
        return self._show_action_menu()
    
    def _show_header(self, results: BacktestResults):
        """헤더 표시"""
        config = results.config
        
        title = Text("Bitcoin Futures Turtle Trading Bot", style="bold cyan")
        subtitle = Text("백테스트 결과", style="bold white")
        
        info = (
            f"[cyan]종목:[/cyan] {config.symbol} | "
            f"[cyan]기간:[/cyan] {config.start_date} ~ {config.end_date} | "
            f"[cyan]타임프레임:[/cyan] {config.timeframe}"
        )
        
        header_panel = Panel(
            Align.center(f"{title}\n{subtitle}\n\n{info}"),
            style="cyan",
            padding=(1, 2)
        )
        
        self.console.print(header_panel)
        self.console.print()
    
    def _show_performance_summary(self, results: BacktestResults):
        """성과 요약 표시"""
        metrics = results.metrics
        
        # 수익률 계산
        total_return = metrics.total_return * 100
        annual_return = metrics.annual_return * 100
        
        # 색상 결정
        return_color = "green" if total_return > 0 else "red"
        drawdown_color = "red" if metrics.max_drawdown > 0.15 else "yellow" if metrics.max_drawdown > 0.10 else "green"
        
        summary_table = Table(title="📊 전체 성과 요약", title_style="bold yellow")
        summary_table.add_column("지표", style="cyan", width=20)
        summary_table.add_column("값", style="bold", width=25)
        summary_table.add_column("평가", style="white", width=30)
        
        # 수익 관련
        summary_table.add_row(
            "초기 자금",
            f"${results.initial_balance:,.2f}",
            "백테스트 시작 자금"
        )
        summary_table.add_row(
            "최종 자금",
            f"[{return_color}]${results.final_balance:,.2f}[/{return_color}]",
            f"[{return_color}]{'+' if total_return > 0 else ''}{results.final_balance - results.initial_balance:,.2f}[/{return_color}]"
        )
        summary_table.add_row(
            "총 수익률",
            f"[{return_color}]{total_return:+.2f}%[/{return_color}]",
            self._evaluate_return(total_return)
        )
        summary_table.add_row(
            "연화 수익률",
            f"[{return_color}]{annual_return:+.2f}%[/{return_color}]",
            self._evaluate_annual_return(annual_return)
        )
        
        # 리스크 관련
        summary_table.add_row(
            "최대 드로다운",
            f"[{drawdown_color}]{metrics.max_drawdown:.2%}[/{drawdown_color}]",
            self._evaluate_drawdown(metrics.max_drawdown)
        )
        summary_table.add_row(
            "샤프 비율",
            f"{metrics.sharpe_ratio:.2f}",
            self._evaluate_sharpe(metrics.sharpe_ratio)
        )
        
        self.console.print(summary_table)
        self.console.print()
    
    def _show_trading_statistics(self, results: BacktestResults):
        """거래 통계 표시"""
        metrics = results.metrics
        
        trading_table = Table(title="📈 거래 통계", title_style="bold yellow")
        trading_table.add_column("지표", style="cyan", width=20)
        trading_table.add_column("전체", style="white", width=15)
        trading_table.add_column("롱 포지션", style="green", width=15)
        trading_table.add_column("숏 포지션", style="red", width=15)
        
        # 거래 수
        trading_table.add_row(
            "총 거래 수",
            f"{metrics.total_trades}번",
            f"{metrics.long_trades}번",
            f"{metrics.short_trades}번"
        )
        
        # 승률
        win_rate_color = "green" if metrics.win_rate > 0.5 else "yellow" if metrics.win_rate > 0.4 else "red"
        trading_table.add_row(
            "승률",
            f"[{win_rate_color}]{metrics.win_rate:.1%}[/{win_rate_color}]",
            f"{metrics.long_win_rate:.1%}",
            f"{metrics.short_win_rate:.1%}"
        )
        
        # 평균 손익
        trading_table.add_row(
            "평균 수익",
            f"[green]${metrics.avg_win:+.2f}[/green]",
            "-",
            "-"
        )
        trading_table.add_row(
            "평균 손실",
            f"[red]${metrics.avg_loss:+.2f}[/red]",
            "-",
            "-"
        )
        
        # 수익 팩터
        pf_color = "green" if metrics.profit_factor > 1.5 else "yellow" if metrics.profit_factor > 1.0 else "red"
        trading_table.add_row(
            "수익 팩터",
            f"[{pf_color}]{metrics.profit_factor:.2f}[/{pf_color}]",
            "-",
            "-"
        )
        
        # 연속 거래
        trading_table.add_row(
            "최대 연속 승",
            f"[green]{metrics.max_consecutive_wins}번[/green]",
            "-",
            "-"
        )
        trading_table.add_row(
            "최대 연속 패",
            f"[red]{metrics.max_consecutive_losses}번[/red]",
            "-",
            "-"
        )
        
        self.console.print(trading_table)
        self.console.print()
    
    def _show_monthly_performance(self, results: BacktestResults):
        """월별 성과 표시 (요약)"""
        monthly_returns = results.monthly_returns
        
        if not monthly_returns:
            return
        
        # 최고/최악 월 찾기
        best_month = max(monthly_returns.items(), key=lambda x: x[1])
        worst_month = min(monthly_returns.items(), key=lambda x: x[1])
        
        # 연도별 요약
        yearly_summary = {}
        for month, return_rate in monthly_returns.items():
            year = month[:4]
            if year not in yearly_summary:
                yearly_summary[year] = []
            yearly_summary[year].append(return_rate)
        
        monthly_table = Table(title="📅 월별 수익률 요약", title_style="bold yellow")
        monthly_table.add_column("구분", style="cyan", width=15)
        monthly_table.add_column("기간/연도", style="white", width=15)
        monthly_table.add_column("수익률", style="bold", width=15)
        monthly_table.add_column("비고", style="dim", width=25)
        
        # 최고 월
        monthly_table.add_row(
            "최고 월",
            best_month[0],
            f"[green]{best_month[1]:+.2%}[/green]",
            "가장 좋은 성과"
        )
        
        # 최악 월  
        monthly_table.add_row(
            "최악 월",
            worst_month[0],
            f"[red]{worst_month[1]:+.2%}[/red]",
            "가장 나쁜 성과"
        )
        
        # 연도별 요약
        for year, returns in sorted(yearly_summary.items()):
            year_return = sum(returns)
            color = "green" if year_return > 0 else "red"
            monthly_table.add_row(
                f"{year}년",
                f"{len(returns)}개월",
                f"[{color}]{year_return:+.2%}[/{color}]",
                f"월평균 {year_return/len(returns):.2%}"
            )
        
        self.console.print(monthly_table)
        self.console.print()
    
    def _show_recent_trades(self, results: BacktestResults):
        """최근 거래 내역 표시"""
        trades = results.trades[-5:]  # 최근 5개 거래
        
        if not trades:
            return
        
        trades_table = Table(title="📋 최근 거래 내역 (최근 5개)", title_style="bold yellow")
        trades_table.add_column("날짜", style="cyan", width=12)
        trades_table.add_column("방향", style="white", width=6)
        trades_table.add_column("진입가", style="blue", width=12)
        trades_table.add_column("청산가", style="blue", width=12)
        trades_table.add_column("손익", style="bold", width=12)
        trades_table.add_column("사유", style="dim", width=10)
        
        for trade in trades:
            pnl_color = "green" if trade.pnl > 0 else "red"
            direction_color = "green" if trade.direction == "LONG" else "red"
            
            trades_table.add_row(
                trade.exit_date.strftime("%m-%d"),
                f"[{direction_color}]{trade.direction}[/{direction_color}]",
                f"${trade.entry_price:,.0f}",
                f"${trade.exit_price:,.0f}",
                f"[{pnl_color}]{trade.pnl:+.0f}[/{pnl_color}]",
                trade.exit_reason[:6]
            )
        
        self.console.print(trades_table)
        self.console.print()
    
    def _show_action_menu(self) -> str:
        """액션 메뉴 표시"""
        menu_panel = Panel(
            "[bold white]백테스트 결과 메뉴[/bold white]\n\n"
            "[cyan]1.[/cyan] 상세 분석 보기\n"
            "[cyan]2.[/cyan] 거래 내역 전체 보기\n"
            "[yellow]3.[/yellow] 롱/숏 상세 거래 분석\n"
            "[cyan]4.[/cyan] 차트 생성 및 저장\n"
            "[cyan]5.[/cyan] 결과 CSV 내보내기\n"
            "[green]6.[/green] 새로운 백테스트 실행\n"
            "[blue]7.[/blue] 이 설정으로 가상매매 시작\n"
            "[red]8.[/red] 메인 메뉴로 돌아가기",
            title="다음 작업",
            style="blue"
        )
        
        self.console.print(menu_panel)
        return Prompt.ask("메뉴를 선택하세요", choices=['1','2','3','4','5','6','7','8'])
    
    def show_detailed_analysis(self, results: BacktestResults):
        """상세 분석 표시"""
        self.console.clear()
        self.console.print(Panel("📊 상세 백테스트 분석", style="cyan"))
        
        # 포트폴리오 성과 분석
        self._show_portfolio_analysis(results)
        
        # 시스템별 성과 (시스템 1 vs 시스템 2)
        self._show_system_comparison(results)
        
        # 리스크 분석
        self._show_risk_analysis(results)
        
        Prompt.ask("\n[dim]엔터를 눌러 계속하세요...[/dim]", default="")
    
    def show_detailed_trade_analysis(self, results: BacktestResults):
        """상세 거래 분석 표시"""
        analysis = self.detailed_analyzer.analyze_trades(results.trades)
        self.detailed_analyzer.display_detailed_analysis(analysis)
    
    def _show_portfolio_analysis(self, results: BacktestResults):
        """포트폴리오 분석"""
        equity_curve = results.equity_curve
        
        if not equity_curve:
            return
        
        # 드로다운 기간 분석
        max_dd_duration = self._calculate_max_drawdown_duration(equity_curve)
        
        # 월별 변동성
        monthly_volatility = self._calculate_monthly_volatility(results.monthly_returns)
        
        portfolio_table = Table(title="포트폴리오 심화 분석")
        portfolio_table.add_column("지표", style="cyan")
        portfolio_table.add_column("값", style="green")
        portfolio_table.add_column("설명", style="dim")
        
        portfolio_table.add_row(
            "최대 드로다운 기간",
            f"{max_dd_duration}일",
            "연속 손실 기간"
        )
        portfolio_table.add_row(
            "월별 변동성",
            f"{monthly_volatility:.2%}",
            "월수익률 표준편차"
        )
        portfolio_table.add_row(
            "수익/위험 비율",
            f"{results.metrics.annual_return / max(results.metrics.max_drawdown, 0.01):.2f}",
            "연수익률 ÷ 최대드로다운"
        )
        
        self.console.print(portfolio_table)
        self.console.print()
    
    def _show_system_comparison(self, results: BacktestResults):
        """시스템별 성과 비교"""
        trades = results.trades
        
        # 시스템별 거래 분리
        system1_trades = [t for t in trades if t.system == 1]
        system2_trades = [t for t in trades if t.system == 2]
        
        if not system1_trades and not system2_trades:
            return
        
        system_table = Table(title="시스템별 성과 비교")
        system_table.add_column("지표", style="cyan")
        system_table.add_column("시스템 1 (20일)", style="green")
        system_table.add_column("시스템 2 (55일)", style="blue")
        
        if system1_trades:
            s1_winrate = len([t for t in system1_trades if t.pnl > 0]) / len(system1_trades)
            s1_avg_pnl = sum(t.pnl for t in system1_trades) / len(system1_trades)
        else:
            s1_winrate = 0
            s1_avg_pnl = 0
        
        if system2_trades:
            s2_winrate = len([t for t in system2_trades if t.pnl > 0]) / len(system2_trades)
            s2_avg_pnl = sum(t.pnl for t in system2_trades) / len(system2_trades)
        else:
            s2_winrate = 0
            s2_avg_pnl = 0
        
        system_table.add_row(
            "거래 수",
            f"{len(system1_trades)}회",
            f"{len(system2_trades)}회"
        )
        system_table.add_row(
            "승률",
            f"{s1_winrate:.1%}",
            f"{s2_winrate:.1%}"
        )
        system_table.add_row(
            "평균 손익",
            f"${s1_avg_pnl:+.2f}",
            f"${s2_avg_pnl:+.2f}"
        )
        
        self.console.print(system_table)
        self.console.print()
    
    def _show_risk_analysis(self, results: BacktestResults):
        """리스크 분석"""
        trades = results.trades
        
        if not trades:
            return
        
        # 손실 거래 분석
        losing_trades = [t for t in trades if t.pnl < 0]
        
        if losing_trades:
            max_loss = min(t.pnl for t in losing_trades)
            avg_loss = sum(t.pnl for t in losing_trades) / len(losing_trades)
        else:
            max_loss = 0
            avg_loss = 0
        
        risk_table = Table(title="리스크 분석")
        risk_table.add_column("지표", style="cyan")
        risk_table.add_column("값", style="red")
        risk_table.add_column("평가", style="dim")
        
        risk_table.add_row(
            "최대 단일 손실",
            f"${max_loss:.2f}",
            f"초기자금 대비 {abs(max_loss)/results.initial_balance:.2%}"
        )
        risk_table.add_row(
            "평균 손실",
            f"${avg_loss:.2f}",
            f"손실 거래 {len(losing_trades)}회"
        )
        risk_table.add_row(
            "손실 거래 비율",
            f"{len(losing_trades)/len(trades):.1%}",
            "전체 거래 중 손실 비율"
        )
        
        self.console.print(risk_table)
        self.console.print()
    
    def show_all_trades(self, results: BacktestResults):
        """전체 거래 내역 표시"""
        trades = results.trades
        
        if not trades:
            self.console.print("[yellow]거래 내역이 없습니다.[/yellow]")
            return
        
        self.console.clear()
        self.console.print(Panel(f"📋 전체 거래 내역 ({len(trades)}건)", style="cyan"))
        
        # 페이지네이션으로 표시 (10개씩)
        page_size = 10
        total_pages = (len(trades) + page_size - 1) // page_size
        current_page = 1
        
        while True:
            start_idx = (current_page - 1) * page_size
            end_idx = min(start_idx + page_size, len(trades))
            page_trades = trades[start_idx:end_idx]
            
            # 거래 테이블
            trades_table = Table(title=f"페이지 {current_page}/{total_pages}")
            trades_table.add_column("번호", style="dim", width=5)
            trades_table.add_column("날짜", style="cyan", width=12)
            trades_table.add_column("방향", style="white", width=6)
            trades_table.add_column("진입가", style="blue", width=10)
            trades_table.add_column("청산가", style="blue", width=10)
            trades_table.add_column("수량", style="white", width=8)
            trades_table.add_column("손익", style="bold", width=10)
            trades_table.add_column("시스템", style="yellow", width=6)
            trades_table.add_column("사유", style="dim", width=8)
            
            for i, trade in enumerate(page_trades, start_idx + 1):
                pnl_color = "green" if trade.pnl > 0 else "red"
                direction_color = "green" if trade.direction == "LONG" else "red"
                
                trades_table.add_row(
                    str(i),
                    trade.exit_date.strftime("%Y-%m-%d"),
                    f"[{direction_color}]{trade.direction[:4]}[/{direction_color}]",
                    f"${trade.entry_price:,.0f}",
                    f"${trade.exit_price:,.0f}",
                    f"{trade.size:.3f}",
                    f"[{pnl_color}]{trade.pnl:+.0f}[/{pnl_color}]",
                    f"S{trade.system}",
                    trade.exit_reason[:6]
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
    
    def export_results(self, results: BacktestResults):
        """결과 내보내기"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # CSV 내보내기
        trades_data = []
        for trade in results.trades:
            trades_data.append({
                'date': trade.exit_date.strftime('%Y-%m-%d'),
                'symbol': trade.symbol,
                'direction': trade.direction,
                'entry_price': trade.entry_price,
                'exit_price': trade.exit_price,
                'size': trade.size,
                'pnl': trade.pnl,
                'system': trade.system,
                'exit_reason': trade.exit_reason
            })
        
        # 간단한 CSV 생성 (pandas 없이)
        csv_filename = f"data/backtest_results/trades_{timestamp}.csv"
        os.makedirs("data/backtest_results", exist_ok=True)
        
        with open(csv_filename, 'w') as f:
            if trades_data:
                # 헤더
                headers = list(trades_data[0].keys())
                f.write(','.join(headers) + '\n')
                
                # 데이터
                for trade in trades_data:
                    values = [str(trade[header]) for header in headers]
                    f.write(','.join(values) + '\n')
        
        # JSON 결과도 저장
        json_filename = f"data/backtest_results/backtest_{timestamp}.json"
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(results.to_dict(), f, indent=2, ensure_ascii=False, default=str)
        
        self.console.print(Panel(
            f"[green]✅ 결과가 성공적으로 내보내졌습니다![/green]\n\n"
            f"[cyan]거래 내역 CSV:[/cyan] {csv_filename}\n"
            f"[cyan]전체 결과 JSON:[/cyan] {json_filename}",
            title="내보내기 완료",
            style="green"
        ))
        
        Prompt.ask("\n[dim]엔터를 눌러 계속하세요...[/dim]", default="")
    
    # 유틸리티 메서드들
    def _evaluate_return(self, return_pct: float) -> str:
        """수익률 평가"""
        if return_pct > 50:
            return "[green]매우 우수[/green]"
        elif return_pct > 20:
            return "[green]우수[/green]"
        elif return_pct > 5:
            return "[yellow]양호[/yellow]"
        elif return_pct > -5:
            return "[white]보통[/white]"
        else:
            return "[red]부진[/red]"
    
    def _evaluate_annual_return(self, annual_return: float) -> str:
        """연수익률 평가"""
        if annual_return > 30:
            return "[green]매우 우수[/green]"
        elif annual_return > 15:
            return "[green]우수[/green]"
        elif annual_return > 8:
            return "[yellow]양호[/yellow]"
        elif annual_return > 0:
            return "[white]보통[/white]"
        else:
            return "[red]부진[/red]"
    
    def _evaluate_drawdown(self, drawdown: float) -> str:
        """드로다운 평가"""
        if drawdown < 0.05:
            return "[green]매우 안전[/green]"
        elif drawdown < 0.10:
            return "[green]안전[/green]"
        elif drawdown < 0.20:
            return "[yellow]보통[/yellow]"
        else:
            return "[red]위험[/red]"
    
    def _evaluate_sharpe(self, sharpe: float) -> str:
        """샤프 비율 평가"""
        if sharpe > 2.0:
            return "[green]매우 우수[/green]"
        elif sharpe > 1.0:
            return "[green]우수[/green]"
        elif sharpe > 0.5:
            return "[yellow]양호[/yellow]"
        elif sharpe > 0:
            return "[white]보통[/white]"
        else:
            return "[red]부진[/red]"
    
    def _calculate_max_drawdown_duration(self, equity_curve: List[Dict]) -> int:
        """최대 드로다운 지속 기간 계산"""
        if not equity_curve:
            return 0
        
        peak = equity_curve[0]['total_value']
        drawdown_start = None
        max_duration = 0
        current_duration = 0
        
        for point in equity_curve:
            value = point['total_value']
            
            if value >= peak:
                peak = value
                if drawdown_start is not None:
                    # 드로다운 종료
                    max_duration = max(max_duration, current_duration)
                    drawdown_start = None
                    current_duration = 0
            else:
                if drawdown_start is None:
                    drawdown_start = point
                current_duration += 1
        
        # 마지막이 드로다운으로 끝났을 경우
        if drawdown_start is not None:
            max_duration = max(max_duration, current_duration)
        
        return max_duration
    
    def _calculate_monthly_volatility(self, monthly_returns: Dict[str, float]) -> float:
        """월별 변동성 계산"""
        if len(monthly_returns) < 2:
            return 0.0
        
        returns = list(monthly_returns.values())
        mean_return = sum(returns) / len(returns)
        variance = sum((r - mean_return) ** 2 for r in returns) / len(returns)
        
        return variance ** 0.5

if __name__ == "__main__":
    # 테스트용 더미 데이터
    from .backend.engines.backtest_engine import BacktestConfig_, BacktestResults, PerformanceMetrics
    from strategy.turtle_strategy import TradeResult
    
    # 더미 결과 생성
    config = BacktestConfig_()
    metrics = PerformanceMetrics(
        total_return=0.25,
        annual_return=0.20,
        max_drawdown=0.12,
        sharpe_ratio=1.5,
        win_rate=0.65,
        profit_factor=1.8,
        total_trades=45
    )
    
    dummy_results = BacktestResults(
        config=config,
        initial_balance=10000,
        final_balance=12500,
        metrics=metrics,
        trades=[],
        equity_curve=[],
        monthly_returns={'2023-01': 0.05, '2023-02': -0.02}
    )
    
    ui = BacktestResultsUI()
    action = ui.display_results(dummy_results)
    print(f"Selected action: {action}")
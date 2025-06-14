"""
실시간 트레이딩 대시보드 - Rich 라이브러리 기반
"""

import asyncio
from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.live import Live
from rich.align import Align
from rich.progress import Progress, BarColumn, TextColumn
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import json

from frontend.dashboard.components.header import HeaderComponent
from frontend.dashboard.components.account import AccountComponent
from frontend.dashboard.components.positions import PositionsComponent
from frontend.dashboard.components.metrics import MetricsComponent
from frontend.dashboard.components.trades import TradesComponent
from strategy.turtle_strategy import TurtleStrategy, Position
from config import UIConfig, TradingMode

class TradingDashboard:
    """실시간 트레이딩 대시보드"""
    
    def __init__(self, mode: str = "paper", initial_balance: float = 10000.0):
        self.console = Console()
        self.mode = mode
        self.is_running = False
        self.last_update = datetime.now()
        
        # 컴포넌트 초기화
        self.header = HeaderComponent()
        self.account = AccountComponent(initial_balance)
        self.positions = PositionsComponent()
        self.metrics = MetricsComponent()
        self.trades = TradesComponent()
        
        # 터틀 전략
        self.strategy = TurtleStrategy()
        
        # 더미 데이터 (실제로는 API에서 가져옴)
        self.current_prices = {"BTCUSDT": 67500.0}
        self.market_data = {}
        
    async def start(self):
        """대시보드 시작"""
        self.is_running = True
        
        with Live(
            self._create_layout(),
            console=self.console,
            refresh_per_second=1,
            screen=True
        ) as live:
            try:
                while self.is_running:
                    # 데이터 업데이트
                    await self._update_data()
                    
                    # 레이아웃 새로고침
                    live.update(self._create_layout())
                    
                    await asyncio.sleep(UIConfig.DASHBOARD_REFRESH_RATE)
                    
            except KeyboardInterrupt:
                self.is_running = False
                self.console.print("\n[yellow]대시보드를 종료합니다...[/yellow]")
    
    def stop(self):
        """대시보드 중지"""
        self.is_running = False
    
    def _create_layout(self) -> Layout:
        """대시보드 레이아웃 생성"""
        layout = Layout()
        
        # 상단 헤더
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="main"),
            Layout(name="footer", size=3)
        )
        
        # 메인 영역을 좌우로 분할
        layout["main"].split_row(
            Layout(name="left", ratio=2),
            Layout(name="right", ratio=1)
        )
        
        # 좌측을 상하로 분할
        layout["left"].split_column(
            Layout(name="account_positions", ratio=1),
            Layout(name="metrics", ratio=1)
        )
        
        # 계좌와 포지션을 좌우로 분할
        layout["account_positions"].split_row(
            Layout(name="account"),
            Layout(name="positions")
        )
        
        # 각 패널에 컴포넌트 할당
        layout["header"].update(self._create_header_panel())
        layout["account"].update(self._create_account_panel())
        layout["positions"].update(self._create_positions_panel())
        layout["metrics"].update(self._create_metrics_panel())
        layout["right"].update(self._create_trades_panel())
        layout["footer"].update(self._create_footer_panel())
        
        return layout
    
    def _create_header_panel(self) -> Panel:
        """헤더 패널 생성"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 모드에 따른 색상
        mode_color = {
            "live": "red",
            "paper": "yellow", 
            "backtest": "blue"
        }.get(self.mode, "white")
        
        # 상태 표시
        status = "RUNNING" if self.is_running else "STOPPED"
        status_color = "green" if self.is_running else "red"
        
        header_text = (
            f"[bold cyan]Bitcoin Futures Turtle Trading Bot[/bold cyan]  |  "
            f"Mode: [{mode_color}]{self.mode.upper()}[/{mode_color}]  |  "
            f"Status: [{status_color}]{status}[/{status_color}]  |  "
            f"Time: [blue]{current_time}[/blue]"
        )
        
        return Panel(
            Align.center(header_text),
            style="cyan"
        )
    
    def _create_account_panel(self) -> Panel:
        """계좌 정보 패널"""
        account_data = self.account.get_account_data()
        
        account_table = Table.grid()
        account_table.add_column(style="cyan", width=12)
        account_table.add_column(style="bold", width=15)
        
        # 잔고
        balance_color = "green" if account_data['balance'] > 0 else "red"
        account_table.add_row("Balance:", f"[{balance_color}]${account_data['balance']:,.2f}[/{balance_color}]")
        
        # P&L
        pnl_color = "green" if account_data['pnl'] >= 0 else "red"
        pnl_sign = "+" if account_data['pnl'] >= 0 else ""
        account_table.add_row("P&L:", f"[{pnl_color}]{pnl_sign}${account_data['pnl']:,.2f} ({account_data['pnl_pct']:+.1f}%)[/{pnl_color}]")
        
        # 사용 가능 자금
        account_table.add_row("Available:", f"[green]${account_data['available']:,.2f}[/green]")
        
        # 사용 중인 마진
        margin_color = "yellow" if account_data['margin_used'] > account_data['balance'] * 0.5 else "white"
        account_table.add_row("Margin Used:", f"[{margin_color}]${account_data['margin_used']:,.2f}[/{margin_color}]")
        
        return Panel(
            account_table,
            title="💰 Account Summary",
            title_align="left",
            style="green"
        )
    
    def _create_positions_panel(self) -> Panel:
        """포지션 패널"""
        positions = self.strategy.get_all_positions()
        
        if not positions:
            no_positions = Text("No open positions", style="dim italic")
            return Panel(
                Align.center(no_positions),
                title="📊 Current Positions",
                title_align="left",
                style="blue"
            )
        
        pos_table = Table()
        pos_table.add_column("Symbol", style="cyan", width=8)
        pos_table.add_column("Side", style="white", width=5)
        pos_table.add_column("Size", style="white", width=8)
        pos_table.add_column("Entry", style="blue", width=8)
        pos_table.add_column("Current", style="blue", width=8)
        pos_table.add_column("P&L", style="bold", width=10)
        
        for symbol, position in positions.items():
            current_price = self.current_prices.get(symbol, position.avg_price)
            unrealized_pnl = self.strategy.calculate_unrealized_pnl(symbol, current_price)
            pnl_pct = (unrealized_pnl / (position.avg_price * position.total_size)) * 100
            
            # 색상 결정
            direction_color = "green" if position.direction == "LONG" else "red"
            pnl_color = "green" if unrealized_pnl >= 0 else "red"
            
            pos_table.add_row(
                symbol[:8],
                f"[{direction_color}]{position.direction}[/{direction_color}]",
                f"{position.total_size:.3f}",
                f"${position.avg_price:,.0f}",
                f"${current_price:,.0f}",
                f"[{pnl_color}]{unrealized_pnl:+.0f} ({pnl_pct:+.1f}%)[/{pnl_color}]"
            )
        
        return Panel(
            pos_table,
            title="📊 Current Positions",
            title_align="left",
            style="blue"
        )
    
    def _create_metrics_panel(self) -> Panel:
        """성과 지표 패널"""
        metrics_data = self.metrics.get_metrics_data()
        
        # 2열 레이아웃
        metrics_table = Table.grid()
        metrics_table.add_column(style="cyan", width=18)
        metrics_table.add_column(style="bold", width=12)
        metrics_table.add_column(style="cyan", width=18)
        metrics_table.add_column(style="bold", width=12)
        
        # 첫 번째 행
        win_rate_color = "green" if metrics_data['win_rate'] > 0.5 else "yellow" if metrics_data['win_rate'] > 0.4 else "red"
        sharpe_color = "green" if metrics_data['sharpe_ratio'] > 1.0 else "yellow" if metrics_data['sharpe_ratio'] > 0.5 else "red"
        
        metrics_table.add_row(
            "Win Rate (Total):",
            f"[{win_rate_color}]{metrics_data['win_rate']:.0%}[/{win_rate_color}]",
            "Sharpe Ratio:",
            f"[{sharpe_color}]{metrics_data['sharpe_ratio']:.2f}[/{sharpe_color}]"
        )
        
        # 두 번째 행
        metrics_table.add_row(
            "Long Win Rate:",
            f"{metrics_data['long_win_rate']:.0%}",
            "Profit Factor:",
            f"{metrics_data['profit_factor']:.2f}"
        )
        
        # 세 번째 행
        metrics_table.add_row(
            "Short Win Rate:",
            f"{metrics_data['short_win_rate']:.0%}",
            "Total Trades:",
            f"{metrics_data['total_trades']}"
        )
        
        # 네 번째 행
        dd_color = "red" if metrics_data['max_drawdown'] > 0.15 else "yellow" if metrics_data['max_drawdown'] > 0.1 else "green"
        current_dd_color = "red" if metrics_data['current_drawdown'] > 0.1 else "yellow" if metrics_data['current_drawdown'] > 0.05 else "green"
        
        metrics_table.add_row(
            "Max Drawdown:",
            f"[{dd_color}]{metrics_data['max_drawdown']:.1%}[/{dd_color}]",
            "Current DD:",
            f"[{current_dd_color}]{metrics_data['current_drawdown']:.1%}[/{current_dd_color}]"
        )
        
        return Panel(
            metrics_table,
            title="📈 Performance Metrics",
            title_align="left",
            style="yellow"
        )
    
    def _create_trades_panel(self) -> Panel:
        """최근 거래 패널"""
        recent_trades = self.strategy.get_trade_history()[-5:]  # 최근 5개
        
        if not recent_trades:
            no_trades = Text("No completed trades yet", style="dim italic")
            return Panel(
                Align.center(no_trades),
                title="📋 Recent Trades (Last 5)",
                title_align="left",
                style="magenta"
            )
        
        trades_table = Table()
        trades_table.add_column("Date", style="cyan", width=10)
        trades_table.add_column("Symbol", style="white", width=8)
        trades_table.add_column("Side", style="bold", width=5)
        trades_table.add_column("Entry", style="blue", width=8)
        trades_table.add_column("Exit", style="blue", width=8)
        trades_table.add_column("P&L", style="bold", width=8)
        trades_table.add_column("Reason", style="dim", width=6)
        
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
                trade.exit_reason[:6]
            )
        
        return Panel(
            trades_table,
            title="📋 Recent Trades (Last 5)",
            title_align="left",
            style="magenta"
        )
    
    def _create_footer_panel(self) -> Panel:
        """푸터 패널"""
        footer_text = (
            "[dim]Controls: [bold]Q[/bold]=Quit  [bold]P[/bold]=Pause/Resume  "
            "[bold]R[/bold]=Reset  [bold]S[/bold]=Settings  [bold]T[/bold]=Trade History[/dim]"
        )
        
        return Panel(
            Align.center(footer_text),
            style="dim"
        )
    
    async def _update_data(self):
        """데이터 업데이트"""
        # 실제 구현에서는 여기서 API 호출
        current_time = datetime.now()
        
        # 가격 시뮬레이션 (더미 데이터)
        import random
        for symbol in self.current_prices:
            # 약간의 랜덤 가격 변동
            change_pct = random.uniform(-0.005, 0.005)  # ±0.5%
            self.current_prices[symbol] *= (1 + change_pct)
        
        # 컴포넌트 데이터 업데이트
        await self.account.update_data(self.current_prices, self.strategy.get_all_positions())
        await self.metrics.update_data(self.strategy.get_trade_history())
        
        self.last_update = current_time
    
    def handle_keyboard_input(self, key: str):
        """키보드 입력 처리"""
        if key.upper() == 'Q':
            self.stop()
        elif key.upper() == 'P':
            self.is_running = not self.is_running
        elif key.upper() == 'R':
            self.strategy.reset()
            self.account.reset()
        # 추가 단축키 처리...

class LiveTradingManager:
    """라이브 트레이딩 관리자"""
    
    def __init__(self, mode: str = "paper"):
        self.mode = mode
        self.dashboard = TradingDashboard(mode)
        self.trading_engine = None  # 실제 거래 엔진
        
    async def start_trading(self, config: Dict[str, Any]):
        """트레이딩 시작"""
        self.console = Console()
        
        try:
            # 설정 표시
            self._show_trading_config(config)
            
            # 대시보드 시작
            await self.dashboard.start()
            
        except Exception as e:
            self.console.print(f"[red]트레이딩 중 오류 발생: {e}[/red]")
            raise
    
    def _show_trading_config(self, config: Dict[str, Any]):
        """트레이딩 설정 표시"""
        config_panel = Panel(
            f"[bold white]트레이딩 설정[/bold white]\n\n"
            f"[cyan]모드:[/cyan] {self.mode.upper()}\n"
            f"[cyan]종목:[/cyan] {config.get('symbol', 'BTCUSDT')}\n"
            f"[cyan]초기 자금:[/cyan] ${config.get('initial_balance', 10000):,.2f}\n"
            f"[cyan]활성 시스템:[/cyan] {config.get('systems', [1, 2])}\n\n"
            f"[yellow]⚠️ 주의: {self.mode} 모드로 실행됩니다.[/yellow]",
            title="트레이딩 시작",
            style="green"
        )
        
        self.console.print(config_panel)

if __name__ == "__main__":
    # 테스트 실행
    async def test_dashboard():
        dashboard = TradingDashboard(mode="paper")
        
        # 더미 포지션 추가
        from strategy.turtle_strategy import TradingUnit, Position
        from datetime import datetime
        
        unit = TradingUnit(
            entry_price=65000,
            entry_date=datetime.now(),
            size=0.1,
            stop_loss=63000,
            system=1,
            unit_number=1
        )
        
        position = Position(
            symbol="BTCUSDT",
            direction="LONG",
            units=[unit],
            total_size=0.1,
            avg_price=65000
        )
        
        dashboard.strategy.positions["BTCUSDT"] = position
        
        # 5초간 실행
        import asyncio
        await asyncio.wait_for(dashboard.start(), timeout=5.0)
    
    try:
        asyncio.run(test_dashboard())
    except asyncio.TimeoutError:
        print("Dashboard test completed")
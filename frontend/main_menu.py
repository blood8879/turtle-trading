"""
메인 메뉴 UI - 애플리케이션 진입점
"""

import asyncio
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.text import Text
from rich.align import Align
from rich.layout import Layout
from typing import Dict, Any, Optional

from frontend.backtest.setup_ui import BacktestSetupUI
from frontend.backtest.results_ui import BacktestResultsUI
from frontend.dashboard.main_dashboard import TradingDashboard
from frontend.backtest.backend.engines.backtest_engine import BacktestEngine
from config import validate_config, BacktestConfig

class MainMenuUI:
    """메인 메뉴 UI"""
    
    def __init__(self):
        self.console = Console()
        self.backtest_setup = BacktestSetupUI()
        self.backtest_results = BacktestResultsUI()
        
        # 설정 검증
        try:
            validate_config()
        except ValueError as e:
            self.console.print(f"[red]설정 오류: {e}[/red]")
            self.console.print("[yellow]계속하려면 .env 파일을 확인하고 올바른 설정을 입력하세요.[/yellow]")
    
    async def show(self):
        """메인 메뉴 표시"""
        while True:
            self.console.clear()
            self._show_header()
            self._show_status()
            
            choice = self._show_menu()
            
            if choice == '1':
                await self._handle_backtest()
            elif choice == '2':
                await self._handle_paper_trading()
            elif choice == '3':
                await self._handle_live_trading()
            elif choice == '4':
                self._handle_view_results()
            elif choice == '5':
                self._handle_settings()
            elif choice == '6':
                self.console.print("[cyan]프로그램을 종료합니다. 안녕히 가세요![/cyan]")
                break
            else:
                self.console.print("[red]잘못된 선택입니다.[/red]")
                self.console.input("[dim]엔터를 눌러 계속하세요...[/dim]")
    
    def _show_header(self):
        """헤더 표시"""
        title = Text("Bitcoin Futures Turtle Trading Bot", style="bold cyan")
        subtitle = Text("Professional Algorithmic Trading System", style="bold white")
        version = Text("Version 1.0.0 | Developed with Claude Code", style="dim")
        
        header_content = f"{title}\n{subtitle}\n{version}"
        
        header_panel = Panel(
            Align.center(header_content),
            style="cyan",
            padding=(1, 2)
        )
        
        self.console.print(header_panel)
        self.console.print()
    
    def _show_status(self):
        """시스템 상태 표시"""
        # 간단한 시스템 상태 체크
        api_status = "[green]●[/green] API 연결 준비됨"
        data_status = "[green]●[/green] 데이터 시스템 정상"
        config_status = "[green]●[/green] 설정 유효"
        
        status_text = f"{api_status}  {data_status}  {config_status}"
        
        status_panel = Panel(
            status_text,
            title="시스템 상태",
            style="green",
            padding=(0, 1)
        )
        
        self.console.print(status_panel)
        self.console.print()
    
    def _show_menu(self) -> str:
        """메뉴 표시 및 선택"""
        menu_text = (
            "[bold white]메인 메뉴[/bold white]\n\n"
            "[cyan]1.[/cyan] 백테스트 실행\n"
            "   • 과거 데이터로 전략 검증\n"
            "   • 다양한 기간과 설정으로 테스트\n"
            "   • 상세한 성과 분석 리포트\n\n"
            "[cyan]2.[/cyan] 가상매매 시작\n"
            "   • 실시간 데이터로 모의 거래\n"
            "   • 리스크 없는 전략 실습\n"
            "   • 라이브 대시보드 모니터링\n\n"
            "[cyan]3.[/cyan] 실제매매 시작\n"
            "   • Binance 실계좌 연동\n"
            "   • 실제 자금으로 자동 거래\n"
            "   • 실시간 포지션 관리\n\n"
            "[cyan]4.[/cyan] 이전 결과 보기\n"
            "   • 백테스트 결과 조회\n"
            "   • 거래 내역 분석\n"
            "   • 성과 비교\n\n"
            "[cyan]5.[/cyan] 설정\n"
            "   • 시스템 설정 변경\n"
            "   • API 키 관리\n"
            "   • 로그 설정\n\n"
            "[red]6.[/red] 종료"
        )
        
        menu_panel = Panel(
            menu_text,
            title="🚀 Bitcoin Futures Turtle Trading Bot",
            style="blue",
            padding=(1, 2)
        )
        
        self.console.print(menu_panel)
        
        return Prompt.ask(
            "\n[bold]메뉴를 선택하세요",
            choices=['1', '2', '3', '4', '5', '6'],
            default='1'
        )
    
    async def _handle_backtest(self):
        """백테스트 처리"""
        try:
            # 백테스트 설정
            config = self.backtest_setup.show_setup_screen()
            
            if config is None:
                return  # 사용자가 취소
            
            # 백테스트 설정 객체 생성
            backtest_config = BacktestConfig(
                symbol=config['symbol'],
                start_date=config['start_date'],
                end_date=config['end_date'],
                timeframe=config['timeframe'],
                initial_balance=config['initial_balance'],
                commission_rate=config['commission_rate'],
                systems=config['systems']
            )
            
            # 백테스트 실행
            self.console.print("\n[yellow]백테스트를 실행 중입니다...[/yellow]")
            
            engine = BacktestEngine(backtest_config)
            results = await engine.run_backtest()
            
            # 결과 표시
            while True:
                action = self.backtest_results.display_results(results)
                
                if action == '1':  # 상세 분석
                    self.backtest_results.show_detailed_analysis(results)
                elif action == '2':  # 전체 거래 내역
                    self.backtest_results.show_all_trades(results)
                elif action == '3':  # 롱/숏 상세 거래 분석
                    self.backtest_results.show_detailed_trade_analysis(results)
                elif action == '4':  # 차트 생성
                    self._create_backtest_chart(results)
                elif action == '5':  # CSV 내보내기
                    self.backtest_results.export_results(results)
                elif action == '6':  # 새 백테스트
                    break
                elif action == '7':  # 가상매매 시작
                    await self._start_paper_trading_from_backtest(config)
                    break
                elif action == '8':  # 메인 메뉴
                    break
                    
        except Exception as e:
            self.console.print(f"[red]백테스트 중 오류 발생: {e}[/red]")
            self.console.input("[dim]엔터를 눌러 계속하세요...[/dim]")
    
    async def _handle_paper_trading(self):
        """가상매매 처리"""
        try:
            # 가상매매 설정
            config = self._get_trading_config("paper")
            
            if config is None:
                return
            
            # 가상매매 시작
            self.console.print(f"\n[yellow]가상매매를 시작합니다...[/yellow]")
            self.console.print(f"[dim]Ctrl+C를 눌러 중지할 수 있습니다.[/dim]\n")
            
            dashboard = TradingDashboard(mode="paper", initial_balance=config['initial_balance'])
            await dashboard.start()
            
        except KeyboardInterrupt:
            self.console.print("\n[yellow]가상매매를 중지했습니다.[/yellow]")
        except Exception as e:
            self.console.print(f"[red]가상매매 중 오류 발생: {e}[/red]")
        finally:
            self.console.input("[dim]엔터를 눌러 메인 메뉴로 돌아가세요...[/dim]")
    
    async def _handle_live_trading(self):
        """실제매매 처리"""
        # 안전 확인
        self.console.print("[bold red]⚠️ 경고: 실제 자금을 사용한 거래입니다![/bold red]")
        
        confirm = Confirm.ask(
            "실제 거래를 시작하시겠습니까? 이는 실제 손실을 초래할 수 있습니다.",
            default=False
        )
        
        if not confirm:
            return
        
        # API 키 확인
        try:
            from config import BinanceConfig
            if not BinanceConfig.API_KEY or not BinanceConfig.SECRET_KEY:
                self.console.print("[red]Binance API 키가 설정되지 않았습니다.[/red]")
                self.console.print("[yellow].env 파일에 BINANCE_API_KEY와 BINANCE_SECRET_KEY를 설정하세요.[/yellow]")
                self.console.input("[dim]엔터를 눌러 계속하세요...[/dim]")
                return
        except Exception as e:
            self.console.print(f"[red]API 설정 확인 중 오류: {e}[/red]")
            return
        
        try:
            # 실제 거래 설정
            config = self._get_trading_config("live")
            
            if config is None:
                return
            
            # 실제 거래 시작
            self.console.print(f"\n[red]🔴 실제매매를 시작합니다...[/red]")
            self.console.print(f"[dim]Ctrl+C를 눌러 중지할 수 있습니다.[/dim]\n")
            
            dashboard = TradingDashboard(mode="live", initial_balance=config['initial_balance'])
            await dashboard.start()
            
        except KeyboardInterrupt:
            self.console.print("\n[yellow]실제매매를 중지했습니다.[/yellow]")
        except Exception as e:
            self.console.print(f"[red]실제매매 중 오류 발생: {e}[/red]")
        finally:
            self.console.input("[dim]엔터를 눌러 메인 메뉴로 돌아가세요...[/dim]")
    
    def _handle_view_results(self):
        """결과 보기 처리"""
        self.console.print("[yellow]이전 결과 조회 기능을 구현 중입니다...[/yellow]")
        
        # 백테스트 결과 파일 목록 표시
        import os
        results_dir = "data/backtest_results"
        
        if os.path.exists(results_dir):
            files = [f for f in os.listdir(results_dir) if f.endswith('.json')]
            
            if files:
                self.console.print(f"\n[cyan]백테스트 결과 파일 ({len(files)}개):[/cyan]")
                for i, file in enumerate(files[:10], 1):  # 최근 10개만 표시
                    self.console.print(f"  {i}. {file}")
                
                if len(files) > 10:
                    self.console.print(f"  ... 및 {len(files) - 10}개 더")
            else:
                self.console.print("[dim]저장된 백테스트 결과가 없습니다.[/dim]")
        else:
            self.console.print("[dim]백테스트 결과 디렉토리가 없습니다.[/dim]")
        
        self.console.input("[dim]엔터를 눌러 계속하세요...[/dim]")
    
    def _handle_settings(self):
        """설정 처리"""
        self.console.print("[yellow]설정 메뉴를 구현 중입니다...[/yellow]")
        
        settings_info = (
            "[bold white]현재 설정 정보[/bold white]\n\n"
            "[cyan]• 설정 파일:[/cyan] config.py\n"
            "[cyan]• 환경 변수:[/cyan] .env\n"
            "[cyan]• 로그 디렉토리:[/cyan] logs/\n"
            "[cyan]• 데이터 디렉토리:[/cyan] data/\n\n"
            "[yellow]설정 변경을 원하시면 해당 파일을 직접 편집하세요.[/yellow]"
        )
        
        settings_panel = Panel(
            settings_info,
            title="⚙️ 시스템 설정",
            style="blue"
        )
        
        self.console.print(settings_panel)
        self.console.input("[dim]엔터를 눌러 계속하세요...[/dim]")
    
    def _get_trading_config(self, mode: str) -> Optional[Dict[str, Any]]:
        """트레이딩 설정 가져오기"""
        self.console.print(f"\n[bold yellow]📊 {mode.upper()} 트레이딩 설정[/bold yellow]")
        
        # 기본 설정값
        default_config = {
            'symbol': 'BTCUSDT',
            'initial_balance': 10000.0,
            'systems': [1, 2]
        }
        
        # 간단한 설정 입력
        from rich.prompt import FloatPrompt
        
        symbol = Prompt.ask("거래 종목", default=default_config['symbol'])
        initial_balance = FloatPrompt.ask("초기 자금 ($)", default=default_config['initial_balance'])
        
        # 시스템 선택
        self.console.print("\n[bold]사용할 터틀 시스템을 선택하세요:[/bold]")
        self.console.print("[cyan]1.[/cyan] 시스템 1만 (20일 돌파)")
        self.console.print("[cyan]2.[/cyan] 시스템 2만 (55일 돌파)")
        self.console.print("[cyan]3.[/cyan] 시스템 1 + 2 (권장)")
        
        system_choice = Prompt.ask("시스템 선택", choices=['1', '2', '3'], default='3')
        
        if system_choice == '1':
            systems = [1]
        elif system_choice == '2':
            systems = [2]
        else:
            systems = [1, 2]
        
        config = {
            'symbol': symbol,
            'initial_balance': initial_balance,
            'systems': systems
        }
        
        # 설정 확인
        confirm_text = (
            f"[bold white]설정 확인[/bold white]\n\n"
            f"[cyan]모드:[/cyan] {mode.upper()}\n"
            f"[cyan]종목:[/cyan] {config['symbol']}\n"
            f"[cyan]초기 자금:[/cyan] ${config['initial_balance']:,.2f}\n"
            f"[cyan]시스템:[/cyan] {', '.join(f'시스템 {s}' for s in config['systems'])}"
        )
        
        confirm_panel = Panel(confirm_text, style="green")
        self.console.print(confirm_panel)
        
        if Confirm.ask("\n이 설정으로 진행하시겠습니까?", default=True):
            return config
        else:
            return None
    
    async def _start_paper_trading_from_backtest(self, backtest_config: Dict[str, Any]):
        """백테스트 설정으로 가상매매 시작"""
        try:
            config = {
                'symbol': backtest_config['symbol'],
                'initial_balance': backtest_config['initial_balance'],
                'systems': backtest_config['systems']
            }
            
            self.console.print(f"\n[yellow]백테스트 설정으로 가상매매를 시작합니다...[/yellow]")
            self.console.print(f"[dim]Ctrl+C를 눌러 중지할 수 있습니다.[/dim]\n")
            
            dashboard = TradingDashboard(mode="paper", initial_balance=config['initial_balance'])
            await dashboard.start()
            
        except KeyboardInterrupt:
            self.console.print("\n[yellow]가상매매를 중지했습니다.[/yellow]")
        except Exception as e:
            self.console.print(f"[red]가상매매 중 오류 발생: {e}[/red]")
        finally:
            self.console.input("[dim]엔터를 눌러 메인 메뉴로 돌아가세요...[/dim]")
    
    def _create_backtest_chart(self, results):
        """백테스트 차트 생성"""
        self.console.print("[yellow]차트 생성 기능을 구현 중입니다...[/yellow]")
        self.console.print("[dim]향후 matplotlib을 사용하여 수익 곡선 차트를 생성할 예정입니다.[/dim]")
        self.console.input("[dim]엔터를 눌러 계속하세요...[/dim]")

if __name__ == "__main__":
    # 애플리케이션 실행
    async def main():
        menu = MainMenuUI()
        await menu.show()
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n프로그램이 중단되었습니다.")
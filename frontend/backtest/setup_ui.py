"""
백테스트 설정 UI - Rich 라이브러리 기반 터미널 인터페이스
"""

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, IntPrompt, FloatPrompt, Confirm
from rich.table import Table
from rich.text import Text
from rich.layout import Layout
from rich.align import Align
from datetime import datetime, timedelta
from typing import Dict, Any, List

from config import BacktestConfig

class BacktestSetupUI:
    """백테스트 설정 UI"""
    
    def __init__(self):
        self.console = Console()
        self.config = {
            'symbol': 'BTCUSDT',
            'start_date': '2023-01-01',
            'end_date': '2024-12-31',
            'timeframe': '1d',
            'initial_balance': 10000.0,
            'commission_rate': 0.0004,
            'leverage': 1.0,
            'systems': [1, 2]
        }
    
    def show_setup_screen(self) -> Dict[str, Any]:
        """백테스트 설정 화면 표시"""
        self.console.clear()
        
        # 헤더 표시
        self._show_header()
        
        # 현재 설정 표시
        self._show_current_settings()
        
        # 설정 메뉴
        while True:
            choice = self._show_setup_menu()
            
            if choice == '1':
                self._configure_period()
            elif choice == '2':
                self._configure_timeframe()
            elif choice == '3':
                self._configure_balance()
            elif choice == '4':
                self._configure_leverage()
            elif choice == '5':
                self._configure_systems()
            elif choice == '6':
                self._configure_advanced()
            elif choice == '7':
                if self._confirm_settings():
                    return self.config
            elif choice == '8':
                return None  # 취소
            else:
                self.console.print("[red]잘못된 선택입니다. 다시 시도해주세요.[/red]")
    
    def _show_header(self):
        """헤더 표시"""
        title = Text("Bitcoin Futures Turtle Trading Bot", style="bold cyan")
        subtitle = Text("백테스트 설정", style="bold white")
        
        header_panel = Panel(
            Align.center(f"{title}\n{subtitle}"),
            style="cyan",
            padding=(1, 2)
        )
        
        self.console.print(header_panel)
        self.console.print()
    
    def _show_current_settings(self):
        """현재 설정 표시"""
        table = Table(title="현재 백테스트 설정", title_style="bold yellow")
        table.add_column("항목", style="cyan", width=20)
        table.add_column("값", style="green", width=30)
        table.add_column("설명", style="white", width=40)
        
        table.add_row(
            "거래 종목",
            self.config['symbol'],
            "백테스트할 암호화폐 종목"
        )
        table.add_row(
            "시작일",
            self.config['start_date'],
            "백테스트 시작 날짜"
        )
        table.add_row(
            "종료일",
            self.config['end_date'],
            "백테스트 종료 날짜"
        )
        table.add_row(
            "타임프레임",
            self.config['timeframe'],
            "캔들 차트 시간 간격"
        )
        table.add_row(
            "초기 자금",
            f"${self.config['initial_balance']:,.2f}",
            "백테스트 시작 자금"
        )
        table.add_row(
            "수수료",
            f"{self.config['commission_rate']:.4f} ({self.config['commission_rate']*100:.2f}%)",
            "거래 수수료율"
        )
        table.add_row(
            "활성 시스템",
            f"시스템 {', '.join(map(str, self.config['systems']))}",
            "사용할 터틀 트레이딩 시스템"
        )
        table.add_row(
            "레버리지",
            f"{self.config['leverage']:.1f}x",
            "거래 레버리지 배율"
        )
        
        # 예상 백테스트 기간 계산
        start_date = datetime.strptime(self.config['start_date'], '%Y-%m-%d')
        end_date = datetime.strptime(self.config['end_date'], '%Y-%m-%d')
        duration = (end_date - start_date).days
        
        table.add_row(
            "백테스트 기간",
            f"{duration}일 ({duration/365.25:.1f}년)",
            "전체 백테스트 기간"
        )
        
        self.console.print(table)
        self.console.print()
    
    def _show_setup_menu(self) -> str:
        """설정 메뉴 표시"""
        menu_panel = Panel(
            "[bold white]백테스트 설정 메뉴[/bold white]\n\n"
            "[cyan]1.[/cyan] 기간 설정 (시작일/종료일)\n"
            "[cyan]2.[/cyan] 타임프레임 설정\n"
            "[cyan]3.[/cyan] 초기 자금 설정\n"
            "[cyan]4.[/cyan] 레버리지 설정\n"
            "[cyan]5.[/cyan] 시스템 설정\n"
            "[cyan]6.[/cyan] 고급 설정 (수수료 등)\n"
            "[green]7.[/green] 백테스트 시작\n"
            "[red]8.[/red] 메인 메뉴로 돌아가기",
            title="메뉴",
            style="blue"
        )
        
        self.console.print(menu_panel)
        return Prompt.ask("메뉴를 선택하세요", choices=['1','2','3','4','5','6','7','8'])
    
    def _configure_period(self):
        """기간 설정"""
        self.console.print("\n[bold yellow]📅 백테스트 기간 설정[/bold yellow]")
        
        # 미리 정의된 기간 옵션
        preset_options = {
            '1': ('2024-01-01', '2024-12-31', '2024년 (1년)'),
            '2': ('2023-01-01', '2024-12-31', '2023-2024년 (2년)'),
            '3': ('2022-01-01', '2024-12-31', '2022-2024년 (3년)'),
            '4': ('2020-01-01', '2024-12-31', '2020-2024년 (5년)'),
            '5': ('custom', 'custom', '직접 입력')
        }
        
        # 옵션 표시
        period_table = Table()
        period_table.add_column("선택", style="cyan")
        period_table.add_column("기간", style="green")
        period_table.add_column("설명", style="white")
        
        for key, (start, end, desc) in preset_options.items():
            if start != 'custom':
                period_table.add_row(key, f"{start} ~ {end}", desc)
            else:
                period_table.add_row(key, "사용자 지정", desc)
        
        self.console.print(period_table)
        
        choice = Prompt.ask("기간을 선택하세요", choices=list(preset_options.keys()))
        
        if choice == '5':  # 직접 입력
            while True:
                try:
                    start_date = Prompt.ask("시작일을 입력하세요 (YYYY-MM-DD)")
                    datetime.strptime(start_date, '%Y-%m-%d')
                    break
                except ValueError:
                    self.console.print("[red]올바른 날짜 형식이 아닙니다. YYYY-MM-DD 형식으로 입력해주세요.[/red]")
            
            while True:
                try:
                    end_date = Prompt.ask("종료일을 입력하세요 (YYYY-MM-DD)")
                    end_dt = datetime.strptime(end_date, '%Y-%m-%d')
                    start_dt = datetime.strptime(start_date, '%Y-%m-%d')
                    
                    if end_dt <= start_dt:
                        self.console.print("[red]종료일은 시작일보다 늦어야 합니다.[/red]")
                        continue
                    break
                except ValueError:
                    self.console.print("[red]올바른 날짜 형식이 아닙니다. YYYY-MM-DD 형식으로 입력해주세요.[/red]")
            
            self.config['start_date'] = start_date
            self.config['end_date'] = end_date
        else:
            start_date, end_date, _ = preset_options[choice]
            self.config['start_date'] = start_date
            self.config['end_date'] = end_date
        
        self.console.print(f"[green]✅ 기간이 설정되었습니다: {self.config['start_date']} ~ {self.config['end_date']}[/green]")
        self.console.print()
    
    def _configure_timeframe(self):
        """타임프레임 설정"""
        self.console.print("\n[bold yellow]⏰ 타임프레임 설정[/bold yellow]")
        
        timeframes = {
            '1': ('1m', '1분봉 (고빈도 거래, 데이터 많음)'),
            '2': ('5m', '5분봉 (단기 거래)'),
            '3': ('15m', '15분봉 (중단기 거래)'),
            '4': ('1h', '1시간봉 (중기 거래)'),
            '5': ('4h', '4시간봉 (중장기 거래)'),
            '6': ('1d', '일봉 (장기 거래, 터틀 전략 최적)'),
            '7': ('1w', '주봉 (초장기 거래)'),
            '8': ('1M', '월봉 (극장기 거래)')
        }
        
        tf_table = Table()
        tf_table.add_column("선택", style="cyan")
        tf_table.add_column("타임프레임", style="green")
        tf_table.add_column("설명", style="white")
        
        for key, (tf, desc) in timeframes.items():
            style = "bold green" if tf == '1d' else "white"
            tf_table.add_row(key, tf, desc, style=style)
        
        self.console.print(tf_table)
        self.console.print("\n[dim]💡 터틀 트레이딩 전략은 일봉(1d)에서 가장 효과적입니다.[/dim]")
        
        choice = Prompt.ask("타임프레임을 선택하세요", choices=list(timeframes.keys()), default='6')
        
        timeframe, description = timeframes[choice]
        self.config['timeframe'] = timeframe
        
        self.console.print(f"[green]✅ 타임프레임이 설정되었습니다: {timeframe} ({description})[/green]")
        self.console.print()
    
    def _configure_balance(self):
        """초기 자금 설정"""
        self.console.print("\n[bold yellow]💰 초기 자금 설정[/bold yellow]")
        
        preset_balances = {
            '1': (1000, '소액 테스트'),
            '2': (10000, '일반적인 백테스트'),
            '3': (50000, '중간 자금'),
            '4': (100000, '대규모 자금'),
            '5': (0, '직접 입력')
        }
        
        balance_table = Table()
        balance_table.add_column("선택", style="cyan")
        balance_table.add_column("금액", style="green")
        balance_table.add_column("설명", style="white")
        
        for key, (amount, desc) in preset_balances.items():
            if amount > 0:
                balance_table.add_row(key, f"${amount:,}", desc)
            else:
                balance_table.add_row(key, "사용자 지정", desc)
        
        self.console.print(balance_table)
        
        choice = Prompt.ask("초기 자금을 선택하세요", choices=list(preset_balances.keys()), default='2')
        
        if choice == '5':  # 직접 입력
            while True:
                try:
                    balance = FloatPrompt.ask("초기 자금을 입력하세요 ($)")
                    if balance <= 0:
                        self.console.print("[red]초기 자금은 0보다 커야 합니다.[/red]")
                        continue
                    break
                except:
                    self.console.print("[red]올바른 숫자를 입력해주세요.[/red]")
            
            self.config['initial_balance'] = balance
        else:
            balance, _ = preset_balances[choice]
            self.config['initial_balance'] = balance
        
        self.console.print(f"[green]✅ 초기 자금이 설정되었습니다: ${self.config['initial_balance']:,.2f}[/green]")
        self.console.print()
    
    def _configure_leverage(self):
        """레버리지 설정"""
        self.console.print("\n[bold yellow]📊 레버리지 설정[/bold yellow]")
        
        leverage_presets = {
            '1': (1.0, '1배 (현물거래, 안전)'),
            '2': (2.0, '2배 (낮은 위험)'),
            '3': (5.0, '5배 (중간 위험)'),
            '4': (10.0, '10배 (높은 위험)'),
            '5': (20.0, '20배 (매우 높은 위험)'),
            '6': (0, '직접 입력')
        }
        
        leverage_table = Table()
        leverage_table.add_column("선택", style="cyan")
        leverage_table.add_column("레버리지", style="green")
        leverage_table.add_column("위험도", style="white")
        
        for key, (leverage, desc) in leverage_presets.items():
            if leverage > 0:
                risk_color = "green" if leverage <= 2 else "yellow" if leverage <= 5 else "red"
                leverage_table.add_row(key, f"{leverage:.1f}x", f"[{risk_color}]{desc}[/{risk_color}]")
            else:
                leverage_table.add_row(key, "사용자 지정", desc)
        
        self.console.print(leverage_table)
        self.console.print("\n[dim]⚠️  높은 레버리지는 수익과 손실을 모두 증폭시킵니다.[/dim]")
        
        choice = Prompt.ask("레버리지를 선택하세요", choices=list(leverage_presets.keys()), default='1')
        
        if choice == '6':  # 직접 입력
            while True:
                try:
                    leverage = FloatPrompt.ask("레버리지를 입력하세요 (1.0 ~ 100.0)")
                    if leverage < 1.0 or leverage > 100.0:
                        self.console.print("[red]레버리지는 1.0배에서 100.0배 사이여야 합니다.[/red]")
                        continue
                    break
                except:
                    self.console.print("[red]올바른 숫자를 입력해주세요.[/red]")
            
            self.config['leverage'] = leverage
        else:
            leverage, _ = leverage_presets[choice]
            self.config['leverage'] = leverage
        
        risk_level = "낮음" if self.config['leverage'] <= 2 else "중간" if self.config['leverage'] <= 5 else "높음"
        self.console.print(f"[green]✅ 레버리지가 설정되었습니다: {self.config['leverage']:.1f}x (위험도: {risk_level})[/green]")
        self.console.print()
    
    def _configure_systems(self):
        """시스템 설정"""
        self.console.print("\n[bold yellow]⚙️ 터틀 트레이딩 시스템 설정[/bold yellow]")
        
        system_info = Table()
        system_info.add_column("시스템", style="cyan")
        system_info.add_column("진입", style="green")
        system_info.add_column("청산", style="red")
        system_info.add_column("필터", style="yellow")
        system_info.add_column("특징", style="white")
        
        system_info.add_row(
            "시스템 1",
            "20일 돌파",
            "10일 돌파",
            "손실 필터",
            "더 빈번한 거래, 손실 후 대기"
        )
        system_info.add_row(
            "시스템 2", 
            "55일 돌파",
            "20일 돌파",
            "필터 없음",
            "더 큰 추세만 포착, 모든 신호 거래"
        )
        
        self.console.print(system_info)
        
        self.console.print("\n[bold white]사용할 시스템을 선택하세요:[/bold white]")
        
        system1 = Confirm.ask("시스템 1 사용하시겠습니까?", default=True)
        system2 = Confirm.ask("시스템 2 사용하시겠습니까?", default=True)
        
        systems = []
        if system1:
            systems.append(1)
        if system2:
            systems.append(2)
        
        if not systems:
            self.console.print("[red]최소 하나의 시스템은 선택해야 합니다. 시스템 1과 2를 모두 활성화합니다.[/red]")
            systems = [1, 2]
        
        self.config['systems'] = systems
        
        system_names = [f"시스템 {s}" for s in systems]
        self.console.print(f"[green]✅ 활성화된 시스템: {', '.join(system_names)}[/green]")
        self.console.print()
    
    def _configure_advanced(self):
        """고급 설정"""
        self.console.print("\n[bold yellow]🔧 고급 설정[/bold yellow]")
        
        # 수수료 설정
        commission_presets = {
            '1': (0.0000, '수수료 없음 (이상적인 환경)'),
            '2': (0.0004, 'Binance 일반 수수료 (0.04%)'),
            '3': (0.0010, '높은 수수료 (0.10%)'),
            '4': (0, '직접 입력')
        }
        
        comm_table = Table(title="수수료 설정")
        comm_table.add_column("선택", style="cyan")
        comm_table.add_column("수수료", style="green")
        comm_table.add_column("설명", style="white")
        
        for key, (rate, desc) in commission_presets.items():
            if key != '4':
                comm_table.add_row(key, f"{rate:.4f} ({rate*100:.2f}%)", desc)
            else:
                comm_table.add_row(key, "사용자 지정", desc)
        
        self.console.print(comm_table)
        
        choice = Prompt.ask("수수료를 선택하세요", choices=list(commission_presets.keys()), default='2')
        
        if choice == '4':
            while True:
                try:
                    rate = FloatPrompt.ask("수수료율을 입력하세요 (예: 0.0004 = 0.04%)")
                    if rate < 0:
                        self.console.print("[red]수수료는 0 이상이어야 합니다.[/red]")
                        continue
                    break
                except:
                    self.console.print("[red]올바른 숫자를 입력해주세요.[/red]")
            
            self.config['commission_rate'] = rate
        else:
            rate, _ = commission_presets[choice]
            self.config['commission_rate'] = rate
        
        self.console.print(f"[green]✅ 수수료가 설정되었습니다: {self.config['commission_rate']:.4f} ({self.config['commission_rate']*100:.2f}%)[/green]")
        self.console.print()
    
    def _confirm_settings(self) -> bool:
        """설정 확인"""
        self.console.print("\n[bold yellow]📋 백테스트 설정 확인[/bold yellow]")
        
        # 최종 설정 요약
        summary_panel = Panel(
            f"[bold white]백테스트 설정 요약[/bold white]\n\n"
            f"[cyan]종목:[/cyan] {self.config['symbol']}\n"
            f"[cyan]기간:[/cyan] {self.config['start_date']} ~ {self.config['end_date']}\n"
            f"[cyan]타임프레임:[/cyan] {self.config['timeframe']}\n"
            f"[cyan]초기 자금:[/cyan] ${self.config['initial_balance']:,.2f}\n"
            f"[cyan]수수료:[/cyan] {self.config['commission_rate']:.4f} ({self.config['commission_rate']*100:.2f}%)\n"
            f"[cyan]레버리지:[/cyan] {self.config['leverage']:.1f}x\n"
            f"[cyan]시스템:[/cyan] {', '.join(f'시스템 {s}' for s in self.config['systems'])}\n\n"
            f"[yellow]예상 소요 시간:[/yellow] 30초 ~ 5분\n"
            f"[yellow]예상 거래 수:[/yellow] 20 ~ 100회",
            style="green"
        )
        
        self.console.print(summary_panel)
        
        return Confirm.ask("\n이 설정으로 백테스트를 시작하시겠습니까?", default=True)

if __name__ == "__main__":
    # 테스트 실행
    setup_ui = BacktestSetupUI()
    config = setup_ui.show_setup_screen()
    
    if config:
        print("\n최종 설정:")
        for key, value in config.items():
            print(f"  {key}: {value}")
    else:
        print("\n백테스트가 취소되었습니다.")
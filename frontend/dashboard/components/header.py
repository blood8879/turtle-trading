"""
대시보드 헤더 컴포넌트
"""

from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from datetime import datetime
from typing import Dict, Any

class HeaderComponent:
    """대시보드 헤더 컴포넌트"""
    
    def __init__(self):
        self.app_name = "Bitcoin Futures Turtle Trading Bot"
        self.version = "v1.0.0"
    
    def create_header(self, mode: str, status: str, is_running: bool) -> Panel:
        """헤더 패널 생성"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 모드에 따른 색상
        mode_colors = {
            "live": "red",
            "paper": "yellow",
            "backtest": "blue"
        }
        mode_color = mode_colors.get(mode.lower(), "white")
        
        # 상태에 따른 색상
        status_color = "green" if is_running else "red"
        
        # 헤더 텍스트 구성
        header_parts = [
            f"[bold cyan]{self.app_name}[/bold cyan]",
            f"Mode: [{mode_color}]{mode.upper()}[/{mode_color}]",
            f"Status: [{status_color}]{status}[/{status_color}]",
            f"Time: [blue]{current_time}[/blue]"
        ]
        
        header_text = "  |  ".join(header_parts)
        
        return Panel(
            Align.center(header_text),
            style="cyan",
            padding=(0, 1)
        )
    
    def create_connection_status(self, api_connected: bool, data_feed_active: bool) -> Text:
        """연결 상태 표시"""
        api_status = "[green]●[/green]" if api_connected else "[red]●[/red]"
        feed_status = "[green]●[/green]" if data_feed_active else "[red]●[/red]"
        
        return Text.from_markup(
            f"API: {api_status}  Data: {feed_status}"
        )
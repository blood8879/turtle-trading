"""
포지션 정보 컴포넌트
"""

from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from typing import Dict, Any, List
from datetime import datetime, timedelta

class PositionsComponent:
    """포지션 정보 컴포넌트"""
    
    def __init__(self):
        self.positions = {}
        self.current_prices = {}
    
    def update_positions(self, positions: Dict[str, Any], current_prices: Dict[str, float]):
        """포지션 데이터 업데이트"""
        self.positions = positions
        self.current_prices = current_prices
    
    def create_positions_panel(self, positions: Dict[str, Any], current_prices: Dict[str, float]) -> Panel:
        """포지션 패널 생성"""
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
        pos_table.add_column("P&L", style="bold", width=12)
        pos_table.add_column("Duration", style="dim", width=8)
        
        for symbol, position in positions.items():
            current_price = current_prices.get(symbol, position.avg_price)
            
            # 미실현 손익 계산
            if position.direction == "LONG":
                unrealized_pnl = (current_price - position.avg_price) * position.total_size
            else:  # SHORT
                unrealized_pnl = (position.avg_price - current_price) * position.total_size
            
            # 수익률 계산
            position_value = position.avg_price * position.total_size
            pnl_pct = (unrealized_pnl / position_value) * 100 if position_value > 0 else 0
            
            # 포지션 지속 기간
            if position.units:
                duration = datetime.now() - position.units[0].entry_date
                duration_str = self._format_duration(duration)
            else:
                duration_str = "N/A"
            
            # 색상 결정
            direction_color = "green" if position.direction == "LONG" else "red"
            pnl_color = "green" if unrealized_pnl >= 0 else "red"
            
            pos_table.add_row(
                symbol[:8],
                f"[{direction_color}]{position.direction}[/{direction_color}]",
                f"{position.total_size:.3f}",
                f"${position.avg_price:,.0f}",
                f"${current_price:,.0f}",
                f"[{pnl_color}]{unrealized_pnl:+.0f} ({pnl_pct:+.1f}%)[/{pnl_color}]",
                duration_str
            )
        
        return Panel(
            pos_table,
            title="📊 Current Positions",
            title_align="left",
            style="blue"
        )
    
    def create_position_details_panel(self, symbol: str, position: Any, current_price: float) -> Panel:
        """특정 포지션의 상세 정보 패널"""
        details_table = Table.grid()
        details_table.add_column(style="cyan", width=15)
        details_table.add_column(style="white", width=20)
        
        # 기본 정보
        details_table.add_row("Symbol:", symbol)
        details_table.add_row("Direction:", position.direction)
        details_table.add_row("Total Size:", f"{position.total_size:.6f}")
        details_table.add_row("Average Price:", f"${position.avg_price:,.2f}")
        details_table.add_row("Current Price:", f"${current_price:,.2f}")
        
        # 미실현 손익
        if position.direction == "LONG":
            unrealized_pnl = (current_price - position.avg_price) * position.total_size
        else:
            unrealized_pnl = (position.avg_price - current_price) * position.total_size
        
        pnl_color = "green" if unrealized_pnl >= 0 else "red"
        details_table.add_row(
            "Unrealized P&L:",
            f"[{pnl_color}]{unrealized_pnl:+.2f}[/{pnl_color}]"
        )
        
        # 유닛별 정보
        if position.units:
            details_table.add_row("", "")  # 빈 줄
            details_table.add_row("[bold]Units:[/bold]", "")
            
            for i, unit in enumerate(position.units, 1):
                unit_pnl = self._calculate_unit_pnl(unit, current_price, position.direction)
                unit_color = "green" if unit_pnl >= 0 else "red"
                
                details_table.add_row(
                    f"  Unit {unit.unit_number}:",
                    f"${unit.entry_price:,.0f} → [{unit_color}]{unit_pnl:+.0f}[/{unit_color}]"
                )
                details_table.add_row(
                    f"    Stop Loss:",
                    f"${unit.stop_loss:,.0f}"
                )
        
        return Panel(
            details_table,
            title=f"Position Details - {symbol}",
            style="yellow"
        )
    
    def get_positions_summary(self, positions: Dict[str, Any], current_prices: Dict[str, float]) -> Dict[str, Any]:
        """포지션 요약 정보"""
        if not positions:
            return {
                'total_positions': 0,
                'long_positions': 0,
                'short_positions': 0,
                'total_unrealized_pnl': 0.0,
                'total_margin_used': 0.0
            }
        
        total_unrealized = 0.0
        total_margin = 0.0
        long_count = 0
        short_count = 0
        
        for symbol, position in positions.items():
            current_price = current_prices.get(symbol, position.avg_price)
            
            # 미실현 손익
            if position.direction == "LONG":
                unrealized = (current_price - position.avg_price) * position.total_size
                long_count += 1
            else:
                unrealized = (position.avg_price - current_price) * position.total_size
                short_count += 1
            
            total_unrealized += unrealized
            
            # 마진 사용량 추정
            position_value = position.total_size * current_price
            total_margin += position_value * 0.1  # 10% 마진으로 가정
        
        return {
            'total_positions': len(positions),
            'long_positions': long_count,
            'short_positions': short_count,
            'total_unrealized_pnl': total_unrealized,
            'total_margin_used': total_margin
        }
    
    def get_risk_exposure(self, positions: Dict[str, Any], current_prices: Dict[str, float]) -> Dict[str, float]:
        """포지션 리스크 노출도"""
        total_long_exposure = 0.0
        total_short_exposure = 0.0
        
        for symbol, position in positions.items():
            current_price = current_prices.get(symbol, position.avg_price)
            position_value = position.total_size * current_price
            
            if position.direction == "LONG":
                total_long_exposure += position_value
            else:
                total_short_exposure += position_value
        
        total_exposure = total_long_exposure + total_short_exposure
        
        return {
            'total_exposure': total_exposure,
            'long_exposure': total_long_exposure,
            'short_exposure': total_short_exposure,
            'net_exposure': total_long_exposure - total_short_exposure,
            'long_ratio': (total_long_exposure / total_exposure) * 100 if total_exposure > 0 else 0,
            'short_ratio': (total_short_exposure / total_exposure) * 100 if total_exposure > 0 else 0
        }
    
    def _calculate_unit_pnl(self, unit: Any, current_price: float, direction: str) -> float:
        """개별 유닛의 손익 계산"""
        if direction == "LONG":
            return (current_price - unit.entry_price) * unit.size
        else:  # SHORT
            return (unit.entry_price - current_price) * unit.size
    
    def _format_duration(self, duration: timedelta) -> str:
        """지속 기간 포맷팅"""
        total_seconds = int(duration.total_seconds())
        days = total_seconds // 86400
        hours = (total_seconds % 86400) // 3600
        minutes = (total_seconds % 3600) // 60
        
        if days > 0:
            return f"{days}d {hours}h"
        elif hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m"
    
    def create_units_breakdown_panel(self, position: Any, current_price: float) -> Panel:
        """유닛별 상세 분석 패널"""
        if not position.units:
            return Panel(
                Text("No units data", style="dim"),
                title="Units Breakdown"
            )
        
        units_table = Table()
        units_table.add_column("Unit", style="cyan", width=6)
        units_table.add_column("System", style="yellow", width=8)
        units_table.add_column("Entry", style="blue", width=10)
        units_table.add_column("Size", style="white", width=8)
        units_table.add_column("Stop Loss", style="red", width=10)
        units_table.add_column("P&L", style="bold", width=10)
        units_table.add_column("Risk", style="orange", width=8)
        
        for unit in position.units:
            unit_pnl = self._calculate_unit_pnl(unit, current_price, position.direction)
            pnl_color = "green" if unit_pnl >= 0 else "red"
            
            # 리스크 계산 (현재가와 손절가의 차이)
            if position.direction == "LONG":
                risk = (current_price - unit.stop_loss) * unit.size
            else:
                risk = (unit.stop_loss - current_price) * unit.size
            
            risk_color = "red" if risk < 0 else "green"
            
            units_table.add_row(
                f"#{unit.unit_number}",
                f"S{unit.system}",
                f"${unit.entry_price:,.0f}",
                f"{unit.size:.3f}",
                f"${unit.stop_loss:,.0f}",
                f"[{pnl_color}]{unit_pnl:+.0f}[/{pnl_color}]",
                f"[{risk_color}]{risk:+.0f}[/{risk_color}]"
            )
        
        return Panel(
            units_table,
            title=f"Units Breakdown - {position.symbol}",
            style="magenta"
        )
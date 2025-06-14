"""
백테스트 엔진 테스트
"""

import pytest
import asyncio
import sys
from pathlib import Path
from datetime import datetime, timedelta

# 프로젝트 루트를 파이썬 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from frontend.backtest.backend.engines.backtest_engine import (
    BacktestEngine, BacktestConfig_, BacktestResults, 
    PerformanceMetrics, BacktestResultsManager
)
from strategy.turtle_strategy import PriceData, TradeResult

class TestBacktestConfig:
    """백테스트 설정 테스트"""
    
    def test_default_config_creation(self):
        """기본 설정 생성 테스트"""
        config = BacktestConfig_()
        
        assert config.symbol == "BTCUSDT", "기본 심볼이 BTCUSDT여야 합니다"
        assert config.timeframe == "1d", "기본 타임프레임이 1d여야 합니다"
        assert config.initial_balance == 10000.0, "기본 초기 자금이 10000이어야 합니다"
        assert config.systems == [1, 2], "기본 시스템이 [1, 2]여야 합니다"
    
    def test_custom_config_creation(self):
        """커스텀 설정 생성 테스트"""
        config = BacktestConfig_(
            symbol="ETHUSDT",
            start_date="2023-06-01",
            end_date="2023-12-31",
            timeframe="4h",
            initial_balance=20000.0,
            systems=[1]
        )
        
        assert config.symbol == "ETHUSDT", "심볼이 정확해야 합니다"
        assert config.start_date == "2023-06-01", "시작일이 정확해야 합니다"
        assert config.end_date == "2023-12-31", "종료일이 정확해야 합니다"
        assert config.timeframe == "4h", "타임프레임이 정확해야 합니다"
        assert config.initial_balance == 20000.0, "초기 자금이 정확해야 합니다"
        assert config.systems == [1], "시스템이 정확해야 합니다"

class TestBacktestEngine:
    """백테스트 엔진 테스트"""
    
    def setup_method(self):
        """테스트 설정"""
        self.config = BacktestConfig_(
            symbol="BTCUSDT",
            start_date="2024-01-01",
            end_date="2024-01-31",
            timeframe="1d",
            initial_balance=10000.0,
            systems=[1, 2]
        )
        self.engine = BacktestEngine(self.config)
    
    @pytest.mark.asyncio
    async def test_historical_data_loading(self):
        """과거 데이터 로딩 테스트"""
        data = await self.engine.load_historical_data()
        
        assert len(data) > 0, "데이터가 로드되어야 합니다"
        assert all(isinstance(item, PriceData) for item in data), "모든 데이터가 PriceData 타입이어야 합니다"
        
        # 데이터 순서 확인
        for i in range(1, len(data)):
            assert data[i].date >= data[i-1].date, "데이터가 시간순으로 정렬되어야 합니다"
        
        # 기본 데이터 검증
        for item in data[:5]:  # 처음 5개만 확인
            assert item.symbol == self.config.symbol, "심볼이 일치해야 합니다"
            assert item.high >= item.low, "고가가 저가보다 크거나 같아야 합니다"
            assert item.high >= item.open, "고가가 시가보다 크거나 같아야 합니다"
            assert item.high >= item.close, "고가가 종가보다 크거나 같아야 합니다"
            assert item.low <= item.open, "저가가 시가보다 작거나 같아야 합니다"
            assert item.low <= item.close, "저가가 종가보다 작거나 같아야 합니다"
            assert item.volume > 0, "거래량이 0보다 커야 합니다"
    
    @pytest.mark.asyncio
    async def test_backtest_execution(self):
        """백테스트 실행 테스트"""
        results = await self.engine.run_backtest()
        
        assert isinstance(results, BacktestResults), "결과가 BacktestResults 타입이어야 합니다"
        assert results.initial_balance == self.config.initial_balance, "초기 자금이 일치해야 합니다"
        assert results.final_balance > 0, "최종 자금이 0보다 커야 합니다"
        
        # 성과 지표 검증
        metrics = results.metrics
        assert isinstance(metrics, PerformanceMetrics), "지표가 PerformanceMetrics 타입이어야 합니다"
        assert 0 <= metrics.win_rate <= 1, "승률이 0과 1 사이여야 합니다"
        assert metrics.max_drawdown >= 0, "최대 드로다운이 0 이상이어야 합니다"
        
        # 거래 내역 검증
        assert isinstance(results.trades, list), "거래 내역이 리스트여야 합니다"
        assert all(isinstance(trade, TradeResult) for trade in results.trades), "모든 거래가 TradeResult 타입이어야 합니다"
        
        # 수익 곡선 검증
        assert isinstance(results.equity_curve, list), "수익 곡선이 리스트여야 합니다"
        if results.equity_curve:
            assert all('date' in point and 'total_value' in point for point in results.equity_curve), "수익 곡선 포인트가 올바른 형식이어야 합니다"
    
    @pytest.mark.asyncio
    async def test_short_period_backtest(self):
        """짧은 기간 백테스트 테스트"""
        short_config = BacktestConfig_(
            symbol="BTCUSDT",
            start_date="2024-01-01",
            end_date="2024-01-10",  # 10일만
            timeframe="1d",
            initial_balance=5000.0
        )
        
        short_engine = BacktestEngine(short_config)
        
        # 너무 짧은 기간은 예외 발생해야 함
        with pytest.raises(ValueError, match="최소 30일"):
            await short_engine.run_backtest()
    
    def test_portfolio_value_calculation(self):
        """포트폴리오 가치 계산 테스트"""
        # 포지션이 없을 때
        value = self.engine._calculate_portfolio_value(50000)
        assert value == self.engine.current_balance, "포지션이 없으면 현재 잔고와 같아야 합니다"
    
    def test_commission_application(self):
        """수수료 적용 테스트"""
        initial_balance = self.engine.current_balance
        trade_value = 1000.0
        
        self.engine._apply_commission(trade_value)
        
        expected_commission = trade_value * self.config.commission_rate
        expected_balance = initial_balance - expected_commission
        
        assert abs(self.engine.current_balance - expected_balance) < 0.01, "수수료가 정확히 적용되어야 합니다"
    
    def test_can_add_position_logic(self):
        """포지션 추가 가능 여부 로직 테스트"""
        # 초기에는 포지션 추가 가능해야 함
        assert self.engine._can_add_position(), "초기에는 포지션 추가가 가능해야 합니다"
    
    def test_used_margin_calculation(self):
        """사용 마진 계산 테스트"""
        margin = self.engine._calculate_used_margin()
        assert margin >= 0, "사용 마진이 0 이상이어야 합니다"

class TestPerformanceMetrics:
    """성과 지표 테스트"""
    
    def test_metrics_creation(self):
        """지표 생성 테스트"""
        metrics = PerformanceMetrics(
            total_return=0.25,
            annual_return=0.20,
            max_drawdown=0.10,
            sharpe_ratio=1.5,
            win_rate=0.65,
            profit_factor=1.8,
            total_trades=50
        )
        
        assert metrics.total_return == 0.25, "총 수익률이 정확해야 합니다"
        assert metrics.annual_return == 0.20, "연 수익률이 정확해야 합니다"
        assert metrics.max_drawdown == 0.10, "최대 드로다운이 정확해야 합니다"
        assert metrics.sharpe_ratio == 1.5, "샤프 비율이 정확해야 합니다"
        assert metrics.win_rate == 0.65, "승률이 정확해야 합니다"
        assert metrics.profit_factor == 1.8, "수익 팩터가 정확해야 합니다"
        assert metrics.total_trades == 50, "총 거래 수가 정확해야 합니다"
    
    def test_metrics_defaults(self):
        """지표 기본값 테스트"""
        metrics = PerformanceMetrics()
        
        assert metrics.total_return == 0.0, "기본 총 수익률이 0이어야 합니다"
        assert metrics.win_rate == 0.0, "기본 승률이 0이어야 합니다"
        assert metrics.total_trades == 0, "기본 거래 수가 0이어야 합니다"

class TestBacktestResults:
    """백테스트 결과 테스트"""
    
    def setup_method(self):
        """테스트 설정"""
        self.config = BacktestConfig_()
        self.metrics = PerformanceMetrics(
            total_return=0.15,
            win_rate=0.60,
            total_trades=30
        )
        
        self.results = BacktestResults(
            config=self.config,
            initial_balance=10000,
            final_balance=11500,
            metrics=self.metrics,
            trades=[],
            equity_curve=[],
            monthly_returns={}
        )
    
    def test_results_creation(self):
        """결과 생성 테스트"""
        assert self.results.initial_balance == 10000, "초기 자금이 정확해야 합니다"
        assert self.results.final_balance == 11500, "최종 자금이 정확해야 합니다"
        assert self.results.metrics.total_return == 0.15, "수익률이 정확해야 합니다"
    
    def test_results_to_dict(self):
        """결과 딕셔너리 변환 테스트"""
        result_dict = self.results.to_dict()
        
        assert isinstance(result_dict, dict), "딕셔너리 타입이어야 합니다"
        assert 'config' in result_dict, "설정이 포함되어야 합니다"
        assert 'initial_balance' in result_dict, "초기 자금이 포함되어야 합니다"
        assert 'final_balance' in result_dict, "최종 자금이 포함되어야 합니다"
        assert 'metrics' in result_dict, "지표가 포함되어야 합니다"
        assert 'trades' in result_dict, "거래 내역이 포함되어야 합니다"
        assert 'equity_curve' in result_dict, "수익 곡선이 포함되어야 합니다"
        assert 'monthly_returns' in result_dict, "월별 수익률이 포함되어야 합니다"

class TestBacktestResultsManager:
    """백테스트 결과 관리자 테스트"""
    
    def setup_method(self):
        """테스트 설정"""
        self.config = BacktestConfig_()
        self.metrics = PerformanceMetrics()
        self.results = BacktestResults(
            config=self.config,
            initial_balance=10000,
            final_balance=11000,
            metrics=self.metrics,
            trades=[],
            equity_curve=[],
            monthly_returns={}
        )
        
        # 테스트 디렉토리 생성
        import os
        os.makedirs("data/backtest_results", exist_ok=True)
    
    def test_save_and_load_results(self):
        """결과 저장 및 로드 테스트"""
        test_filename = "test_backtest_result"
        
        # 저장
        BacktestResultsManager.save_results(self.results, test_filename)
        
        # 로드
        loaded_data = BacktestResultsManager.load_results(test_filename)
        
        assert loaded_data is not None, "데이터가 로드되어야 합니다"
        assert loaded_data['initial_balance'] == 10000, "초기 자금이 일치해야 합니다"
        assert loaded_data['final_balance'] == 11000, "최종 자금이 일치해야 합니다"
        
        # 테스트 파일 정리
        import os
        test_file_path = f"data/backtest_results/{test_filename}.json"
        if os.path.exists(test_file_path):
            os.remove(test_file_path)
    
    def test_load_nonexistent_file(self):
        """존재하지 않는 파일 로드 테스트"""
        result = BacktestResultsManager.load_results("nonexistent_file")
        assert result is None, "존재하지 않는 파일은 None을 반환해야 합니다"

class TestBacktestIntegration:
    """백테스트 통합 테스트"""
    
    @pytest.mark.asyncio
    async def test_full_backtest_workflow(self):
        """전체 백테스트 워크플로우 테스트"""
        # 1. 설정 생성
        config = BacktestConfig_(
            symbol="BTCUSDT",
            start_date="2024-01-01",
            end_date="2024-02-29",  # 2개월
            timeframe="1d",
            initial_balance=15000.0,
            commission_rate=0.0005,
            systems=[1, 2]
        )
        
        # 2. 엔진 생성 및 실행
        engine = BacktestEngine(config)
        results = await engine.run_backtest()
        
        # 3. 결과 검증
        assert results.config.symbol == "BTCUSDT", "설정이 보존되어야 합니다"
        assert results.initial_balance == 15000.0, "초기 자금이 설정값과 일치해야 합니다"
        
        # 4. 결과 저장 및 로드
        test_filename = "integration_test_result"
        BacktestResultsManager.save_results(results, test_filename)
        
        loaded_data = BacktestResultsManager.load_results(test_filename)
        assert loaded_data is not None, "저장된 결과를 로드할 수 있어야 합니다"
        
        # 정리
        import os
        test_file_path = f"data/backtest_results/{test_filename}.json"
        if os.path.exists(test_file_path):
            os.remove(test_file_path)
    
    @pytest.mark.asyncio
    async def test_different_timeframes(self):
        """다양한 타임프레임 테스트"""
        timeframes = ["1h", "4h", "1d"]
        
        for tf in timeframes:
            config = BacktestConfig_(
                symbol="BTCUSDT",
                start_date="2024-01-01",
                end_date="2024-01-31",
                timeframe=tf,
                initial_balance=10000.0
            )
            
            engine = BacktestEngine(config)
            results = await engine.run_backtest()
            
            assert results.config.timeframe == tf, f"타임프레임 {tf}가 보존되어야 합니다"
            assert results.final_balance > 0, f"타임프레임 {tf}에서 최종 자금이 0보다 커야 합니다"

if __name__ == "__main__":
    # 테스트 실행
    pytest.main([__file__, "-v", "-s"])
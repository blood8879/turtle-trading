#!/usr/bin/env python3
"""
매매일지 기능 단독 테스트 스크립트
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import TradingMode
from utils.trade_journal import TradeJournalManager, get_trade_journal_manager


def test_trade_journal():
    """매매일지 기능 테스트"""
    print("📊 매매일지 기능 테스트 시작")
    
    try:
        # 각 거래 모드별 테스트
        modes = [
            (TradingMode.BACKTEST, "백테스트"),
            (TradingMode.PAPER, "테스트매매"), 
            (TradingMode.LIVE, "실제매매")
        ]
        
        for mode, mode_name in modes:
            print(f"\n--- {mode_name} 매매일지 테스트 ---")
            
            # 매매일지 관리자 생성
            journal = get_trade_journal_manager(mode)
            
            # 테스트 거래 기록
            print("1. 진입 거래 기록...")
            trade_id = journal.log_trade_entry(
                symbol="BTCUSDT",
                direction="LONG",
                entry_price=50000.0,
                size=0.1,
                stop_loss=49000.0,
                atr=1000.0,
                leverage=2.0,
                account_balance=10000.0,
                system=1,
                notes=f"{mode_name} 테스트 진입"
            )
            print(f"생성된 거래 ID: {trade_id}")
            
            # 피라미딩 기록
            print("2. 피라미딩 기록...")
            journal.log_pyramid_entry(
                trade_id=trade_id,
                symbol="BTCUSDT",
                direction="LONG",
                entry_price=50500.0,
                size=0.05,
                stop_loss=49500.0,
                atr=1000.0,
                leverage=2.0,
                account_balance=9950.0,
                system=1,
                unit_number=2,
                notes=f"{mode_name} 테스트 피라미딩"
            )
            
            # 청산 기록
            print("3. 청산 기록...")
            journal.log_trade_exit(
                trade_id=trade_id,
                symbol="BTCUSDT",
                direction="LONG",
                entry_price=50250.0,
                exit_price=51000.0,
                size=0.15,
                pnl=112.5,
                account_balance=10112.5,
                reason="SIGNAL",
                leverage=2.0,
                notes=f"{mode_name} 테스트 청산"
            )
            
            # 일일 요약 조회
            print("4. 일일 요약 조회...")
            summary = journal.get_daily_summary()
            print(f"일일 요약: {summary}")
            
            # 거래 내역 조회
            print("5. 거래 내역 조회...")
            history = journal.get_trade_history()
            print(f"총 {len(history)}개 기록")
            
            print(f"✅ {mode_name} 테스트 완료!")
        
        print("\n📁 생성된 파일들 확인:")
        
        # 생성된 CSV 파일들 확인
        import glob
        from datetime import datetime
        today = datetime.now().strftime('%Y%m%d')
        
        csv_files = glob.glob(f"data/trade_journals/*/*/*{today}.csv")
        for csv_file in csv_files:
            print(f"  📄 {csv_file}")
            
        # 생성된 로그 파일들 확인
        log_files = glob.glob("logs/*trade_journal.log")
        for log_file in log_files:
            print(f"  📋 {log_file}")
        
        return True
        
    except Exception as e:
        print(f"❌ 매매일지 테스트 오류: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_trade_journal()
    if success:
        print("\n🎉 매매일지 테스트 성공!")
        sys.exit(0)
    else:
        print("\n💥 매매일지 테스트 실패!")
        sys.exit(1)
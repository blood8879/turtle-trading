"""
Bitcoin Futures Turtle Trading Bot - 메인 실행 파일
"""

import asyncio
import sys
import os
import logging
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 로깅 설정
from config import LoggingConfig, DataConfig

def setup_logging():
    """로깅 설정"""
    # 로그 디렉토리 생성
    os.makedirs(DataConfig.LOGS_DIR, exist_ok=True)
    
    # 로깅 설정
    logging.basicConfig(
        level=getattr(logging, LoggingConfig.LOG_LEVEL),
        format=LoggingConfig.LOG_FORMAT,
        handlers=[
            logging.FileHandler(LoggingConfig.MAIN_LOG_FILE, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # 애플리케이션 로거
    logger = logging.getLogger(__name__)
    return logger

def check_dependencies():
    """필수 의존성 검사"""
    # 패키지 이름: (pip 설치명, import 이름)
    required_packages = {
        'rich': 'rich',
        'pandas': 'pandas', 
        'numpy': 'numpy',
        'python-dotenv': 'dotenv',  # pip로는 python-dotenv, import는 dotenv
        'asyncio': 'asyncio',
        'datetime': 'datetime',
        'json': 'json'
    }
    
    missing_packages = []
    
    for pip_name, import_name in required_packages.items():
        try:
            __import__(import_name)
        except ImportError:
            missing_packages.append(pip_name)
    
    if missing_packages:
        print(f"❌ 다음 패키지가 설치되지 않았습니다: {', '.join(missing_packages)}")
        print("다음 명령어로 설치하세요:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    return True

def check_environment():
    """환경 설정 검사"""
    try:
        from config import validate_config
        validate_config()
        return True
    except Exception as e:
        print(f"❌ 환경 설정 오류: {e}")
        print("💡 .env 파일을 확인하고 올바른 설정을 입력하세요.")
        print("📄 .env.example 파일을 참고하세요.")
        return False

def show_startup_banner():
    """시작 배너 표시"""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║    🐢 Bitcoin Futures Turtle Trading Bot                    ║
║                                                              ║
║    Professional Algorithmic Trading System                  ║
║    Based on Original Turtle Trading Rules                   ║
║                                                              ║
║    🔹 Dual System Support (20-day & 55-day breakouts)       ║
║    🔹 Advanced Risk Management                               ║
║    🔹 Comprehensive Backtesting                              ║
║    🔹 Real-time Dashboard                                    ║
║    🔹 Paper & Live Trading                                   ║
║                                                              ║
║    ⚠️  Trading involves risk. Use at your own discretion.    ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
"""
    print(banner)

async def main():
    """메인 실행 함수"""
    # 시작 배너
    show_startup_banner()
    
    # 로깅 설정
    logger = setup_logging()
    logger.info("🚀 Bitcoin Futures Turtle Trading Bot 시작")
    
    # 의존성 검사
    if not check_dependencies():
        print("\n❌ 의존성 검사 실패. 프로그램을 종료합니다.")
        return 1
    
    # 환경 설정 검사
    if not check_environment():
        print("\n❌ 환경 설정 검사 실패. 프로그램을 종료합니다.")
        return 1
    
    # 데이터 디렉토리 생성
    try:
        os.makedirs(DataConfig.HISTORICAL_DIR, exist_ok=True)
        os.makedirs(DataConfig.BACKTEST_RESULTS_DIR, exist_ok=True)
        os.makedirs(DataConfig.LIVE_TRADING_DIR, exist_ok=True)
        logger.info("✅ 데이터 디렉토리 확인 완료")
    except Exception as e:
        logger.error(f"❌ 데이터 디렉토리 생성 실패: {e}")
        return 1
    
    # 메인 UI 시작
    try:
        from frontend.main_menu import MainMenuUI
        
        logger.info("🎯 메인 메뉴 UI 시작")
        menu = MainMenuUI()
        await menu.show()
        
        logger.info("👋 프로그램 정상 종료")
        return 0
        
    except KeyboardInterrupt:
        logger.info("⏹️ 사용자에 의해 프로그램이 중단됨")
        print("\n\n👋 프로그램이 중단되었습니다. 안녕히 가세요!")
        return 0
        
    except Exception as e:
        logger.error(f"💥 예상치 못한 오류 발생: {e}", exc_info=True)
        print(f"\n❌ 오류가 발생했습니다: {e}")
        print("📋 자세한 정보는 로그 파일을 확인하세요.")
        return 1

def cli_main():
    """CLI 진입점"""
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n👋 프로그램이 중단되었습니다.")
        sys.exit(0)
    except Exception as e:
        print(f"\n💥 치명적 오류: {e}")
        sys.exit(1)

if __name__ == "__main__":
    cli_main()
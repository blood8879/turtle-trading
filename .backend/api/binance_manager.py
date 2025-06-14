"""
Binance API 관리자 - 실제 거래 및 과거 데이터 조회
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import pandas as pd
from binance.client import Client
from binance.exceptions import BinanceAPIException
import time
import json

from strategy.turtle_strategy import PriceData
from config import BinanceConfig

logger = logging.getLogger(__name__)

class BinanceManager:
    """Binance API 관리자"""
    
    def __init__(self, mode: str = "paper"):
        """
        mode: 'live', 'paper', 'backtest'
        """
        self.mode = mode
        self.client = None
        
        if mode == "live":
            if not BinanceConfig.API_KEY or not BinanceConfig.SECRET_KEY:
                raise ValueError("Live trading requires API keys")
            self.client = Client(BinanceConfig.API_KEY, BinanceConfig.SECRET_KEY, 
                               testnet=BinanceConfig.TESTNET)
        elif mode in ["paper", "backtest"]:
            # Paper trading용 클라이언트 (API 키 없이 데이터만 조회)
            self.client = Client()
        
        # API 제한 관리
        self.last_request_time = 0
        self.request_count = 0
        self.daily_request_count = 0
        self.last_daily_reset = datetime.now().date()
        
    async def get_historical_klines(self, symbol: str, interval: str, 
                                  start_time: str, end_time: str = None, 
                                  limit: int = 1000) -> List[PriceData]:
        """과거 캔들 데이터 조회"""
        try:
            await self._check_rate_limit()
            
            # Binance API 호출
            klines = self.client.get_historical_klines(
                symbol=symbol,
                interval=interval,
                start_str=start_time,
                end_str=end_time,
                limit=limit
            )
            
            # PriceData 객체로 변환
            price_data = []
            for kline in klines:
                price_data.append(PriceData(
                    symbol=symbol,
                    date=datetime.fromtimestamp(kline[0] / 1000),
                    open=float(kline[1]),
                    high=float(kline[2]),
                    low=float(kline[3]),
                    close=float(kline[4]),
                    volume=float(kline[5])
                ))
            
            logger.info(f"Retrieved {len(price_data)} historical data points for {symbol}")
            return price_data
            
        except BinanceAPIException as e:
            logger.error(f"Binance API error: {e}")
            raise
        except Exception as e:
            logger.error(f"Error retrieving historical data: {e}")
            raise
    
    async def get_current_price(self, symbol: str) -> float:
        """현재 가격 조회"""
        try:
            await self._check_rate_limit()
            
            ticker = self.client.get_symbol_ticker(symbol=symbol)
            return float(ticker['price'])
            
        except BinanceAPIException as e:
            logger.error(f"Error getting current price for {symbol}: {e}")
            raise
    
    async def get_klines(self, symbol: str, interval: str, limit: int = 100) -> List[PriceData]:
        """최근 캔들 데이터 조회"""
        try:
            await self._check_rate_limit()
            
            klines = self.client.get_klines(
                symbol=symbol,
                interval=interval,
                limit=limit
            )
            
            price_data = []
            for kline in klines:
                price_data.append(PriceData(
                    symbol=symbol,
                    date=datetime.fromtimestamp(kline[0] / 1000),
                    open=float(kline[1]),
                    high=float(kline[2]),
                    low=float(kline[3]),
                    close=float(kline[4]),
                    volume=float(kline[5])
                ))
            
            return price_data
            
        except BinanceAPIException as e:
            logger.error(f"Error getting klines for {symbol}: {e}")
            raise
    
    async def place_order(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """주문 실행"""
        if self.mode != "live":
            # Paper trading mode에서는 가상 주문 처리
            return await self._simulate_order(order_data)
        
        try:
            await self._check_rate_limit()
            
            # 실제 주문 실행
            if order_data['side'] == 'BUY':
                result = self.client.order_market_buy(
                    symbol=order_data['symbol'],
                    quantity=order_data['quantity']
                )
            else:  # SELL
                result = self.client.order_market_sell(
                    symbol=order_data['symbol'],
                    quantity=order_data['quantity']
                )
            
            logger.info(f"Order executed: {result}")
            return result
            
        except BinanceAPIException as e:
            logger.error(f"Order execution failed: {e}")
            raise
    
    async def get_account_info(self) -> Dict[str, Any]:
        """계좌 정보 조회"""
        if self.mode != "live":
            # Paper trading용 더미 계좌 정보
            return {
                'balances': [
                    {'asset': 'USDT', 'free': '10000.0', 'locked': '0.0'},
                    {'asset': 'BTC', 'free': '0.0', 'locked': '0.0'}
                ],
                'canTrade': True,
                'canWithdraw': True,
                'canDeposit': True
            }
        
        try:
            await self._check_rate_limit()
            return self.client.get_account()
            
        except BinanceAPIException as e:
            logger.error(f"Error getting account info: {e}")
            raise
    
    async def get_open_orders(self, symbol: str = None) -> List[Dict[str, Any]]:
        """미체결 주문 조회"""
        if self.mode != "live":
            return []  # Paper trading에서는 미체결 주문 없음
        
        try:
            await self._check_rate_limit()
            return self.client.get_open_orders(symbol=symbol)
            
        except BinanceAPIException as e:
            logger.error(f"Error getting open orders: {e}")
            raise
    
    async def cancel_order(self, symbol: str, order_id: int) -> Dict[str, Any]:
        """주문 취소"""
        if self.mode != "live":
            return {'status': 'CANCELED'}  # Paper trading용 더미 응답
        
        try:
            await self._check_rate_limit()
            return self.client.cancel_order(symbol=symbol, orderId=order_id)
            
        except BinanceAPIException as e:
            logger.error(f"Error canceling order: {e}")
            raise
    
    async def _simulate_order(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """가상 주문 처리 (Paper Trading)"""
        # 현재 가격 조회
        current_price = await self.get_current_price(order_data['symbol'])
        
        # 가상 주문 결과 생성
        result = {
            'symbol': order_data['symbol'],
            'orderId': int(time.time() * 1000),  # 임시 주문 ID
            'side': order_data['side'],
            'type': 'MARKET',
            'quantity': order_data['quantity'],
            'price': current_price,
            'status': 'FILLED',
            'executedQty': order_data['quantity'],
            'transactTime': int(time.time() * 1000)
        }
        
        logger.info(f"Simulated order: {result}")
        return result
    
    async def _check_rate_limit(self):
        """API 제한 확인 및 대기"""
        now = time.time()
        
        # 일일 요청 수 리셋
        today = datetime.now().date()
        if today != self.last_daily_reset:
            self.daily_request_count = 0
            self.last_daily_reset = today
        
        # 분당 요청 수 확인
        if now - self.last_request_time < 60:
            self.request_count += 1
        else:
            self.request_count = 1
        
        if self.request_count > BinanceConfig.REQUESTS_PER_MINUTE:
            sleep_time = 60 - (now - self.last_request_time)
            if sleep_time > 0:
                logger.warning(f"Rate limit exceeded, sleeping for {sleep_time:.2f} seconds")
                await asyncio.sleep(sleep_time)
                self.request_count = 1
        
        # 일일 요청 수 확인
        self.daily_request_count += 1
        if self.daily_request_count > BinanceConfig.ORDERS_PER_DAY:
            logger.error("Daily request limit exceeded")
            raise Exception("Daily API request limit exceeded")
        
        self.last_request_time = now

class HistoricalDataManager:
    """과거 데이터 관리자"""
    
    def __init__(self, binance_manager: BinanceManager):
        self.binance_manager = binance_manager
        self.cache = {}
        
    async def get_price_data(self, symbol: str, interval: str, 
                           start_date: str, end_date: str = None) -> List[PriceData]:
        """과거 가격 데이터 조회 (캐시 포함)"""
        cache_key = f"{symbol}_{interval}_{start_date}_{end_date}"
        
        # 캐시 확인
        if cache_key in self.cache:
            cached_data, cached_time = self.cache[cache_key]
            if datetime.now() - cached_time < timedelta(hours=1):  # 1시간 캐시
                logger.info(f"Using cached data for {cache_key}")
                return cached_data
        
        # API에서 데이터 조회
        try:
            # 큰 데이터셋은 청크로 나누어 조회
            all_data = []
            start_time = datetime.strptime(start_date, "%Y-%m-%d")
            end_time = datetime.strptime(end_date, "%Y-%m-%d") if end_date else datetime.now()
            
            current_time = start_time
            while current_time < end_time:
                # 한 번에 최대 1000개 캔들 조회 (Binance 제한)
                chunk_end = min(current_time + timedelta(days=1000), end_time)
                
                chunk_data = await self.binance_manager.get_historical_klines(
                    symbol=symbol,
                    interval=interval,
                    start_time=current_time.strftime("%Y-%m-%d"),
                    end_time=chunk_end.strftime("%Y-%m-%d"),
                    limit=1000
                )
                
                all_data.extend(chunk_data)
                current_time = chunk_end + timedelta(days=1)
                
                # API 제한을 위한 짧은 대기
                await asyncio.sleep(0.1)
            
            # 중복 제거 및 정렬
            unique_data = {}
            for data in all_data:
                key = data.date.isoformat()
                if key not in unique_data:
                    unique_data[key] = data
            
            sorted_data = sorted(unique_data.values(), key=lambda x: x.date)
            
            # 캐시 저장
            self.cache[cache_key] = (sorted_data, datetime.now())
            
            logger.info(f"Retrieved {len(sorted_data)} data points for {symbol}")
            return sorted_data
            
        except Exception as e:
            logger.error(f"Error retrieving historical data: {e}")
            raise
    
    def save_to_csv(self, data: List[PriceData], filename: str):
        """CSV 파일로 저장"""
        df_data = []
        for item in data:
            df_data.append({
                'date': item.date,
                'symbol': item.symbol,
                'open': item.open,
                'high': item.high,
                'low': item.low,
                'close': item.close,
                'volume': item.volume
            })
        
        df = pd.DataFrame(df_data)
        df.to_csv(f"data/historical/{filename}.csv", index=False)
        logger.info(f"Data saved to {filename}.csv")
    
    def load_from_csv(self, filename: str) -> List[PriceData]:
        """CSV 파일에서 로드"""
        try:
            df = pd.read_csv(f"data/historical/{filename}.csv")
            data = []
            
            for _, row in df.iterrows():
                data.append(PriceData(
                    symbol=row['symbol'],
                    date=pd.to_datetime(row['date']),
                    open=float(row['open']),
                    high=float(row['high']),
                    low=float(row['low']),
                    close=float(row['close']),
                    volume=float(row['volume'])
                ))
            
            logger.info(f"Loaded {len(data)} data points from {filename}.csv")
            return data
            
        except FileNotFoundError:
            logger.warning(f"File {filename}.csv not found")
            return []

class PaperTradingEngine:
    """가상매매 엔진"""
    
    def __init__(self, initial_balance: float = 10000.0):
        self.initial_balance = initial_balance
        self.balance = initial_balance
        self.positions = {}
        self.trade_history = []
        self.orders = []
        
    async def place_order(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """가상 주문 실행"""
        # 실제 가격으로 주문 체결 시뮬레이션
        current_price = order_data.get('price', 0.0)
        quantity = order_data['quantity']
        side = order_data['side']
        symbol = order_data['symbol']
        
        order_value = current_price * quantity
        
        if side == 'BUY':
            if self.balance >= order_value:
                self.balance -= order_value
                if symbol in self.positions:
                    self.positions[symbol] += quantity
                else:
                    self.positions[symbol] = quantity
            else:
                raise ValueError("Insufficient balance")
        
        elif side == 'SELL':
            if symbol in self.positions and self.positions[symbol] >= quantity:
                self.balance += order_value
                self.positions[symbol] -= quantity
                if self.positions[symbol] == 0:
                    del self.positions[symbol]
            else:
                raise ValueError("Insufficient position")
        
        # 주문 기록
        order_result = {
            'symbol': symbol,
            'side': side,
            'quantity': quantity,
            'price': current_price,
            'value': order_value,
            'timestamp': datetime.now(),
            'status': 'FILLED'
        }
        
        self.orders.append(order_result)
        logger.info(f"Paper trade executed: {order_result}")
        
        return order_result
    
    def get_portfolio_value(self, current_prices: Dict[str, float]) -> float:
        """포트폴리오 총 가치 계산"""
        total_value = self.balance
        
        for symbol, quantity in self.positions.items():
            if symbol in current_prices:
                total_value += quantity * current_prices[symbol]
        
        return total_value
    
    def get_account_summary(self) -> Dict[str, Any]:
        """계좌 요약 정보"""
        return {
            'initial_balance': self.initial_balance,
            'current_balance': self.balance,
            'positions': self.positions.copy(),
            'total_trades': len(self.orders),
            'pnl': self.balance - self.initial_balance
        }

if __name__ == "__main__":
    # 테스트 코드
    import asyncio
    
    async def test_binance_manager():
        # Paper trading 모드로 테스트
        manager = BinanceManager(mode="paper")
        
        try:
            # 현재 가격 조회 테스트
            price = await manager.get_current_price("BTCUSDT")
            print(f"Current BTC price: ${price:,.2f}")
            
            # 과거 데이터 조회 테스트
            historical_data = await manager.get_historical_klines(
                symbol="BTCUSDT",
                interval="1d",
                start_time="2024-01-01",
                end_time="2024-01-31",
                limit=31
            )
            print(f"Retrieved {len(historical_data)} historical data points")
            
            # 가상 주문 테스트
            order_result = await manager.place_order({
                'symbol': 'BTCUSDT',
                'side': 'BUY',
                'quantity': '0.001'
            })
            print(f"Order result: {order_result}")
            
        except Exception as e:
            print(f"Test failed: {e}")
    
    # asyncio.run(test_binance_manager())
from enum import Enum


        

class OrderStatus(Enum):
    CREATED = 0
    SENT = 1
    PARTIAL_FILLED = 2
    FULL_FILLED = 3
    CANCELLED = 4
    DELETED = 5

class OrderSide(Enum):
    BUY = 0
    SELL = 1
    
class ExchangeName(Enum):
    BYBIT = 0
    
class OrderType(Enum):
    LIMIT = 0
    MARKET = 1
    
class OrderCategory(Enum):
    SPOT = 0
    PERPETUAL = 1
    FUTURE = 2
    OPTION = 3
    
exchange_mappings = {
    ExchangeName.BYBIT:{
        OrderType.LIMIT:"Limit",
        OrderType.MARKET:"Market",
        OrderSide.BUY:"Buy",
        OrderSide.SELL:"Sell",
        OrderCategory.SPOT:"spot"
    },
    
}
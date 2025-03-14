import time
from utils import hash_id
from enums import *


class Order(object):
    def __init__(self, price:float, side:OrderSide, usdt_qty:float, exchange:ExchangeName, type:OrderType, instrument:str, category:OrderCategory, is_leverage:bool):
        self.__price = price
        self.__usdt_qty = usdt_qty
        self.__exchange = exchange
        self.__type = type
        self.__order_id = self.__set_order_link_id()
        self.__side = side
        self.__instrument = instrument
        self.__status = OrderStatus.CREATED
        self.__category = category
        self.create_time = time.time() * 1000
        self.is_leverage = is_leverage
    
    def __set_order_link_id(self):
        return hash_id()
    
    def update_status(self, status:OrderStatus):
        self.__status = status        
    
    @property
    def instrument(self):
        return self.__instrument
    
    @property
    def price(self):
        return self.__price
    
    @property
    def exchange(self):
        return self.__exchange
    
    @property
    def usdt_qty(self):
        return self.__usdt_qty
    
    @property
    def type(self):
        return exchange_mappings[self.exchange][self.__type]
    
    @property
    def order_id(self):
        return self.__order_id
    
    @property
    def side(self):
        return exchange_mappings[self.exchange][self.__side]
    
    @property
    def spot_qty(self):
        return self.usdt_qty / self.price
    
    @property
    def status(self):
        return self.__status
    
    @property
    def category(self):
        return exchange_mappings[self.exchange][self.__category]
    
    
class OrderResponse(object):
    def __init__(self):
        self.is_success = None
    
    def parser(self, response):
        self.is_success = response['retMsg']
        result = response['result']
        
        self.__order_id = result['orderId']
        self.__time = response['time']
        
    @property
    def order_id(self):
        return self.__order_id
    
    @property
    def order_time(self):
        return self.__time
    
        
from pybit.unified_trading import HTTP
from enums import *

class SessionManager(object):
    def __init__(self):
        self.session_dict = {}
        
    def add_session(self, exchange:ExchangeName, session):
        self.session_dict[exchange] = session
        
    def send_bybit_order(self, category:str, instrument:str, side:str, type:str, spot_qty:float, price:float, is_leverage:bool):
        
        if is_leverage:
            leverage_sign = 1
        else:
            leverage_sign = 0
        
        order_response = self.session_dict[ExchangeName.BYBIT].place_order(
                category=category,
                symbol=instrument,
                side=side,
                orderType=type,
                marketUnit="baseCoin",
                qty=spot_qty,
                price=price,
                isLeverage=leverage_sign,
                )
        return order_response 
    
    def check_bybit_pending_order(self, order_id, category, instrument):
        response = self.session_dict[ExchangeName.BYBIT].get_open_orders(
            category=category,
            symbol=instrument,
            orderLinkId=order_id,
            
        )
        print(response)
        
         
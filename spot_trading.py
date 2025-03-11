from pybit.unified_trading import HTTP
import json
import math
from orders import Order, OrderResponse
from utils import floor




class SpotTradeManager(object):
    
    
    def __init__(self, session:HTTP):
        with open("min_amount.json") as file:
            trading_rules_table = json.load(file)
        self.trading_rule_table = trading_rules_table
        self.session = session
    
    def get_current_index_close_minute(self, trading_pair):
        
        '''
        can be transformed to agent
        '''
        
        response = self.session.get_index_price_kline(
            symbol=trading_pair,
            interval=1
        )
        return float(response["result"]["list"][0][-1])
    
    def get_price_limit(self, trading_pair):
        # under/above index 1%
        ticksize = self.trading_rule_table[trading_pair]["ticksize"]
        index_price = self.get_current_index_close_minute(trading_pair)
        
        return round(index_price * 1.005,ticksize), round(index_price * 0.995,ticksize)
        
        
    

    
    def check_pending_orders(self, order:Order):
        response = self.session.get_open_orders(
            category=order.category,
            symbol=order.instrument,
            orderId=order.order_id,
            
        )
        status = response["result"]["list"][0]["orderStatus"]
        leaves_qty = response["result"]["list"][0]["leavesQty"]
        
        return status, leaves_qty
    
    def send_order(self, order:Order, is_leverage=False):
        
        if is_leverage:
            leverage_sign = 1
        else:
            leverage_sign = 0
        
        
        order_response = self.session.place_order(
                category=order.category,
                symbol=order.instrument,
                side=order.side,
                orderType=order.type,
                marketUnit="baseCoin",
                qty=order.spot_qty,
                price=order.price,
                isLeverage=leverage_sign,
                )
        return order_response
    
    def place_low_frequency_buy_order(self, trading_pair, usdt_qty, target_price):
        '''
        usdt_qty: in USDT amount
        
        logic:
        place limit order for current price
        
        if not fully filled, place 1.005 * current price
        repeat 2 times and if not filled, cancel remaining orders
        
        '''
        
        # can use a dataclass to wrap here
        
        
        
        price_limit_high, price_limit_low = self.get_price_limit(trading_pair)
        price = min(target_price, price_limit_high)
        
        board_lot = self.trading_rule_table[trading_pair]["board_lot"]
        ticksize = self.trading_rule_table[trading_pair]["ticksize"]
        min_amount = self.trading_rule_table[trading_pair]["min_amount"]
        qty = max(round(usdt_qty/price,board_lot), min_amount) # need to upgrade, not to use min_amount
        order_response = self.send_order(trading_pair, qty, price, "Buy")
        order_id = order_response['result']['orderId']
        
        
        for i in range(2):
            # amend order in 2 times, if still not filled, cancel the order
                
            
            status, leaves_qty = self.check_pending_orders(order_id, trading_pair)
            
            if status == "Filled":
                # if filled, then exit the logic
                continue
            else:
                # if partially filled or not filled, then amend orders with new price and leaves qty
                price = round(min(1.005 * price, price_limit_high), ticksize) # 0.5% increase in price
                order_response = self.session.amend_order(
                    category="spot",
                    symbol=trading_pair,
                    orderId=order_id,
                    price=price
                )
        
        # if still not filled, cancel that order
        status, leaves_qty = self.check_pending_orders(order_id, trading_pair)
        if status == "Filled":
            return order_response
        else:
            order_response = self.session.cancel_order(
                category="spot",
                symbol=trading_pair,
                orderId=order_id
            )
            return order_response
            
    
    def place_low_frequency_sell_order(self, trading_pair, usdt_qty, target_price):
        '''
        NOT USED FOR SPOT MODE, WILL BE APPLIED FOR MARGIN TRADING
        
        usdt_qty: in USDT amount
        
        logic:
        place limit order for current price
        
        if not fully filled, place 0.995 * current price
        repeat 3 times and if not filled, cancel remaining orders
        
        '''
        
        # can use a dataclass to wrap here
        price_limit_high, price_limit_low = self.get_price_limit(trading_pair)
        price = max(target_price, price_limit_low)
        
        board_lot = self.trading_rule_table[trading_pair]["board_lot"]
        ticksize = self.trading_rule_table[trading_pair]["ticksize"]
        min_amount = self.trading_rule_table[trading_pair]["min_amount"]
        qty = max(round(usdt_qty/price,board_lot), min_amount) # need to upgrade, not to use min_amount
        order_response = self.send_order(trading_pair, qty, price, "Sell")
        order_id = order_response['result']['orderId']
        
        
        for i in range(2):
            # amend order in 2 times, if still not filled, cancel the order
                
            
            status, leaves_qty = self.check_pending_orders(order_id, trading_pair)
            
            if status == "Filled":
                # if filled, then exit the logic
                continue
            else:
                # if partially filled or not filled, then amend orders with new price and leaves qty
                price = round(max(0.995 * price,price_limit_low), ticksize) # 0.5% increase in price
                order_response = self.session.amend_order(
                    category="spot",
                    symbol=trading_pair,
                    orderId=order_id,
                    price=price
                )
        
        # if still not filled, cancel that order
        status, leaves_qty = self.check_pending_orders(order_id, trading_pair)
        if status == "Filled":
            return order_response
        else:
            response = self.session.cancel_order(
                category="spot",
                symbol=trading_pair,
                orderId=order_id
            )
            return order_response
        
        
    def close_position(self, trading_pair, target_qty):
        board_lot = self.trading_rule_table[trading_pair]["board_lot"]
        min_qty = self.trading_rule_table[trading_pair]['min_amount']
        qty = max(floor(target_qty,board_lot),min_qty)
        
        response = self.session.place_order(
            category="spot",
            symbol=trading_pair,
            qty=qty,
            side="Sell",
            orderType="Market",
            marketUnit="baseCoin"
        )
        
        return response
        
        
if __name__ == "__main__":
    with open("keys.json") as file:
        apis = json.load(file)

    with open("min_amount.json") as file:
        trading_rules_table = json.load(file)
    
    session = HTTP(
        testnet=False,
        api_key=apis['API_KEY'],
        api_secret=apis['API_SECRET']
    )
        
    test_order = Order(80000, side="Buy", usdt_qty=10, exchange="Bybit", type="Limit", instrument="BTCUSDT", category="spot")
    response = OrderResponse
    print(test_order.create_time)
    manager = SpotTradeManager(session)
    response = OrderResponse()
    response.parser(manager.send_order(test_order))
    print(response.order_time - test_order.create_time)
from pybit.unified_trading import HTTP
from spot_trading import SpotTradeManager
from spot_strategies import NaiveCTAStartegy, Strategy
import json
from abc import abstractmethod
import time
import logging

LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
logging.basicConfig(filename='trading_log.txt', level=logging.INFO, format=LOG_FORMAT)

class NaiveCTAAgent(object):
    
    def __init__(self, session:HTTP, init_quota, heart_beat=60):
        self.session = session
        self.balance = {}
        self.heart_beat = heart_beat
        self.init_quota = init_quota
        
        with open("trading_pairs.json") as file:
            self.trading_pairs = json.load(file)

        
    def get_klines(self, trading_pair):
        data = self.session.get_kline(
            category="spot",
            symbol=trading_pair,
            interval=1
        )
        
        return data['result']['list'][:30]
    
    def get_current_index_close_minute(self, trading_pair):
        response = self.session.get_index_price_kline(
            symbol=trading_pair,
            interval=1
        )
        return float(response["result"]["list"][0][-1])
    
    def get_balance(self, coin_name="USDT"):
        response = self.session.get_coins_balance(accountType="UNIFIED",coin=coin_name)
        
        return float(response["result"]["balance"][0]["transferBalance"])
    
    def set_all_balance_target_pairs(self):
        for pairs in self.trading_pairs:
            base_coin_balance = self.get_balance(pairs['base_coin'])
            quote_coin_balance = self.get_balance() # right now only quote coin is USDT
            trading_pairs = pairs['trading_pair']
            
            self.balance[trading_pairs] = {"base_coin_qty":base_coin_balance,"base_coin_amt":base_coin_balance * self.get_current_index_close_minute(trading_pairs)} # only quote coin is USDT, need modification in the future for supporting USDC/ETH etc. 
    
    def initalize_strategies(self):
        
        '''
        init quota is 100 for every pairs now
        '''
        self.set_all_balance_target_pairs()
        self.trading_pool = [x['trading_pair'] for x in self.trading_pairs]
        self.strategy_pool = [NaiveCTAStartegy(self.init_quota, x) for x in self.trading_pool]
        
    def rebalancing_quota(self):
        self.set_all_balance_target_pairs()
        for strategy in self.strategy_pool:
            remaining_quota = max(0, self.init_quota- self.balance[strategy.trading_pair]["base_coin_amt"])
            strategy.set_quota(remaining_quota)
            
            
    def run(self):
        self.initalize_strategies()
        spot_manager = SpotTradeManager(self.session)
        while True:
            try:
                self.rebalancing_quota()
                for strategy in self.strategy_pool:
                    kline = self.get_klines(strategy.trading_pair)
                    strategy.input(data=kline)
                    
                    output = strategy.output()
                    if output:
                        side = output["side"]
                        qty = output["qty"]
                        close_position_qty = self.balance[strategy.trading_pair]["base_coin_qty"]
                        target_price = output["target_price"]
                        
                        if (side=="Buy") and (qty!="all"):
                            response = spot_manager.place_low_frequency_buy_order(strategy.trading_pair, qty, target_price)
                        
                        elif (side=="Sell") and (qty=="all"):
                            response = spot_manager.close_position(strategy.trading_pair, close_position_qty)
                        
                        else:
                            response = "No trade"
                        logging.info(response)
                    
                    else:
                        pass
                    
                time.sleep(self.heart_beat)
                
            except Exception as e:
                logging.info(e)
                time.sleep(1)
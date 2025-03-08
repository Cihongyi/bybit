from pybit.unified_trading import HTTP
from spot_trading import SpotTradeManager
from abc import abstractmethod
import time

class Strategy(object):
    def __init__(self, quota:float):
        '''
        quota in USDT
        '''
        self.__quota = quota
    
    @property
    def quota(self):
        return self.__quota
    
    def set_quota(self, new_quota):
        self.__quota = new_quota
    
    @abstractmethod
    def input(self, **kwargs):
        ...
    
    @abstractmethod
    def output(self):
        ...


class NaiveCTAStartegy(Strategy):
    def __init__(self, quota, trading_pair):
        super().__init__(quota)
        self.trading_pair = trading_pair # only for labelling
        
        
    def input(self, **kwargs):
        self.data = kwargs['data']
        
    def calculate_ma(self,lag=0):
        ma5 = sum([float(i[4]) for i in self.data[lag:5+lag]])/5
        ma30 = sum([float(i[4]) for i in self.data[lag:30+lag]])/30
        return ma5, ma30
    
    def output(self):
        ma5, ma30 = self.calculate_ma()
        ma5_t_1, ma30_t_1 = self.calculate_ma(lag=1)
        if (ma5 > ma30) and (ma5_t_1<=ma30_t_1):
            # golden cross, 1/5 of quota, target_price is ma5 * 1.2 (almost market order)
            return {"side":"Buy", "qty":self.quota, "target_price":ma5*1.2}
        
        elif (ma5 <= ma30) and (ma5_t_1>ma30_t_1):
            # death cross, close all position
            return {"side":'Sell', "qty":"all", "target_price":None}
        
        else:
            return None
        
    def __str__(self):
        return f"naive_cta_spot_{self.trading_pair}_quota_{round(self.quota,0)}"
    
    def __repr__(self):
        return self.__str__()
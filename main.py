from pybit.unified_trading import HTTP
from spot_trading import SpotTradeManager
from spot_strategies import NaiveCTAStartegy
from agent import NaiveCTAAgent
import time
import json

with open("keys.json") as file:
    apis = json.load(file)

with open("min_amount.json") as file:
    trading_rules_table = json.load(file)


session = HTTP(
    testnet=False,
    api_key=apis['API_KEY'],
    api_secret=apis['API_SECRET']
)


agent = NaiveCTAAgent(session,100,heart_beat=60)

agent.run()

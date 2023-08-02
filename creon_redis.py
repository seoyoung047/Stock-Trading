# 대신증권 계좌정보, 매매내역 자동 전송

# %load_ext autoreload
# %autoreload 

from dashin_api import Creon
from dashin_api import auth
import redis
import json

c = Creon.Creon()
c.connect(*auth.load())
# # 대신증권 ID jws02096     비밀번호: Z100315P    공인인증: Z100315h*!~ 

r = redis.Redis(host='34.64.37.236', port=6379, db=0)

i=0
while i < 10 :

    # 종목별 주문체결 내역
    for stock_n in range(len(c.get_holdings()['data'])):

        for stock_k in range(len(tuple(c.get_holdings()['data'][stock_n].keys()))):
            key = tuple(c.get_holdings()['data'][stock_n].keys())[stock_k]
            value=tuple(c.get_holdings()['data'][stock_n].values())[stock_k]
            # print(key,value)

            r.publish('{}'.format(key),'{}'.format(value))

    
    # 계좌 정보
    for stock_k in range(len(tuple(c.get_holdings()['header'].keys()))):

        key = tuple(c.get_holdings()['header'].keys())[stock_k]
        value=tuple(c.get_holdings()['header'].values())[stock_k]
        # print(key,value)

        r.publish('{}'.format(key),'{}'.format(value))
        

    # 금일 주문 발생 건별 주문체결 내역
    for stock_n in range(len(c.get_trade_history()['data'])):

        for stock_k in range(len(tuple(c.get_holdings()['data'][stock_n].keys()))):
            key = tuple(c.get_trade_history()['data'][stock_n].keys())[stock_k]
            value=tuple(c.get_trade_history()['data'][stock_n].values())[stock_k]
            # print(key,value)

            r.publish('{}'.format(key),'{}'.format(value))

    i+=1
    print(i)


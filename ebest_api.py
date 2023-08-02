# ebest api 활용

import json
import requests
from datetime import datetime


def make_token():

    APP_KEY = "PSLnfwwiJf5HaEEBvBmIIhPH4Z6P4QkchDN3"
    APP_SECRET = "9JCohD0eRXfKTvEhlqAvJct8vfRlamFC"

    header = {"content-type":"application/x-www-form-urlencoded"}
    param = {"grant_type":"client_credentials", "appkey":APP_KEY, "appsecretkey":APP_SECRET,"scope":"oob"}

    PATH = "oauth2/token"
    BASE_URL = "https://openapi.ebestsec.co.kr:8080"
    URL = f"{BASE_URL}/{PATH}"

    request = requests.post(URL, verify=False, headers=header, params=param)
    ACCESS_TOKEN = request.json()
    ACCESS_TOKEN = ACCESS_TOKEN['access_token']

    return ACCESS_TOKEN


# 주식현재가호가조회(t1101)
def chart_data(ACCESS_TOKEN,shcode):
    
    BASE_URL = "https://openapi.ebestsec.co.kr:8080"
    PATH = "stock/market-data"
    URL = f"{BASE_URL}/{PATH}"
    ACCESS_TOKEN = ACCESS_TOKEN

    header = {  
        "content-type":"application/json; charset=utf-8", 
        "authorization": f"Bearer {ACCESS_TOKEN}",
        "tr_cd":"t1101", 
        "tr_cont":"N",
        "tr_cont_key":"",
    }

    body = {
        "t1101InBlock" : 
        {    
            "shcode" : "{}".format(shcode),    
        }
    }
    requset = requests.post(URL, headers=header, data=json.dumps(body))
    t1101 = requset.json()['t1101OutBlock']
    dtime = datetime.strftime(datetime.now(),'%Y-%m-%d %H:%M') + ':00'
    
    return dtime, t1101['open'],t1101['high'],t1101['low'],t1101['price'],t1101['volume']



# 현물계좌 주문체결내역 조회(API) (CSPAQ13700)
def trade_order(ACCESS_TOKEN):

    ACCESS_TOKEN=ACCESS_TOKEN

    BASE_URL = "https://openapi.ebestsec.co.kr:8080"
    PATH = "stock/accno"
    URL = f"{BASE_URL}/{PATH}"

    header = {  
        "content-type":"application/json; charset=utf-8", 
        "authorization": f"Bearer {ACCESS_TOKEN}",
        "tr_cd":"CSPAQ13700", 
        "tr_cont":"N",
        "tr_cont_key":"",
    }
    body = {
        "CSPAQ13700OutBlock3" : 
        {    
            "AcntNo" : "",    
        }
    }

    requset = requests.post(URL, headers=header, data=json.dumps(body))
    r = requset.json()

    '''
    {'OrdDt': '20230727',         # 주문일
    'OrdNo': 5073,                # 주문번호
    'IsuNm': '신세계',          # 종목명
    'OrdPtnNm': '(KSE)현금매도',#주문유형명
    'OrdPrc': '189800.00',      # 주문가
    'ExecQty': 2,               # 체결수량
    'ExecPrc': '190250.00',     # 체결가
    'LastExecTime': '09:58:36', # 최종 체결처리시각
    'OrdTime': '09:58:30',      # 주문시간

    '''
    return r['CSPAQ13700OutBlock3']

# 현물주문(CSPAT00601)
def order(ACCESS_TOKEN,shcode, order, ordqty):

    if order == 'sell':
        # 1:매도
        bnstpcode = 1

    if order == 'buy':
        # 2:매수
        bnstpcode = 2

    BASE_URL = "https://openapi.ebestsec.co.kr:8080"
    PATH = "stock/order"
    URL = f"{BASE_URL}/{PATH}"
    ACCESS_TOKEN = ACCESS_TOKEN

    header = {  
        "content-type":"application/json; charset=utf-8", 
        "authorization": f"Bearer {ACCESS_TOKEN}",
        "tr_cd":"CSPAT00601", 
        "tr_cont":"N",
        "tr_cont_key":"",
    }
    body = {
    "CSPAT00601InBlock1": {

        "RecCnt": 1,
        "IsuNo": "{}".format(shcode),
        "OrdQty": ordqty,
        "OrdPrc": 0,
        "BnsTpCode": "{}".format(bnstpcode),     
        "OrdprcPtnCode": "03",
        "PrgmOrdprcPtnCode": "00",
        "StslAbleYn": "0",
        "StslOrdprcTpCode": "0",
        "CommdaCode": "41",
        "MgntrnCode": "000",
        "LoanDt": "",
        "MbrNo": "000",
        "OrdCndiTpCode": "0",
        "StrtgCode": " ",
        "GrpId": " ",
        "OrdSeqNo": 0,
        "PtflNo": 0,
        "BskNo": 0,
        "TrchNo": 0,
        "ItemNo": 0,
        "OpDrtnNo": "0",
        "LpYn": "0",
        "CvrgTpCode": "0"
    }
    } 

    requset = requests.post(URL, headers=header, data=json.dumps(body))
    r = requset.json()
    return r['rsp_msg']

# 현물 계좌 잔고(CSPAQ12300)
def acc_info(ACCESS_TOKEN):

    BASE_URL = "https://openapi.ebestsec.co.kr:8080"
    PATH = "stock/accno"
    URL = f"{BASE_URL}/{PATH}"
    ACCESS_TOKEN = ACCESS_TOKEN

        
    header = {  
        "content-type":"application/json; charset=utf-8", 
        "authorization": f"Bearer {ACCESS_TOKEN}",
        "tr_cd":"CSPAQ12300", 
        "tr_cont":"N",
        "tr_cont_key":"",
    }
    body = {
    "CSPAQ12300InBlock1": {
        "RecCnt" : 1, 
        "BalCreTp" : "0",         # 잔고생성구분
        "CmsnAppTpCode" : "0",    # 수수료적용구분
        "D2balBaseQryTp" : "0",   # 잔고기준 조회구분
        "UprcTpCode" : "0"        # 단가구분

    }
    } 

    requset = requests.post(URL, headers=header, data=json.dumps(body))
    r = requset.json()

    '''
    {
    'BalEvalAmt': 0,               잔고평가금액,  
    'PnlRat': '0.000000',          손익률, 
    'InvstPlAmt': 0,               투자손익금액, 
    'Dps': 500000000,              예수금, 
    'D1Dps': 500000000,            D1예수금, 
    'D2Dps': 500000000,            D2예수금, 
    }
    '''
    
    return r['CSPAQ12300OutBlock2']

# 현물 계좌 잔고(CSPAQ12200)
def acc_info2(ACCESS_TOKEN):

    BASE_URL = "https://openapi.ebestsec.co.kr:8080"
    PATH = "stock/accno"
    URL = f"{BASE_URL}/{PATH}"
    ACCESS_TOKEN = ACCESS_TOKEN

        
    header = {  
        "content-type":"application/json; charset=utf-8", 
        "authorization": f"Bearer {ACCESS_TOKEN}",
        "tr_cd":"CSPAQ12200", 
        "tr_cont":"N",
        "tr_cont_key":"",
    }

    body = {  
        "CSPAQ12200InBlock1" : {    
            "RecCnt" : 1,    
            "MgmtBrnNo" : "1",    
            "BalCreTp" : "1"
 }
} 

    requset = requests.post(URL, headers=header, data=json.dumps(body))
    r = requset.json()

    return r












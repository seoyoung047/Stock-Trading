#insert today trade
# 금일 주문 발생 건별 주문체결 내역

import pandas as pd
from datetime import datetime
import pymysql
import time
import ebest_api as eba
import redis
import urllib3
from urllib3.exceptions import InsecureRequestWarning
urllib3.disable_warnings(InsecureRequestWarning)

ACCESS_TOKEN = eba.make_token()

now_date=datetime.now()
now_date_format=now_date.strftime("%Y-%m-%d %H:%M:%S")
date = pd.to_datetime(now_date_format)

# DB연결

conn = pymysql.connect(host='', user='', password='', db='shin_db')
cur = conn.cursor()

r = redis.Redis(host='', port=, db=0)   


####################################### 거래내역 ###################################################

selecthis_sql = "SELECT orderdateordernum FROM Event_Trade Order By orderdateordernum DESC"
cur.execute(selecthis_sql)
hisresult = cur.fetchall()

trade = eba.trade_order(ACCESS_TOKEN)

# 거래내역 유무 확인
if 'CSPAQ13700OutBlock3' in trade.keys(): 
    trade = trade['CSPAQ13700OutBlock3']

    if len(trade) > 0 :
        dtime = datetime.strftime(datetime.strptime(trade[0]['OrdDt'], '%Y%m%d'),'%Y-%m-%d')

        # 최신 거래내역 유무 확인
        print(hisresult[0][0])
        if  hisresult[0][0] != dtime+' '+trade[0]['OrdTime']+'-'+str(trade[0]['OrdNo']):
        
            # 최신 거래내역 DB 추가
            for i in range(len(trade)-1,0,-1):
                
                tradelist=[]
                tradelist.append(dtime+' '+trade[i]['OrdTime']+'-'+str(trade[i]['OrdNo']))     # 주문시간+주문번호
                tradelist.append(dtime+' '+trade[i]['OrdTime'])                                # 주문시간
                tradelist.append(dtime+' '+trade[i]['LastExecTime'])                           # 체결시간
                tradelist.append(trade[i]['OrdNo'])                                            # 주문번호
                tradelist.append(trade[i]['IsuNm'])                                            # 종목명 
                tradelist.append(trade[i]['OrdPrc'])                                           # 주문가
                tradelist.append(trade[i]['ExecPrc'])                                          # 체결가
                tradelist.append(trade[i]['ExecQty'])                                          # 체결수량
                tradelist.append(trade[i]['OrdPtnNm'])                                         # 주문유형
                inputa_sql = "INSERT IGNORE INTO Event_Trade VALUES {};".format(tuple(tradelist))

                cur.execute(inputa_sql)
            # 실행 mysql 서버에 확정 반영하기
            conn.commit()
            print('Insert Event_Trade',now_date.strftime('%H:%M'))

            
        ################################### 실시간 1분에 한번 redis 전송 #############################################

        # 금일 주문 발생 건별 주문체결 내역
        # trade2 = eba.trade_order(ACCESS_TOKEN)['CSPAQ13700OutBlock3']

        dtime = datetime.strftime(datetime.strptime(trade[0]['OrdDt'], '%Y%m%d'),'%Y-%m-%d')

        r.publish('ordertime',dtime+' '+trade[0]['OrdTime'])        # 주문시간
        r.publish('excepttime',dtime+' '+trade[0]['LastExecTime'])  # 체결시간
        r.publish('ordernum',trade[0]['OrdNo'])                     # 주문번호
        r.publish('stockname',trade[0]['IsuNm'])                    # 종목명
        r.publish('orderprice',trade[0]['OrdPrc'])                  # 주문가
        r.publish('exceptprice',trade[0]['ExecPrc'])                # 체결가
        r.publish('exceptqty',trade[0]['ExecQty'])                  # 체결수량
        r.publish('gubun',trade[0]['OrdPtnNm'])                     # 주문유형

    else :
        print('거래가 없습니다.')

    ## 거래내역 발생시 조건문 종료 ##

else :
    print('Null CSPAQ13700OutBlock3')


###################################### 계좌정보 #########################################  

selectacc_sql = "SELECT rindex FROM Acc_Info ORDER BY rindex DESC limit 1;"
cur.execute(selectacc_sql)
resultacc = cur.fetchall()

accinfo = eba.acc_info(ACCESS_TOKEN)

if 'CSPAQ12300OutBlock2' in accinfo.keys():

    accinfo=accinfo['CSPAQ12300OutBlock2']
    
    if len(accinfo) > 0 :
        acclist=[]

        # DB내 계좌 내역 없을 시 rindex 1부터 시작작
        if len(resultacc) == 0:
            acclist.append(1)
        else:
            acclist.append(resultacc[0][0]+1)   
            
        acclist.append(accinfo['BalEvalAmt'])   # 잔고평가금액
        acclist.append(accinfo['InvstPlAmt'])   # 투자손익금액
        acclist.append(accinfo['Dps'])          # 예수금
        acclist.append(accinfo['D1Dps'])        # D+1 예수금
        acclist.append(accinfo['D2Dps'])        # D+2 예수금
        pltrat = float(accinfo['PnlRat']) * 100
        acclist.append(pltrat)       # 손익률

        inputb_sql = "INSERT INTO Acc_Info VALUES {};".format(tuple(acclist))
        cur.execute(inputb_sql)

    # 실행 mysql 서버에 확정 반영하기
    conn.commit()
    print('Acc_Info Insert', now_date.strftime('%H:%M'))

    
################################### 실시간 1분에 한번 redis 전송 #############################################
    
    r.publish('balanceevaluationamount',accinfo['BalEvalAmt'])   # 잔고평가금액
    r.publish('investmentincome',accinfo['InvstPlAmt'])          # 투자손익금액
    r.publish('jejus',accinfo['Dps'])                            # 예수금
    r.publish('d1jejus',accinfo['D1Dps'])                        # D+1 예수금
    r.publish('d2jejus',accinfo['D2Dps'])                        # D+2 예수금
    r.publish('profitrate',accinfo['PnlRat'])                    # 손익률

else :
    print('Null CSPAQ12300OutBlock2')

###################################### 종목별 손익률 #########################################  
selectacc_sql = "SELECT rindex FROM Stock_Profit ORDER BY rindex DESC limit 1;"
cur.execute(selectacc_sql)
resultacc = cur.fetchall()

accinfo2 = eba.acc_info2(ACCESS_TOKEN)

if 't0424OutBlock1' in accinfo2.keys():

    accinfo2 = accinfo2['t0424OutBlock1']
    
    if len(accinfo2) > 0 :
        acc2list=[]

        # DB내 계좌 내역 없을 시 rindex 1부터 시작작
        if len(resultacc) == 0:
            acc2list.append(1)
        else:
            acc2list.append(resultacc[0][0]+1)   
            
        acc2list.append(now_date_format)          # 날짜
        acc2list.append(accinfo2[0]['sunikrt'])   # 신세계 손익률
        acc2list.append(accinfo2[1]['sunikrt'])   # 신세계푸드 손익률
        acc2list.append(accinfo2[2]['sunikrt'])   # 이마트 손익률

        inputb_sql = "INSERT INTO Stock_Profit VALUES {};".format(tuple(acc2list))
        cur.execute(inputb_sql)

    # 실행 mysql 서버에 확정 반영하기
    conn.commit()
    print('Acc_Info2 Insert', now_date.strftime('%H:%M'))

    
################################### 실시간 1분에 한번 redis 전송 #############################################

    r.publish('datetime',now_date_format)                   # 날짜
    r.publish('shinprofit',accinfo2[0]['sunikrt'])              # 신세계 손익률
    r.publish('foodprofit',accinfo2[1]['sunikrt'])               # 신세계푸드 손익률
    r.publish('emartprofit',accinfo2[2]['sunikrt'])             # 이마트 손익률

else :
    print('Null t0424OutBlock1')




time.sleep(1)

# DB 연결 닫기
conn.close()


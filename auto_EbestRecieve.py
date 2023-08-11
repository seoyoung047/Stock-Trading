# 실시간 데이터 수집 및 전송

from datetime import datetime
import time
import pymysql

import threading
import pandas as pd
import redis
import ebest_api as eba

# 수집 종목 코드
shcode_list = ['031440','034300','035510','004170','139480','000720','097950']

ACCESS_TOKEN = eba.make_token()

# 차트 데이터 불러오기, DB 전송
def recieve_dt(shcode):

    df = eba.chart_data(ACCESS_TOKEN,shcode)

    red.publish('Datetime_{}'.format(shcode),df[0])
    red.publish('price_{}'.format(shcode),df[4])

    # DB에 넣기
    input_sql = "INSERT INTO CHART_{} VALUES{};".format(shcode, tuple(df))
    # print(input_sql)

    cur.execute(input_sql)

    # # 실행 mysql 서버에 확정 반영하기
    conn.commit()
    

    
def multithreading_xing():
    
    threads=[]

    for shcode in shcode_list:
        t = threading.Thread(target=recieve_dt(shcode))
        t.start()
        threads.append(t)

    for thread in threads:
        thread.join()
        
      
i = 0
while True:

    now_date=datetime.now()
    now_date_format=now_date.strftime("%Y-%m-%d %H:%M:%S")
    date = pd.to_datetime(now_date_format)

    # DB연결(DBeaver 사용)
    conn = pymysql.connect(host='', user='', password='', db='shin_db')
    cur = conn.cursor()

    # Redis 연결
    red = redis.Redis(host='',port=6379,db=0)

    if date.second == 1:

        # 멀티스레드 실행
        multithreading_xing()
        print('Chart_ insert',datetime.now().strftime('%H:%M:%S'))
        
        i+=1
        time.sleep(1)
        
        # 테스트용
        # if i == 5:
        #     print('end')
        #     break

        
        # 매시 정각 마다 출력 
        if now_date.strftime('%M') == '00': 
            print('!정각 알람!',now_date.strftime('%H:%M'))


        # 15시20분 수집 종료
        if now_date.strftime('%H:%M') == '15:21':
            print('수집 종료 : ', now_date.strftime('%H:%M'))
            break
    
    # DB 연결 닫기
    conn.close()
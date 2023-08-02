import pandas as pd
import numpy as np
import time
from datetime import datetime

import os
import glob

import pymysql

from tqdm import tqdm
import scipy
import ta
import talib

import locale
locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

#신세계푸드 031440 / 신세계건설 034300 / 신세계 I&C 035510
# 광주신세계 037710 / (주식회사)신세계 004170 / (주식회사)이마트 139480 / 현대건설 000720 / CJ제일제당 097950
codes=['031440','034300','035510','004170','139480','000720','097950']

main_codes = ['031440','004170','139480']
sub_codes = list(set(codes) - set(main_codes))


# 종목 데이터 추가 컬럼 
def add_col(df):
    
    # 등락률 계산
    # 직전 종가 대비
    df["close yesterday"] = df["close"].shift(1)
    df['volume yesterday'] = df['volume'].shift(1)

    df["ratio_close"] = ((df["close"] - df["close yesterday"]) / df["close yesterday"])*100
    df["ratio_high_close"] = ((df["high"] - df["close yesterday"]) / df["close yesterday"])*100
    df["ratio_low_close"] = ((df["low"] - df["close yesterday"]) / df["close yesterday"])*100
    df["ratio_open_close"] = (df["open"] - df["close yesterday"]) / df["close yesterday"]*100


    # 9시1분 데이터 : 누적 거래량 유지
    if df['Datetime'][19] == datetime.strptime('09:01', '%H:%M'):
        df['volume'] = df['volume']

    else:
        df['volume'] = df['volume'] - df['volume yesterday']

    df['ratio_volume'] = ((df['volume']) / df['volume yesterday'])*100
    df['ratio_volume'].fillna(0, inplace=True)
    df['ratio_volume'] = df['ratio_volume'].replace([np.inf,-np.inf],0)
 
    # 이동평균선 (MA20)
    df['MA20'] = talib.SMA(df['close'], 20)
    df['ratio_MA20_close'] = (df['close'] / df['MA20']) *100

    df['ratio_MA20_volume'] = (df['volume'] / talib.SMA(df['volume'], 20)) *100
    df['ratio_MA20_volume'].fillna(0, inplace=True)
    df['ratio_MA20_volume'] = df['ratio_MA20_volume'].replace([np.inf,-np.inf],0)

    # 직전가 컬럼 추가하기
    last_price = df['close'].tolist()
    last_price.insert(0,0)
    last_price = last_price[:-1]

    df['last_price'] = last_price

    # 대비 부호 추가하기
    # 상승:1    보합:0   하락:-1 
    sign = [0]
    for i in range(1,len(df)):
            
        if df['last_price'][i] < df['close'][i]:
            sign.append(1)
        elif df['last_price'][i] == df['close'][i]:
            sign.append(0)
        elif df['last_price'][i] > df['close'][i]:
            sign.append(-1)

        i+=1
    df['sign'] = sign

    return df

# 코스피, 환율 데이터 추가 컬럼
def ma_add_col(df,colname):

    df["close yesterday"] = df[colname].shift(1)
    df["change"] = ((df[colname] - df["close yesterday"]) / df["close yesterday"])*100

    # 이동평균선 (MA20)
    df['MA20'] = talib.SMA(df[colname], 20)
    df['ratio_MA20_close'] = (df[colname] / df['MA20']) *100

    return df

# 환율, 코스피 가져오기

def select_kospi_ex():

    # DB연결
    conn = pymysql.connect(host='34.64.197.181', user='SUJIN', password='SUJIN', db='shin_db')
    cur = conn.cursor()

    # 환율 가져오기
    sql = "SELECT * FROM exchange_crawling ORDER BY ExchangeDate DESC limit 20;"
    cur.execute(sql)
    exchange_rate = pd.DataFrame(data=cur.fetchall()).T
    exchange_rate = exchange_rate.T
    exchange_rate.columns = ['Datetime','USD','CNY']


    exchange_rate['Datetime'] = exchange_rate['Datetime'].apply(lambda _: datetime.strptime(_[:-3],'%Y-%m-%d %H:%M'))
    exchange_rate.sort_values(by='Datetime', ascending=True, inplace=True)
    exchange_rate.reset_index(inplace=True,drop=True)

    # exchange_rate['USD'] = list(map(float,exchange_rate['USD'].apply(lambda _ : locale.atof(_))))
    # exchange_rate['CNY'] = list(map(float,exchange_rate['CNY'].apply(lambda _ : locale.atof(_))))

    exchang_USD = ma_add_col(exchange_rate[['Datetime','USD']],'USD')
    exchang_CNY = ma_add_col(exchange_rate[['Datetime','CNY']],'CNY')

    exchang_USD = exchang_USD[['Datetime','change','ratio_MA20_close']]
    exchang_USD.columns = [['Datetime','USD_change','USD_ratio_MA20_close']]
    exchang_CNY = exchang_CNY[['Datetime','change','ratio_MA20_close']]
    exchang_CNY.columns = [['Datetime','CNY_change','CNY_ratio_MA20_close']]

    #코스피 가져오기
    sql = "SELECT * FROM kospi_crawling ORDER BY KospiDate DESC limit 20;"
    cur.execute(sql)
    kospi = pd.DataFrame(data=cur.fetchall()).T
    kospi = kospi.T
    kospi.columns = ['Datetime','close']

    kospi['Datetime'].apply(lambda _: datetime.strptime(_[:-3],'%Y-%m-%d %H:%M'))
    kospi.sort_values(by='Datetime', ascending=True, inplace=True)
    kospi.reset_index(inplace=True,drop=True)
    # kospi['close'] = list(map(float,kospi['close'].apply(lambda _ : locale.atof(_))))

    kospi = ma_add_col(kospi,'close')
    kospi = kospi[['Datetime','change','ratio_MA20_close']]
    kospi.columns = [['Datetime','kospi_change','kospi_ratio_MA20_close']]

    conn.close()


    return kospi, exchang_USD, exchang_CNY


def add_col_exko(df):

    kospi, exchang_USD, exchang_CNY = select_kospi_ex()
    
    df[['kospi_change','kospi_ratio_MA20_close']] = kospi[['kospi_change','kospi_ratio_MA20_close']]
    df[['USD_change','USD_ratio_MA20_close']] = exchang_USD[['USD_change','USD_ratio_MA20_close']]
    df[['CNY_change','CNY_ratio_MA20_close']] = exchang_CNY[['CNY_change','CNY_ratio_MA20_close']]

    return df

def concat_df(df):
# 메인종목에 서브 종목 컬럼 추가
    for scode in sub_codes:
        df[globals()['add_{}'.format(scode)].columns] = globals()['add_{}'.format(scode)]
    
    # 메인종목 라벨 맨 뒤로
    label = []
    label = df['sign']
    df['label'] = label
    df.drop(columns='sign', inplace=True)
    df.reset_index(inplace=True, drop=True)

    df.columns = [
                    'Datetime','open','high','low','close','volume'

                    ,'ratio_close','ratio_high_close','ratio_low_close','ratio_open_close','ratio_volume','ratio_MA20_close','ratio_MA20_volume'

                    ,'kospi_change','kospi_ratio_MA20_close'

                    ,'USD_change','USD_ratio_MA20_close'

                    ,'CNY_change','CNY_ratio_MA20_close'

                    ,'D035510_sign','D035510_ratio_close','D035510_ratio_high_close','D035510_ratio_low_close','D035510_ratio_open_close','D035510_ratio_volume','D035510_ratio_MA20_close','D035510_ratio_MA20_volume'

                    ,'D000720_sign','D000720_ratio_close','D000720_ratio_high_close','D000720_ratio_low_close','D000720_ratio_open_close','D000720_ratio_volume','D000720_ratio_MA20_close','D000720_ratio_MA20_volume'

                    ,'D034300_sign','D034300_ratio_close','D034300_ratio_high_close','D034300_ratio_low_close','D034300_ratio_open_close','D034300_ratio_volume','D034300_ratio_MA20_close','D034300_ratio_MA20_volume'

                    ,'D097950_sign','D097950_ratio_close','D097950_ratio_high_close','D097950_ratio_low_close','D097950_ratio_open_close','D097950_ratio_volume','D097950_ratio_MA20_close','D097950_ratio_MA20_volume'

                    ,'label']
    
    return df



# 종목 차트 데이터 불러오기(select)
def select_data():

    for code in codes:
        # DB연결
        conn = pymysql.connect(host='', user='', password='', db='shin_db')
        cur = conn.cursor()

        sql = "SELECT * FROM CHART_{} ORDER BY Datetime DESC limit 20;".format(code)
        cur.execute(sql)
        result = cur.fetchall()

        if len(result) > 1 :

            # 불러온 데이터 넣기

            globals()['result_{}'.format(code)] = pd.DataFrame(data=result).T
            globals()['result_{}'.format(code)] = globals()['result_{}'.format(code)].T
            globals()['result_{}'.format(code)].columns = ['Datetime','open','high','low','close','volume']
            
            # Datetime 변경
            globals()['result_{}'.format(code)]['Datetime'] = globals()['result_{}'.format(code)]['Datetime'].apply(lambda _: datetime.strptime(_[:-3],'%Y-%m-%d %H:%M'))

            # DB 연결 닫기
            conn.close()


            # 지표 컬럼 추가하기
            globals()['result_{}'.format(code)].sort_values(by='Datetime', ascending=True, inplace=True)
            globals()['result_{}'.format(code)].reset_index(inplace=True,drop=True)
            globals()['add_{}'.format(code)] = add_col(globals()['result_{}'.format(code)])

            # 서브종목들 컬럼명 변경하기
            if code in sub_codes:
                col_list=['Datetime']
        
                for col in globals()['add_{}'.format(code)].columns[1:]:
                    
                    col_name = 'D' + code +'_'+ col
                    col_list.append(col_name)
                    
                
                globals()['add_{}'.format(code)].columns = col_list
                
                globals()['add_{}'.format(code)] = globals()['add_{}'.format(code)].iloc[:,[0,8,9,10,11,12,14,15,17]]
            
            # 메인 종목들 컬럼 추가 및 제거
            else:
                # 환율,코스피 추가
                globals()['add_{}'.format(code)] = add_col_exko(globals()['add_{}'.format(code)])
                # 직전가, 직전 종가, 거래량 제거
                globals()['add_{}'.format(code)] = globals()['add_{}'.format(code)].iloc[:,[0,1,2,3,4,5,8,9,10,11,12,14,15,17,18,19,20,21,22,23]]
                # # 앞 19개 제거
                globals()['add_{}'.format(code)] = globals()['add_{}'.format(code)].iloc[19:,:]

            # print(globals()['add_{}'.format(code)]['Datetime'][-1:],'데이터 불러오기 완료')

        else:
            print('데이터가 없거나 한 개 이하 입니다.')
            conn.close()
        
    for mcode in main_codes:
        
        globals()['add_{}'.format(mcode)] = concat_df(globals()['add_{}'.format(mcode)])

    return add_031440, add_004170, add_139480

import pandas as pd
import numpy as np

import pymysql
from transformers import AutoTokenizer,AutoModelForSequenceClassification,pipeline
import sentiment_model
import os
import re
import torch
import time
from tqdm import tqdm
import datetime
import threading

import Concat_Chart


def get_news(cur):

    emarts_sql='select * from (select * from eMart where NewsDate in(select max(NewsDate) from eMart) order by NewsDate desc)t group by t.NewsDate;'
    shins_sql='select * from (select * from shin where NewsDate in(select max(NewsDate) from shin) order by NewsDate desc)t group by t.NewsDate;'
    foods_sql='select * from (select * from shinFood where NewsDate in(select max(NewsDate) from shinFood) order by NewsDate desc)t group by t.NewsDate;'

    cur.execute(emarts_sql)
    emarts = cur.fetchall()

    cur.execute(shins_sql)
    shins = cur.fetchall()

    cur.execute(foods_sql)
    foods = cur.fetchall()

    return emarts,shins,foods


def insert_new(stock_news,cur):

    token=sentiment_model.text_token()
    model=sentiment_model.Finbert_Model()

    news = pd.DataFrame(data=stock_news[0]).T
    news.columns = ['Dateitme','NewsTitle','doc']

    classifier=sentiment_model.model_pipeline(token,model)
    text=sentiment_model.text_proprecessing(news)
    sentiment_model.sentiment_predict(text,classifier)

    sentiment_res = text['sentiment'][0]

    vnames = [name for name in globals() if globals()[name] is stock_news]
    
    if vnames[0] == 'foods' :

        datas = Concat_Chart.select_data()
        data = datas[0]
        data['sentiment'] = sentiment_res
        input_sql = "INSERT INTO New_031440 VALUES {};".format(tuple(data.iloc[0,:]))
    

    if vnames[0] == 'shins':

        datas = Concat_Chart.select_data()
        data = datas[1]
        data['sentiment'] = sentiment_res
        input_sql = "INSERT INTO New_004170 VALUES {};".format(tuple(data.iloc[0,:]))
    
    
    if vnames[0] == 'emarts':

        datas = Concat_Chart.select_data()
        data = datas[2]
    
        data['sentiment'] = sentiment_res
        input_sql = "INSERT INTO New_139480 VALUES {};".format(tuple(data.iloc[0,:]))


    cur.execute(input_sql)

def multithreading_new(emarts,shins,foods,cur):
    
    threads=[]

    for nm in (emarts,shins,foods):
        t = threading.Thread(target=insert_new(nm,cur))
        t.start()
        threads.append(t)

    for thread in threads:
        thread.join()
    

while True:
    
    now_date=datetime.datetime.now()
    now_date_format=now_date.strftime("%Y-%m-%d %H:%M:%S")
    
    date = pd.to_datetime(now_date_format)
    
    # 15시 21분 종료
    if now_date.strftime('%H:%M') == '15:21':
        print('Insert 종료 : ',now_date_format)
        break
    
    # 9시 00분 시작
    if date.second == 2:

        conn = pymysql.connect(host='34.64.197.181', user='SUJIN', password='SUJIN', db='shin_db')
        cur = conn.cursor()

        emarts,shins,foods = get_news(cur)
        insert_new(emarts,cur)
        insert_new(shins,cur)
        insert_new(foods,cur)

        conn.commit()
        conn.close()

        print('New_ insert ',now_date_format)

    




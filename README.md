# Stock_Trading

# 주식 트레이딩 및 실매매

PDF 파일 : rainbow_company.pdf





####################### 과거 데이터 수집/전처리 ########################

- t8413_minutedata.ipynb : 이베스트 과거 데이터 수집
- 
- 21_22_concat.ipynb : 과거 종목 데이터 전처리(대신증권 / 틱->분봉)

- 22_23_concat.ipynb : 과거 종목 데이터 전처리(이베스트증권)

- concat_data.ipynb :  과거 2년치(21년 6월28일 ~ 23년 7월20일) 종목 데이터 합치기

- exchange_rate_concat.ipynb : 수집된 환율 데이터 파일 합치기 및 전처리(틱->분봉)

- kospi_concat.ipynb : 수집된 코스피 데이터 합치기 및 전처리

- add_col.ipynb : 지표 추가(종목, 코스피, 환율)

- main_concat.ipynb : 전체 데이터 합치기, 메인종목에 서브종목 추가

####################################################################

##################### 실시간 데이터 수집/전처리 #####################

- auto_EbestRecieve.py : 실시간 차트 수집 및 DB전송

- ebest_api.py :  이베스트 open api 사용 함수

- autosend.py : 실시간 수집 데이터 전처리 

  -> Concat_Chart.py : 차트 데이터 전처리

  -> sentiment_model.py : 뉴스 데이터 전처리

- insert_today_trade.py : 당일 매매내역, 계좌정보 DB전송 및 redis 전송

####################################################################

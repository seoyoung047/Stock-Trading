# Stock_Trading

# 주식 트레이딩 및 실매매

auto_EbestRecieve.py : 실시간 차트 수집 및 DB전송

  -> ebest_api.py :  이베스트 open api 사용 함수

autosend.py : 실시간 수집 데이터 전처리 

  -> Concat_Chart.py : 차트 데이터 전처리

  -> sentiment_model.py : 뉴스 데이터 전처리

insert_today_trade.py : 당일 매매내역, 계좌정보 DB전송 및 redis 전송

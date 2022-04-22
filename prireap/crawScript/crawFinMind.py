
import pandas as pd
import requests
from ..crawSrc.crawBase import BasicCraw
from FinMind.data import DataLoader
from dotenv import load_dotenv
from os import getenv
from time import sleep
from datetime import datetime, date, timedelta, time
from pytz import utc
import warnings
from urllib.parse import urljoin
import json

load_dotenv()


# url = "https://api.finmindtrade.com/api/v4/login"
# parload = {
#     "user_id": getenv('FM_USER_ID'),
#     "password": getenv('FM_PWD'),
# }
# data = requests.post(url, data=parload)
# data = data.json()
# print(data) #msg, status, token
# token=data['token']


# print(df)
# '''
# trading_volume: 成交股數
# Trading_money：成交金額
# Trading_turnover: 成交筆數, transaction
# '''

end_date = getenv('SCRIPT_END_DATE')
start_date = getenv('SCRIPT_START_DATE')
if end_date == None:
    end_date = datetime.utcnow().date()#-timedelta(days=1)
if start_date == None:
    start_date = date.fromisoformat('2000-01-01')

# it's possible already get some stocks, to skip them, indicate stock_li
stock_skip_li=['2330','0050']
stock_start_id=1038
timeout=60*1
API_HR_LIMIT=295

print("\nThe crawler will get data from {} to {}".format(
    start_date.isoformat(), end_date.isoformat()))
input("Press Enter to continue...\n")

craw = BasicCraw()
df_local_stocks = pd.DataFrame.from_dict(craw.list_exg_stocks())
req_counter=0
cycle_start_dt=datetime.now()
for idx, stock in enumerate(df_local_stocks.iterrows()):
    stock = stock[1]
    symbol = stock['symbol']
    stock_id= stock['id']
    print('symbol:',symbol, 'stock_id:', stock_id)
    
    if (symbol not in stock_skip_li) and stock_id>=stock_start_id:
        api = DataLoader()
        # api.login_by_token(api_token=token)
        # api.login(user_id='user_id',password='password')
        df = api.taiwan_stock_daily(
            stock_id=symbol,
            start_date=start_date,
            end_date=end_date,
            timeout=timeout
        )
        req_counter+=1
        
        if not df.shape[0]:
            warnings.warn("May be blocked by foreign server.", RuntimeWarning)

        #fastapi have bug on iso8601 datatime parsing
        df['date']=df['date']+'T'+time(hour=1, tzinfo=utc).isoformat()
        # print( df['date'][0] )
        # raise

        df['stock_id']=stock['id']
        df.rename(columns={'date': 'start_ts', 'max': 'high', 'min': 'low',
                'Trading_Volume': 'volume', 'Trading_turnover': 'transaction'}, inplace=True)
        df.drop(columns=['Trading_money'], inplace=True)

        # upload to local server
    
        # # multi req ver
        # for record in df.iterrows():
        #     '''
        #     非常耗時，batch update 比較好。怎麼detect duplicate?
        #     耗時的原因是io嗎? 網路卡io, 硬碟io? 還是處理request本身就慢？
        #     可以更改api接口內部實現去找到 e.g. 在backend 用for loop 去 if exist，如果變快，表示不是硬碟io的問題
        #     改成一次request，快很多，但是還是有改善空間
        #     '''
        #     record = record[1]
        #     body = {k: v for k, v in record.items() if v}
        #     # print(body)
        #     try:
        #         response = requests.post(
        #             urljoin(getenv('SERVER_URL'), 'kbars'), json=body)
        #         response.raise_for_status()
        #         # print('sucess to add new {} (stock_id:{}) kday to local server.'.format( stock['symbol'], stock['id']))
        #     except requests.exceptions.HTTPError as e:  # e.g. 400, 401, 404...
        #         print(e)
        #         print('symbol:{}, response text:{}'.format( symbol, response.text))
        #     except Exception as e:
        #         print(e)
        #     # raise

        # # sing req ver
        body=df.to_dict(orient="records")
        body = [{k: v for k, v in el.items() if v!=None} for el in body]
        # print(body)
        # raise
        try:
            print('upload to local...')
            response = requests.post(
                urljoin(getenv('SERVER_URL'), 'composite/kbars'), json=body, timeout=timeout)
            response.raise_for_status()
            # print('sucess to add new {} (stock_id:{}) kday to local server.'.format( stock['symbol'], stock['id']))
        except requests.exceptions.HTTPError as e:  # e.g. 400, 401, 404...
            print(e)
            data=response.text
            info = (data[:75] + '..') if len(data) > 75 else data
            print('symbol:{}, response text:{}'.format( symbol, info))
        except Exception as e:
            print(e)
    else:
        print('passed')
        


    # #同時執行兩個if 的coroutine
    # if (idx+1) % 300 == 0:
    #     time.sleep(60*60)  # sleep 1hr
    # # raise
    if req_counter+1>=API_HR_LIMIT:
        if datetime.now()-cycle_start_dt>=timedelta(hours=1):
            print('waiting for 300N/hr limit...')
        while datetime.now()-cycle_start_dt>=timedelta(hours=1):
            sleep(1)
        cycle_start_dt=datetime.now()
        req_counter=0


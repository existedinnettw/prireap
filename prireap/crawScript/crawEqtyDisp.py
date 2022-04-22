
from operator import ne
from xxlimited import new
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
import subprocess
import numpy as np

'''
最後執行日期4/4
'''

load_dotenv()

end_date = getenv('SCRIPT_END_DATE')
start_date = getenv('SCRIPT_START_DATE')
end_date = date(2022, 4, 22)
if end_date == None:
    end_date = datetime.utcnow().date()  # -timedelta(days=1)
if start_date == None:
    start_date = date.fromisoformat('2000-01-01')

# it's possible already get some stocks, to skip them, indicate stock_li
stock_skip_li = []  # ['2330','0050']
stock_start_id = 1  # 2 #489
timeout = 10
# API_HR_LIMIT = 300

print("\nThe crawler will get data from {} to {}".format(
    start_date.isoformat(), end_date.isoformat()))
# input("Press Enter to continue...\n")

craw = BasicCraw()
df_local_stocks = pd.DataFrame.from_dict(craw.list_exg_stocks())
df_local_stocks = df_local_stocks[df_local_stocks['id'] >= stock_start_id]
# req_counter = 0
cycle_start_dt = datetime.now()
for idx, stock in enumerate(df_local_stocks.iterrows()):
    stock = stock[1]
    symbol = stock['symbol']
    stock_id = stock['id']
    print('symbol:', symbol, 'stock_id:', stock_id)

    if (symbol not in stock_skip_li) and stock_id >= stock_start_id:
        api = DataLoader()
        # api.login_by_token(api_token=token)
        # api.login(user_id='user_id',password='password')
        # print(start_date.isoformat())
        try:
            df = api.taiwan_stock_holding_shares_per(
                stock_id=symbol,
                start_date=start_date.isoformat(),
                end_date=end_date.isoformat(),
                timeout=timeout
            )
        except Exception as e:
            msg = e.args[0]
            if "Requests reach the upper limit" in msg:
                print("block by server, redial...")
                subprocess.call([r'C:\Users\exist\Desktop\redial.bat'])
                sleep(10)
            else:
                raise Exception('unkown error')
        # req_counter += 1

        if not df.shape[0]:
            warnings.warn("May be blocked by server.", RuntimeWarning)
        if df.empty:
            print("no data, pass")
            continue

        # -->modify to suit for table column
        dates = df['date'].unique()
        map_HoldingSharesLevel={
            '1-999':'l1',
            '1,000-5,000':'l2',
            '5,001-10,000':'l3',
            '10,001-15,000':'l4',
            '15,001-20,000':'l5',
            '20,001-30,000':'l6',
            '30,001-40,000':'l7',
            '40,001-50,000':'l8',
            '50,001-100,000':'l9',
            '100,001-200,000':'l10',
            '200,001-400,000':'l11',
            '400,001-600,000':'l12',
            '600,001-800,000':'l13',
            '800,001-1,000,000':'l14',
            'more than 1,000,001':'l15',
            '差異數調整（說明4）':'diff',
            'total':None,
        }
        df['HoldingSharesLevel']=df['HoldingSharesLevel'].map(map_HoldingSharesLevel).drop(columns=['percent','stock_id'])
        df=df[~df['HoldingSharesLevel'].isnull()]
        # print(df)
        # raise
        new_df = pd.DataFrame(columns=[
            'l1_nper', 'l1_n', 'l2_nper', 'l2_n', 'l3_nper', 'l3_n',
            'l4_nper', 'l4_n', 'l5_nper', 'l5_n', 'l6_nper', 'l6_n', 'l7_nper', 'l7_n',
            'l8_nper', 'l8_n', 'l9_nper', 'l9_n', 'l10_nper', 'l10_n', 'l11_nper', 'l11_n',
            'l12_nper', 'l12_n', 'l13_nper', 'l13_n', 'l14_nper', 'l14_n', 'l15_nper', 'l15_n', 'diff_n'])
        new_df['date'] = dates
        new_df['diff_n']=0
        new_df=new_df.set_index('date')
        # print(new_df)
        # raise
        def fill_vals(row):
            global new_df
            # print(row)
            col=row['HoldingSharesLevel']
            if col!='diff':
                new_df.loc[row['date'],[col+'_nper',col+'_n']]=[row['people'],row['unit']]
            else:
                new_df.loc[row['date'],col+'_n']=row['unit']
        df.apply(fill_vals, axis=1) #like a for loop
        new_df=new_df.reset_index(drop=False)
        new_df['stock_id'] = stock_id
        # print(new_df)
        # print(np.any(new_df==None))
        # raise
        # --> create dict for create request.
        body = new_df.to_dict(orient="records")
        body = [{k: v for k, v in el.items() if v!=None} for el in body]
        # body = [body[0]]
        # print(body)
        # raise
        try:
            print('upload to local...')
            response = requests.post(
                urljoin(getenv('SERVER_URL'), 'composite/eqty_disp/'), json=body, timeout=timeout)
            response.raise_for_status()
            # print('sucess to add new {} (stock_id:{}) kday to local server.'.format( stock['symbol'], stock['id']))
        except requests.exceptions.HTTPError as e:  # e.g. 400, 401, 404...
            print(e)
            data = response.text
            # info = (data[:75] + '..') if len(data) > 75 else data
            print('symbol:{},\nresponse text:{}'.format(symbol, data))
            raise Exception('local server error, plz fix.')
        except Exception as e:
            print(e)
        # raise
        sleep(3)
    else:
        print('passed')

    # #同時執行兩個if 的coroutine
    # if (idx+1) % 300 == 0:
    #     time.sleep(60*60)  # sleep 1hr
    # # raise
    # if req_counter+1 >= API_HR_LIMIT:
    #     if datetime.now()-cycle_start_dt >= timedelta(hours=1):
    #         print('waiting for 300N/hr limit...')
    #     while datetime.now()-cycle_start_dt >= timedelta(hours=1):
    #         sleep(1)
    #     cycle_start_dt = datetime.now()
    #     req_counter = 0

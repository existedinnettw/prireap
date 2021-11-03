from .crawBase import CrawBase
import requests
import os
from dotenv import load_dotenv
from urllib.parse import urljoin
import time
from datetime import datetime, timedelta
import json
import abc
import yfinance as yf

load_dotenv()

class YfCraw(CrawBase):
    def __init__(self):
        super().__init__()
    
    def create_kmin_of_cur(self):
        super().create_kmin_of_cur()
        print("yahoo finance cann't give you useable kmin, so it isn't supported, return immediately...")
        # raise NotImplementedError
        return
    def create_khour_of_cur(self):
        '''
        the function is expect to called at the callback of each hour to request last hour kbar
        TODO: check marketing time?
        '''
        super().create_khour_of_cur()
        exg_id = self.tpe_exg['id']
        server_stock_list = self.list_exg_stocks(exg_id)
        cdt = datetime.now()
        
        while cdt.minute >= 58:
            '''
            避免基本的時間差，似乎不是很需要，因為是用timer call的，所以local時間不會有error
            '''
            time.sleep(1e-2)  # sleep to make sure can query hourly data
            cdt = datetime.now()
        cdt_hr = self._hour_rounder(cdt)
        # cdt_hr = cdt_hr.replace(hour=cdt_hr.hour-6)  # shifting current time, for test only
        cdt_hr_std = cdt_hr.replace(hour=cdt_hr.hour-1)
        cdt_hr_end = cdt_hr - timedelta(microseconds=1)

        print('acquiring data...\nfrom {} to {}.'.format(cdt_hr_std,cdt_hr_end) )

        for row in server_stock_list:
            yf_stock_symbol = '{}.tw'.format(row['symbol'])
            data = yf.Ticker(yf_stock_symbol)
            df = data.history(
                # period="2y",
                start=cdt_hr_std,
                end=cdt_hr_end,
                interval='1h'
            )
            if df.shape[0] == 0:  # no data exist
                continue
            # 1.增加股票代號
            df['stock_id'] = row['id']

            # 2.switch pd to sql type
            df.reset_index(
                level=0,
                # col_fill='tick',
                inplace=True
            )
            # 3.to request body
            df.rename(columns={'index': 'start_ts', 'Open': 'open', 'High': 'high', 'Low': 'low',
                    'Close': 'close', 'Volume': 'volume', 'Dividends': 'dividends', 'Stock Splits': 'stock_splits'}, inplace=True)
            body = json.loads(df.to_json(orient="records"))[0]
            # print(df, '\n')
            # print(body)
            # raise

            # 4.put request to create
            try:
                response = requests.post(
                    urljoin(os.getenv('SERVER_URL'), 'khours'), json=body)
                response.raise_for_status()
                print('sucess to add new {} (stock_id:{}) khour to local server.'.format(
                    yf_stock_symbol, row['id']))
            except requests.exceptions.HTTPError as e:  # e.g. 400, 401, 404...
                print(e)
                print(response.text)
            except Exception as e:
                print(e)
    
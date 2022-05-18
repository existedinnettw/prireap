
import pandas as pd
import requests
from ..crawSrc.crawBase import BasicCraw
from FinMind.data import DataLoader
from dotenv import load_dotenv
from os import getenv
from time import sleep
from datetime import datetime, date, timedelta
from pytz import utc
import warnings
from urllib.parse import urljoin
import json
from bs4 import BeautifulSoup
import re
from fake_useragent import UserAgent
import numpy as np
import subprocess


ua = UserAgent()

load_dotenv()
'''
[postgresql确定某张业务表最后被使用时间](https://www.cndba.cn/xty/article/3516)
最後執行日期4/3
目前的原定計畫是update用別的datasource:股利分派情形-經股東會確認
考慮登入router自動換ip or 用自己的電腦pppoe撥號
'''

# setting period
end_date = getenv('SCRIPT_END_DATE') #trade date
start_date = getenv('SCRIPT_START_DATE')
if end_date == None:
    end_date = datetime.utcnow().date()  # -timedelta(days=1)
if start_date == None:
    start_date = date.fromisoformat('2000-01-01')

# it's possible already get some stocks, to skip them, indicate stock_li
# 從local api 直接找找缺什麼更好
stock_skip_li = []
stock_start_id = 521 #413 #init 1
timeout = 60*1
wait_time=5 # 爬取間隔

print("\nThe crawler will get data from {} to {}".format(
    start_date.isoformat(), end_date.isoformat()))
# input("Press Enter to continue...\n")

craw = BasicCraw()
df_local_stocks = pd.DataFrame.from_dict(craw.list_exg_stocks())
df_local_stocks=df_local_stocks[df_local_stocks['id']>=stock_start_id]
# print(df_local_stocks)
# raise
for idx, stock in enumerate(df_local_stocks.iterrows()):
    stock = stock[1]
    symbol = stock['symbol']
    stock_id = stock['id']
    print('symbol:', symbol, 'stock_id:', stock_id)

    if (symbol not in stock_skip_li) and stock_id >= stock_start_id:
        api = DataLoader()  # 使用finmind
        # api.login_by_token(api_token=token)
        # api.login(user_id='user_id',password='password')
        url = "https://goodinfo.tw/tw/StockDividendSchedule.asp?STOCK_ID={}".format(
            symbol)
        # print('url:',url)
        headers = {
            "user-agent": ua.random
        }
        while True:
            try:
                r = requests.get(url, headers=headers, timeout=10)
                r.encoding = "utf-8"
                if "您的瀏覽量異常" in r.text:
                    print('blocked by server, switch ip by redial, wait 10s...')
                    subprocess.call([r'C:\Users\exist\Desktop\redial.bat'])
                    sleep(10)
                else:
                    break
            except:
                print('timeout except, try again')
                sleep(timeout)
        
        # print(r.text)
        tb = BeautifulSoup(r.text, "html.parser").find("table", id="tblDetail")
        if tb==None:
            # print(r.text)
            print('no table, skip...')
            sleep(5)
            continue
        tb=tb.select('tr[align="center"]')  # tbody tr
        # print('tb:',tb)
        li = [[col.text for col in row.find_all("td")] for row in tb]
        li2 = [[col.get('title', 'No title attribute')
                for col in row.select('td[align="right"]')] for row in tb]

        for i in range(len(li)):
            li[i] = li[i][:-7]+li2[i]

        # dfs=pd.read_html(''.join(tb))
        # print(dfs[0])
        # print()
        # print(li[12])
        cols = ['year', 'dvd_belong_year', 'holder_meet_date', 'cash_trade_date', 'ref_cash_dvd_price',
                'fin_cach_refill_date', 'cash_require_days', 'issue_cash_date', 'share_trade_date', 'ref_share_dvd_price',
                'fin_share_refill_date', 'share_require_days', 'cash_surplus_dvd', 'cash_apic_dvd', 'cash_sum_dvd',
                'share_surplus_dvd', 'share_apic_dvd', 'share_sum_dvd', 'sum_dvd']
        df = pd.DataFrame(li,
                          columns=cols
                          )
        df = df.drop(columns=['holder_meet_date', 'fin_cach_refill_date', 'cash_require_days', 'issue_cash_date', 'fin_share_refill_date', 'share_require_days',
                              'cash_surplus_dvd', 'cash_apic_dvd', 'share_surplus_dvd', 'share_apic_dvd', 'sum_dvd'
                              ])
        # print(df)

        # -->modify to suit for table column
        df['trade_date'] = df['cash_trade_date'].combine(df['share_trade_date'], max, fill_value=0)
        df=df.drop(df[df.trade_date==''].index)
        df['ref_price'] = df['ref_cash_dvd_price'].combine(df['ref_share_dvd_price'], max, fill_value=0)
        def date_str_to_date(row):
            date_str=row['trade_date']
            # print('date_str',date_str)
            # date_str=re.sub(r'[^\x00-\x7f]', ' ', date_str) #去中文
            date_str=re.findall(r"^[0-9'/]+", date_str)[0]
            # print('date_str',date_str)
            try:
                rst=datetime.strptime(date_str,"%y'%m/%d").date()
                return rst#.isoformat()
            except:
                return ''
        # print(df,'\n')
        # print(df.apply(date_str_to_date, axis=1),'\n')
        # print(df['trade_date'],'\n')
        df['trade_date']=df.apply(date_str_to_date, axis=1, result_type='reduce')
        # raise
        df = df[df['trade_date'] < end_date]
        df = df[df['trade_date'] >= start_date]
        df['trade_date'] = df['trade_date'].astype(str)
        # print(df)
        # raise
        if df.empty:
            print('no valid data for process(empty), skip to next...')
            sleep(wait_time)
            continue

        while True: #combine same day operation
            if not np.any(df['trade_date'].duplicated().values):
                break
            print('process combining...')
            fst_idx=np.where( df['trade_date'].duplicated(keep=False))[0][0]
            fst_el=df.iloc[fst_idx]
            ope_msk=df['trade_date']==fst_el['trade_date']
            ope_df=df[ope_msk]
            dividends=ope_df['cash_sum_dvd'].astype(float).sum()
            share_sum_dvd=ope_df['share_sum_dvd'].astype(float).sum()
            fst_el['cash_sum_dvd']=dividends
            fst_el['share_sum_dvd']=share_sum_dvd
            df=df[~ope_msk].append(fst_el, ignore_index = True)

        def year_str_to_interval_ratio(row):
            '''
            還沒有半年的
            '''
            year_str=row['dvd_belong_year']
            if 'Q' in year_str:
                return 4
            elif '半年' in year_str:
                return 2
            elif '全年' in year_str:
                return 1
            else:
                # not clear def
                # return 
                raise('unknown year_str input')
        df['interval_annual_ratio']=df.apply(year_str_to_interval_ratio, axis=1) #如果是empty df, 會key error

        def share_dvd_to_stock_split(row):
            share_dvd=row['share_sum_dvd']
            return 1+float(share_dvd)/10
        df['stock_split']=df.apply(share_dvd_to_stock_split, axis=1)
        # print(df)
        df = df.drop(columns=['dvd_belong_year','cash_trade_date','share_trade_date','ref_cash_dvd_price','ref_share_dvd_price',])
        df = df.rename(columns={'cash_sum_dvd':'dividends'}).replace({np.nan: None})

        # print(df)
        # raise

        # -->create body for api create
        df['stock_id']=stock_id
        df = df.drop(columns=['year','share_sum_dvd','ref_price'])

        body = df.to_dict(orient="records")
        body = [{k: v for k, v in el.items() if v!=None} for el in body]
        # print(body[0])
        # raise
        try:
            print('upload to local...')
            response = requests.post(
                urljoin(getenv('SERVER_URL'), 'composite/dvd_splt/'), json=body, timeout=timeout)
            response.raise_for_status()
            # print('sucess to add new {} (stock_id:{}) kday to local server.'.format( stock['symbol'], stock['id']))
        except requests.exceptions.HTTPError as e:  # e.g. 400, 401, 404...
            print(e)
            data = response.text
            # info = (data[:100] + '..') if len(data) > 100 else data
            # print('symbol:{}, response text:{}'.format(symbol, info))
            print('\n#=======\n{}\n#======\n'.format(data))
            raise
        except Exception as e:
            print(e)
            raise Exception('unkown error, plz fix.')

        #--> 各種delay避免鎖ip
        sleep(wait_time)
        # raise
    else:
        print('passed')


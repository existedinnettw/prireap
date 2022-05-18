
# import asyncio
# import aiohttp
# from requests import async
# import grequests #it seem gevent, monkey patch cause something on windos # Yes. Import requests after grequests
# gevent 本質是patch，應該用asyncio 代替
from base64 import encode
import requests
import os
from os import getenv
from dotenv import load_dotenv
from urllib.parse import urljoin
import time
# import datetime
from datetime import datetime, timedelta, tzinfo
import json
import orjson
import abc
# from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.asyncio import AsyncIOScheduler
# from apscheduler.triggers.cron import CronTrigger
from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_EXECUTED
import pytz
from cron_converter import Cron
import warnings
import yfinance as yf
from threading import Event  # use event to control 先後
from enum import Enum, auto
import pandas as pd
import functools
import socketio
import asyncio
import httpx
from .asioc import sio
import numpy as np
import warnings
import locale
from locale import atof

locale.setlocale(locale.LC_NUMERIC, '')
load_dotenv()


tpe_tz = pytz.timezone('Asia/Taipei')#LMT+8:06:00 STD



class CrawBase(metaclass=abc.ABCMeta):
    '''
    if really scrap data directly from page rather than api, Scrapy may be helpful
    '''

    def __init__(self):
        self.TWSE_OPENAPI_URL = 'https://openapi.twse.com.tw/v1/'
        self.TDCC_OPENAPI_URL = 'https://openapi.tdcc.com.tw/v1/'
        self.tpe_exg = self.get_tpe_exg()
        self.sched = AsyncIOScheduler()
        self.sio = sio

        # may split scheduler
        self.sched.add_listener(
            self._listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)
        self.sched.start()
        self.khour_event = Event()
        self.kday_event = Event()

        # await can't outside async function
        # await self.sio.connect(url=urljoin(os.getenv('SERVER_URL'),'ws'), socketio_path="/ws/socket.io", wait_timeout = 1)

        self.trade_day_start_dt = None
        self.trade_day_end_dt = None
        self.update_trade_day_dt()

    async def async_init(self):
        '''
        init 的時候就connect 還是比較好debug其它async func，不用每次從self.run 進入
        '''
        await self.sio.connect(url=urljoin(os.getenv('SERVER_URL'), 'ws'), socketio_path="/ws/socket.io", wait_timeout=1)
        await sio.emit('sub_kday')
        # await asyncio.sleep(10)
        # sio.emit('sub_kday')

    def get_tpe_exg(self):
        '''
        return object is in dict format
        TODO:
        can use schmas.py exchange
        '''
        try:
            exg = requests.get(urljoin(os.getenv('SERVER_URL'), 'exchanges'), params={
                'code_names': 'TPE'}).json()[0]
            return exg
        except requests.exceptions.HTTPError as error:
            print(error)
        # except requests.exceptions.
        except requests.exceptions.ConnectionError as e:  # ConnectionRefusedError
            print('\nError: Please make sure if the local server has been opened\n')
        except Exception as e:
            print(e)

    def __get_khours(self):
        '''
        for test only
        '''
        response = requests.get(
            urljoin(os.getenv('SERVER_URL'), 'kbars'), params={'interval': 'hour'})
        print(response.text)
        return response.text
    def _get_today_stocks_kday(self):
        '''
        '''
        url = 'https://www.twse.com.tw/exchangeReport/STOCK_DAY_ALL'
        '''
        https://www.twse.com.tw/exchangeReport/STOCK_DAY_ALL
        https://openapi.twse.com.tw/v1/exchangeReport/STOCK_DAY_ALL
        兩者得出的東西是不一樣的，openapi的會晚一天
        '''
        # print(url) #
        # https://www.twse.com.tw/exchangeReport/STOCK_DAY_ALL
        # headers = {'user-agent': 'Mozilla/5.0 (Macintosh Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36'}
        r = requests.get(url).json()
        # print(r.json())
        # raise
        df_stock_kday = pd.DataFrame.from_dict(r['data'])
        # ,orient='index',columns=['Code','Name','TradeVolume','TradeValue', 'OpeningPrice', 'HighestPrice','LowestPrice','ClosingPrice','Change','Transaction']
        # print(df_stock_kday.columns)
        df_stock_kday = df_stock_kday.rename(columns={0: 'Code', 1: 'Name', 2: 'TradeVolume', 3: 'TradeValue',
                                             4: 'OpeningPrice', 5: 'HighestPrice', 6: 'LowestPrice', 7: 'ClosingPrice', 8: 'Change', 9: 'Transaction'})
        df_stock_kday[['TradeVolume', 'TradeValue', 'OpeningPrice', 'HighestPrice', 'LowestPrice', 'ClosingPrice', 'Transaction']] = \
            df_stock_kday[['TradeVolume', 'TradeValue', 'OpeningPrice', 'HighestPrice', 'LowestPrice', 'ClosingPrice', 'Transaction']].applymap(atof)
        # Change 用不到
        df_stock_kday=df_stock_kday.astype({'TradeVolume':np.int64,'TradeValue':np.int64,'Transaction':np.int64})
        # print(df_stock_kday)
        # raise
        r_date = datetime.strptime(r['date'], '%Y%m%d').astimezone(tpe_tz).replace(hour=9, minute=0, second=0)  # "20220510"
        # print(r_date,np.datetime64(r_date))
        # raise
        df_stock_kday['start_ts']=np.datetime64(r_date) #will directly change to utc
        # print(df_stock_kday['start_ts'])
        # raise
        return df_stock_kday

    def add_tpe_stocks(self):
        official_stock_li = self._get_today_stocks_kday()

        exg_id = self.tpe_exg['id']
        server_stock_list = self.list_exg_stocks(exg_id)
        # print(server_stock_list)
        server_stock_symbols = [i['symbol'] for i in server_stock_list]
        # print(server_stock_symbols)

        for row in official_stock_li.iterrows():
            '''
            row.keys=dict_keys(['Code', 'Name', 'TradeVolume', 'TradeValue', 'OpeningPrice',
            'HighestPrice', 'LowestPrice', 'ClosingPrice', 'Change', 'Transaction'])
            '''
            row=row[1]
            # print(row)
            # raise
            if row['Code'] not in server_stock_symbols:
                # may replace by composite/stocks
                body = {"exchange_id": exg_id,
                        "symbol": row['Code'], "name": row['Name']}
                try:
                    response = requests.post(
                        urljoin(os.getenv('SERVER_URL'), 'stocks'), json=body)
                    response.raise_for_status()
                    print('sucess to add new stocks {} to local server.'.format(
                        row['Code']))
                except requests.exceptions.HTTPError as error:
                    print(error)
                # except requests.exceptions.
                except Exception as e:
                    print(e)
            else:
                print('the stock {} already exist, skip it'.format(
                    row['Code']))

    def list_exg_stocks(self, exg_id: int = None):
        '''
        list all stocks of specfic exg at local server
        '''
        if exg_id == None:
            exg_id = self.tpe_exg['id']
        server_stock_list = requests.get(
            urljoin(os.getenv('SERVER_URL'), 'stocks'), params={'exchanges': exg_id}).json()
        return server_stock_list

    def _hour_rounder(self, t):
        # Rounds to nearest hour by adding a timedelta hour if minute >= 30
        return (t.replace(second=0, microsecond=0, minute=0, hour=t.hour)
                + timedelta(hours=t.minute//30))

    @abc.abstractmethod
    def create_kmin_of_cur(self):
        '''
        should call outer api to get data, then store it to local server. 
        expect to be called at the starting of each minute.
        TODO
        notyetimplemented
        '''
        print('create_kmin_of_cur routine at {}....'.format(datetime.now()))

    @abc.abstractmethod
    def create_khour_of_cur(self):
        '''
        * Should call outer api to get data, then store it to local server. 
        * Expect to be called at the starting of each hour.
        * Each outer api have its own return data structure, that why should code it seperately.
        * To make sure execute after kmin, event is needed.
        TODO
        * 如果是要掃瞄缺少的資料，可以直接在loop call 這個function，同時自己改start & end time.
        * 1:00~1:30 acquire data 會有資料，可是
        notyetimplemented
        '''
        if not self.khour_event.wait(timeout=60):
            warnings.warn(
                'Some problem occur, no kmin event signal come...', RuntimeWarning)
        print('/********************************/\ncreate_khour_of_cur routine at {}....'.format(datetime.now()))

    def create_khour_of_cur_from_local(self):
        '''
        If it's promising to create khour from local kmin.
        call this function at implement "create_khour_of_hour" implement
        '''
        raise NotImplementedError

    async def create_kday_of_cur(self):
        '''
        * Expect to be called "after" few milisecond of exchange close.
        * 要處理sync timeing 問題
        TODO:
        * grequests 會導致local server的 sqlalchemy怪怪的。目前先不async
        * 如果不在official名單內的(下市)要delete，上市的要add。
        * 目前還不確定盤後資料更新時間
        '''
        print('/********************************/\ncreate_kday_of_cur routine at {}....'.format(datetime.now()))
        # url = urljoin(self.TWSE_OPENAPI_URL, 'exchangeReport/STOCK_DAY_ALL')
        # ?response=open_data可以得到csv
        df_stock_kday=self._get_today_stocks_kday()


        while True:
            df_local_stocks = pd.DataFrame.from_dict(self.list_exg_stocks())
            # print(df_local_stocks)
            df_outer = pd.merge(left=df_stock_kday, right=df_local_stocks,
                                how='outer', left_on='Code', right_on='symbol', indicator=True)
            # df_listed = df_stock_kday.merge(right=df_local_stocks, how = 'outer' ,indicator=True).loc[lambda x : x['_merge']=='left_only'] #上市
            df_listed = df_outer.loc[lambda x: x['_merge']
                                     == 'left_only']  # 上市
            # df_shimoichi=df_stock_kday.merge(df_local_stocks, how = 'outer' ,indicator=True).loc[lambda x : x['_merge']=='right_only'] #下市
            df_shimoichi = df_outer.loc[lambda x: x['_merge'] == 'right_only']
            if not df_listed.empty:
                print(df_listed)
                self.add_tpe_stocks()
            else:
                # 到底要不要把下市的股票是個問題，刪掉了話，程式會運行的比較快，不會有太多例外。
                # 但是很多時候，strategy 要有辦法自己避開有問題的股票，如果給的是一定沒有下市的資料，就會bias
                break
                if not df_shimoichi.empty:
                    print(df_shimoichi)
                else:
                    break

            # raise
        # df_join = pd.merge(left=df_stock_kday, right=df_local_stocks,
        #                    how='left', left_on='Code', right_on='symbol')
        df_join = df_outer.loc[lambda x: x['_merge'] == 'both']
        # print(df_join.replace(r'^\s*$', None, regex=True))
        # print(df_join)
        df_na = df_join[df_join[['id']].isna().any(axis=1)]
        if not df_na.empty:
            print(df_na)
            raise ValueError('exist row with id is None, check your logic')

        # r_date = 

        # print(r_date)
        # raise
        '''
        rs = [] 
        for row in df_join.iterrows():
            # add to local server
            row=row[1] #the second one is series
            body = {'stock_id': row['id'], 'start_ts': r_date.isoformat(), 'open': row['OpeningPrice'],
                    'high': row['HighestPrice'], 'low': row['LowestPrice'], 'close': row['ClosingPrice'],
                    'volume': row['TradeVolume'], 'transaction': row['Transaction'], 'interval': 'day', }
            rs.append( grequests.post(urljoin(os.getenv('SERVER_URL'), 'kbars'), json=body) )
        # print(rs)
        # raise
        def exception_handler(request, exception):
            print(exception)
        resp=grequests.map(rs, exception_handler=exception_handler)
        print(resp)
        print(resp[0].text)
        '''
        ws_body_li = list()
        #fastapi have bug on iso8601 datatime parsing
        # df['date']=df['date']+'T'+time(hour=1, tzinfo=utc).isoformat()
        # raise
        for row in df_join.iterrows():
            row = row[1]
            start_ts=row['start_ts'].isoformat()+'+00:00'
            # print(str(row['start_ts']),row['start_ts'].isoformat(), start_ts)
            # raise
            body = {'stock_id': row['id'], 'start_ts': start_ts, 'open': row['OpeningPrice'],
                    'high': row['HighestPrice'], 'low': row['LowestPrice'], 'close': row['ClosingPrice'],
                    'volume': row['TradeVolume'], 'transaction': row['Transaction']}
            ws_body_li.append(body)

            # if value is empty, don't passit
            body = {k: v for k, v in body.items() if v}
            body.update({'interval': 'day'})
            try:
                response = requests.post(
                    urljoin(os.getenv('SERVER_URL'), 'kbars'), json=body)
                response.raise_for_status()
                print('sucess to add new {} (stock_id:{}) kday to local server.'.format(
                    row['symbol'], row['id']))
            except requests.exceptions.HTTPError as e:  # e.g. 400, 401, 404...
                print(e)
                print('symbol:{}, response text:{}'.format(
                    row['symbol'], response.text))
                # print(body)
                # print(type(body['high']))
            except Exception as e:
                print(e)
            # if row['symbol']=='00684R':
            #     break

        #-->直接透過websocket 傳到 agent
        jstr = orjson.dumps(ws_body_li)
        # not work if connect at different event loop
        await self.sio.emit('pub_kday', data=jstr)
        # websocket是實際result不需要 interval

        return

    async def create_eqty_disp(self):
        '''
        * weekly grap eqty disp
        * 目前沒考慮當週都不開市的情況（過年），理論上會因為重複而產生http error
            * 考慮check
            * 考慮先query db裡的資料，不重複的再送出
        '''
        print('/********************************/\n create_eqty_disp routine at {}....'.format(datetime.now()))
        # https://openapi.twse.com.tw/v1/opendata/1-5
        url = urljoin(self.TDCC_OPENAPI_URL, 'opendata/1-5')
        # print(url)
        r = requests.get(url)
        r.encoding = 'utf-8'
        # r.encoding='big5'
        df = pd.DataFrame.from_dict(r.json())
        # print(df)
        # -->modify to suit for table column
        df = df.rename(columns={"﻿資料日期": 'date', '證券代號': 'symbol', '占集保庫存數比例%': 'percent',
                       '人數': 'people', '股數': 'unit', '持股分級': 'HoldingSharesLevel'}).astype({'people': np.int64, 'unit': np.int64})
        # mapping date
        df['date'] = df['date'].apply(
            lambda x: datetime.strptime(x, '%Y%m%d').strftime('%Y-%m-%d'))
        map_HoldingSharesLevel = {
            '1': 'l1',
            '2': 'l2',
            '3': 'l3',
            '4': 'l4',
            '5': 'l5',
            '6': 'l6',
            '7': 'l7',
            '8': 'l8',
            '9': 'l9',
            '10': 'l10',
            '11': 'l11',
            '12': 'l12',
            '13': 'l13',
            '14': 'l14',
            '15': 'l15',
            '16': 'diff',
            '17': None,
        }
        df['HoldingSharesLevel'] = df['HoldingSharesLevel'].map(
            map_HoldingSharesLevel)
        df = df.drop(columns=['percent'])  # 'symbol'
        df = df[~df['HoldingSharesLevel'].isnull()]
        # print('init_df\n', df.head(18))
        # raise

        def temp(df: pd.DataFrame):
            '''
            the method is very difficult...
            '''
            # df_t=df.T
            n_per = df['people'].values
            # col = df.columns
            n = df['unit'].values
            # raise
            data = np.concatenate((n_per[:-1], n)).reshape((1, -1))
            # print(data)
            new_df = pd.DataFrame(data=data, columns=[
                'l1_nper', 'l2_nper', 'l3_nper', 'l4_nper', 'l5_nper', 'l6_nper', 'l7_nper', 'l8_nper',
                'l9_nper', 'l10_nper', 'l11_nper', 'l12_nper', 'l13_nper', 'l14_nper', 'l15_nper',
                'l1_n', 'l2_n', 'l3_n', 'l4_n', 'l5_n', 'l6_n', 'l7_n', 'l8_n',
                'l9_n', 'l10_n', 'l11_n', 'l12_n', 'l13_n', 'l14_n', 'l15_n', 'diff_n'])
            # print(new_df)
            # raise
            return new_df
        new_df = df.groupby(['symbol', 'date'],).apply(temp)
        # print('fin df:\n', new_df)
        # print(new_df.loc['0050',])
        # print(new_df.columns) #AttributeError: 'Series' object has no attribute 'columns'
        # raise
        new_df = new_df.reset_index(drop=False).replace(
            {np.nan: None})  # json can handle none but not nan
        # new_df['date'] = df['date']
        # map symbol to stock_id
        df_local_stocks = pd.DataFrame.from_dict(
            self.list_exg_stocks()).set_index('symbol')
        # print(df_local_stocks)
        new_df = new_df.set_index('symbol')
        new_df['stock_id'] = df_local_stocks['id']
        new_df = new_df.reset_index(drop=True)
        # clear if stock_id not in db
        new_df = new_df[~new_df['stock_id'].isnull()]

        # print('fin df:\n',new_df)
        # raise

        # --> create dict for create request.
        body = new_df.to_dict(orient="records")
        body = [{k: v for k, v in el.items() if v != None} for el in body]
        # body = [body[0]]
        # print(body)
        # raise
        try:
            print('upload to local...')
            response = requests.post(
                urljoin(getenv('SERVER_URL'), 'composite/eqty_disp/'), json=body, timeout=30)
            response.raise_for_status()
            # print('sucess to add new {} (stock_id:{}) kday to local server.'.format( stock['symbol'], stock['id']))
        except requests.exceptions.HTTPError as e:  # e.g. 400, 401, 404...
            print(e)
            data = response.text
            # info = (data[:75] + '..') if len(data) > 75 else data
            print('error at date:{},\nresponse text:{}'.format(
                df['date'][0], data))
            # print('symbol:{},\nresponse text:{}'.format(symbol, data))
            raise Exception('local server error, plz fix.')
        except Exception as e:
            print(e)
            raise Exception('unkown error, plz fix.')
        # raise

        # jstr = orjson.dumps(ws_body_li)
        # await self.sio.emit('pub_kday',data=jstr) #not work if connect at different event loop
        print('===============fin eqty disp==================\n')

        return
    # @abc.abstractmethod

    async def create_cfs(self):
        '''
        cfs，等5/15再implement
        '''
        raise NotImplementedError

    async def create_dvd_splt(self):
        '''
        目前沒有很好的來源拿到除權息資料
        '''
        raise NotImplementedError

    def check_open(self):
        '''
        * check if the exchage is open today,
            because it will close at some nature specific holiday.
        * used at the begining of trade day,
            rather than every minute, or the time exchage had been closed.
        At defaul, use yahoo finance api to solve this problem, and child class can't overrides it to
            achieve better performance.
        return: True or False
        TODO:
        * set timeout to request to prevent strange behavior
        * 試搓的時候就會return true，這樣是正確的嗎?: 不是，這樣會執行兩次tradeday routine
        '''

        tsmc = yf.Ticker("2330.tw")
        cdt = datetime.now()
        start = cdt-timedelta(minutes=1)
        # end=cdt+timedelta(minutes=1)
        # print('{}\n'.format(start))
        print('checking open...')
        # https://query1.finance.yahoo.com/v8/finance/chart/2330.TW?period1=1636419064&period2=1636419124&interval=1d&includePrePost=False&events=div%2Csplits
        for i in range(3):
            df = tsmc.history(
                # period="2y",
                start=start,  # period = "ytd",
                # end=end,
                # interval='1m' #don't know why not work.
            )
            if df.shape[0] == 0:
                # no response, wait and try again...
                time.sleep(0.5)
            else:
                print('exchange is open today')
                # print(df)
                return True
        warnings.warn("Doesn't detecte exchange opened.", RuntimeWarning)
        return False

    def update_trade_day_dt(self):
        '''
        了解並儲存下一個exg的開、閉市時間，還有目前是否在開市時間
        根據這個資料去調整啟動routine
        * if market is trading, start_dt<ref<end_dt
        * if market is not trading, ref<start_dt<end_dt
        * output datetime is in utc timezone.
        '''
        reference = datetime.utcnow()
        cron_sch_trade_day_start = Cron(
            self.tpe_exg['strt_cron_utc']).schedule(reference)
        cron_sch_trade_day_end = Cron(
            self.tpe_exg['end_cron_utc']).schedule(reference)
        self.trade_day_start_dt = cron_sch_trade_day_start.next()
        self.trade_day_end_dt = cron_sch_trade_day_end.next()
        if self.trade_day_end_dt <= self.trade_day_start_dt:  # if already in tradeday
            cron_sch_trade_day_start.reset()
            self.trade_day_start_dt = cron_sch_trade_day_start.prev()
        print('refecrence:{}, start_dt:{}, end_dt:{}'.format(
            reference, self.trade_day_start_dt.isoformat(), self.trade_day_end_dt.isoformat()))
        return reference, self.trade_day_start_dt, self.trade_day_end_dt

    def trade_day_routine(self):
        '''
        * this function is supposed to be called "after" few ms of exchange start. 
            or called during trade day time.
        * 只會在開市時執行一次，分配“當天”任務，所以一定要加end，或是次數限制
        TODO
        -------
        可能要更詳細的考慮程式執行當下的情況
        '''
        print('trade_day_routine at {}....'.format(datetime.now()))
        if self.check_open():  # it possible that exchange close during local holiday.
            '''
            the exchange have started.
            start dalily get data e.g. kmin khour kday
            '''
            reference, trade_day_start_dt, trade_day_end_dt = self.update_trade_day_dt()

            self.sched.add_job(self.create_kmin_of_cur, 'cron',
                               start_date=trade_day_start_dt +
                               timedelta(minutes=1),
                               end_date=trade_day_end_dt,
                               second=0,  # minutely
                               timezone=pytz.utc, jitter=None, id='MIN_ROUTINE')
            # 用signal?, start at next hour to acquire previous 1 hour
            self.sched.add_job(self.create_khour_of_cur, 'cron',
                               start_date=trade_day_start_dt +
                               timedelta(hours=1),
                               end_date=trade_day_end_dt,
                               minute=0,  # hourly
                               timezone=pytz.utc, jitter=None, id='HOUR_ROUTINE')
        else:
            warnings.warn(
                "the exchange doesn't open today, or there are some bug in your code or setting...", RuntimeWarning)

    async def add_days_routine(self):
        '''
        * 在下次開市之前執行了話，已經錯過的routine會補齊，已經開市就不會再補了
        '''
        self.sched.add_job(self.create_kday_of_cur, 'cron',
                           day_of_week='mon-fri', hour=6, id='DAY_ROUTINE', timezone=pytz.utc)  # 2pm==6amutc
        reference, trade_day_start_dt, trade_day_end_dt = self.update_trade_day_dt()
        cron_sch_trade_day_end = Cron(
            self.tpe_exg['end_cron_utc']).schedule(reference)
        last_trade_day_end_dt = cron_sch_trade_day_end.prev()
        # 已經5pm 之後，9am之前
        # print(reference, trade_day_start_dt, trade_day_end_dt, last_trade_day_end_dt.replace(hour=9))
        # raise
        if reference < trade_day_start_dt and reference > last_trade_day_end_dt.replace(hour=6,minute=0):#utc time=tpe time 2pm
            # 處理不了如果在週六日開啟
            # print(reference, trade_day_start_dt, last_trade_day_end_dt)
            # raise
            await self.create_kday_of_cur()
        # raise
        return

    async def add_weeks_routine(self):
        '''
        由於沒有開市問題，直接add job就好
        '''
        self.sched.add_job(self.create_eqty_disp, 'cron',
                           day_of_week='sun', id='WEEK_ROUTINE', timezone=tpe_tz)
        if datetime.today().weekday() == 6:  # already sunday
            self.create_eqty_disp()

    def _listener(self, event):
        '''
        apsscheduler listner 
        '''
        # print(event)
        if not event.exception:
            print('job_id:{}'.format(event.job_id))
        if event.job_id in ['HOUR_ROUTINE', 'TRADE_DAY_ROUTINE', 'DAY_ROUTINE']:
            self.sched.print_jobs()
            print()

    async def run(self):
        '''
        run the crawler with timer to create kmin, khour periodically.
        從大到小，先create TRADE_DAY_ROUTINE 的job，這個job是週期性的在work days 執行
        這個job會產生“該天”內所有週期性的工作，e.g. add kdays。原因在於如果當天是國定假日沒有開市，則不必add work。
        TODO:
        1.開shceduler 下個開市時間。如果scheduler是用subprocess 會需要query自己的data，且錯誤不會顯示在同一頁面，但是時間會準。
            create_khour_of_cur_from_local 會需要等kmin完成才被call
            1.要有機制可以確定今天有沒有開市，或這個時間點有沒有資料，否則一直浪費query。 query 台積 to check
            1-5.掃瞄最後更新資料的時間點和現在時間確定有沒有漏資料？ too costy, 且掃多少是個問題.
            2.確定以後直接開scheduler for 當天，kmin khour kday, 多開還是stack deep call，可以用crontab end的timedelta差值去
                check是否已經閉市。deep call比較好
                1.如果api 有query 限制，就必須按照限制去開subprocess
        '''
        # loop=asyncio.get_running_loop()
        # await self.sio.connect(url=urljoin(os.getenv('SERVER_URL'),'ws'), socketio_path="/ws/socket.io", wait_timeout = 1)
        cron_parts = Cron(self.tpe_exg['strt_cron_utc'], {
                          'output_weekday_names': True}).parts  # .schedule(reference)

        # apscheduler bug: https://github.com/agronholm/apscheduler/issues/286
        reference, trade_day_start_dt, trade_day_end_dt = self.update_trade_day_dt()
        # trade_day_routine 只會在開市時執行一次
        # job = self.sched.add_job(self.trade_day_routine, 'cron',
        #                          minute=cron_parts[0], hour=cron_parts[1],
        #                          day=cron_parts[2], month=cron_parts[3],
        #                          day_of_week=cron_parts[4], timezone=pytz.utc, jitter=None, id='TRADE_DAY_ROUTINE')  # cron_parts[4], 'mon-fri'
        # if trade_day_start_dt < reference:
        #     self.trade_day_routine()  # already in trade day time, fire immediately
        #     warnings.warn(
        #         'currently, market is trading, so there is definately lose some data.\nmake sure this is acceptable for you.', UserWarning)
        #     input("input any key to consume...")
        await self.add_days_routine()
        await self.add_weeks_routine()

        self.sched.print_jobs()
        # await self.sio.emit('pub_kday',data={'test':456}) #not work if connect at different event loop
        # print('sio:{}\n\n'.format(self.sio))
        # print()
        # while True:
        #     time.sleep(60)
        try:
            # asyncio.get_running_loop().run_forever()
            # await asyncio.sleep(10) #use while
            await asyncio.Event().wait()
            # await asyncio.Event().wait()
        except (KeyboardInterrupt, SystemExit):
            pass


class BasicCraw(CrawBase):
    def __init__(self):
        super().__init__()

    def create_kmin_of_cur(self):
        return super().create_kmin_of_cur()

    def create_khour_of_cur(self):
        return super().create_khour_of_cur()


if __name__ == '__main__':
    '''
    for debug only
    '''
    async def main():
        # crawler=YfCraw()
        crawler = BasicCraw()
        await crawler.async_init()
        await crawler.create_kday_of_cur()
        # crawler.add_tpe_stocks()
        # await crawler.create_eqty_disp()
        # await asyncio.Event().wait()
    asyncio.run(main())

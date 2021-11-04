
# import asyncio
# import aiohttp
# from requests import async
import grequests
import requests  # Yes. Import requests after grequests
import os
from dotenv import load_dotenv
from urllib.parse import urljoin
import time
from datetime import datetime, timedelta
import json
import abc
# from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.schedulers.background import BackgroundScheduler
# from apscheduler.schedulers.asyncio import AsyncIOScheduler
# from apscheduler.triggers.cron import CronTrigger
from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_EXECUTED
import pytz
import time
from cron_converter import Cron
import warnings
import yfinance as yf
from threading import Event  # use event to control 先後
from enum import Enum, auto
import pandas as pd


load_dotenv()


class CrawBase(metaclass=abc.ABCMeta):
    '''
    if really scrap data directly from page rather than api, Scrapy may be helpful
    '''

    def __init__(self):
        self.TWSE_OPENAPI_URL = 'https://openapi.twse.com.tw/v1/'
        self.tpe_exg = self.get_tpe_exg()
        self.sched = BackgroundScheduler()
        # may split scheduler
        self.sched.add_listener(
            self._listner, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)
        self.sched.start()
        self.khour_event = Event()
        self.kday_event = Event()

        self.trade_day_start_dt = None
        self.trade_day_end_dt = None
        self.update_trade_day_dt()

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

    def add_tpe_stocks(self):
        r = requests.get(urljoin(self.TWSE_OPENAPI_URL,
                         'exchangeReport/STOCK_DAY_ALL'))
        official_stock_li = r.json()

        exg_id = self.tpe_exg['id']
        server_stock_list = self.list_exg_stocks(exg_id)
        # print(server_stock_list)
        server_stock_symbols = [i['symbol'] for i in server_stock_list]
        # print(server_stock_symbols)

        for row in official_stock_li:
            '''
            row.keys=dict_keys(['Code', 'Name', 'TradeVolume', 'TradeValue', 'OpeningPrice',
            'HighestPrice', 'LowestPrice', 'ClosingPrice', 'Change', 'Transaction'])
            '''
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
        '''
        if not self.khour_event.wait(timeout=3):
            warnings.warn(
                'Some problem occur, no kmin event signal come...', RuntimeWarning)
        print('/********************************/\ncreate_khour_of_cur routine at {}....'.format(datetime.now()))

    def create_khour_of_cur_from_local(self):
        '''
        If it's promising to create khour from local kmin.
        call this function at implement "create_khour_of_hour" implement
        '''
        raise NotImplementedError

    def create_kday_of_cur(self):
        '''
        * Expect to be called "after" few milisecond of exchange close.
        * 要處理sync timeing 問題
        TODO:
        * TWSE 資料更新時間不確定，且資料內沒有標時間
        * grequests 會導致local server的 sqlalchemy怪怪的。
        '''

        url = urljoin(self.TWSE_OPENAPI_URL, 'exchangeReport/STOCK_DAY_ALL')
        r = requests.get(url)
        df_stock_kday = pd.DataFrame.from_dict(r.json())

        df_local_stocks = pd.DataFrame.from_dict(self.list_exg_stocks())
        # print(df_local_stocks)
        df_join = pd.merge(left=df_stock_kday, right=df_local_stocks,
                           how='left', left_on='Code', right_on='symbol')
        # print(df_join.replace(r'^\s*$', None, regex=True))
        print(df_join)
        # raise

        rs = [] #Wed, 03 Nov 2021 21:00:42 GMT
        r_date = datetime.strptime(r.headers['last-modified'],"%a, %d %b %Y %H:%M:%S %Z")
        r_date = r_date.replace(hour=1, minute=0, second=0) #TPE time better method
        # print(r_date)
        # raise
        '''
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
        for row in df_join.iterrows():
            row=row[1]
            # print(row['symbol'])
            body = {'stock_id': row['id'], 'start_ts': r_date.isoformat(), 'open': row['OpeningPrice'],
                                'high': row['HighestPrice'], 'low': row['LowestPrice'], 'close': row['ClosingPrice'],
                                'volume': row['TradeVolume'], 'transaction': row['Transaction'], 'interval': 'day', }
            body={k:v for k,v in body.items() if v}
            try:
                response = requests.post(
                    urljoin(os.getenv('SERVER_URL'), 'kbars'), json=body)
                response.raise_for_status()
                print('sucess to add new {} (stock_id:{}) khour to local server.'.format(
                    row['symbol'], row['id']))
            except requests.exceptions.HTTPError as e:  # e.g. 400, 401, 404...
                print(e)
                print('symbol:{}, response text:{}'.format(row['symbol'], response.text))
                # print(body)
                # print(type(body['high']))
            except Exception as e:
                print(e)
            # if row['symbol']=='00684R':
            #     break

    # @abc.abstractmethod

    def check_open(self):
        '''
        This method is design to check if the exchage is open,
            because it will close at some nature specific holiday.
        This method is design to be used at the begining of trade day,
            rather than every minute, or the time exchage had been closed.
        At defaul, use yahoo finance api to solve this problem, and child class can't overrides it to
            achieve better performance.
        return: True or False
        '''
        tsmc = yf.Ticker("2330.tw")
        cdt = datetime.now()
        start = cdt-timedelta(minutes=1)
        # end=cdt+timedelta(minutes=1)
        # print('{}\n'.format(start))
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
                print(df)
                return True
        warnings.warn("Doesn't detecte exchange opened.", RuntimeWarning)
        return False

    def update_trade_day_dt(self):
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

    def trade_day_routine(self):
        '''
        this function is supposed to be called "after" few ms of exchange start. 
        or called during trade day time.
        '''
        print('trade_day_routine at {}....'.format(datetime.now()))
        if self.check_open():  # it possible that exchange close during local holiday.
            '''
            the exchange have started.
            start dalily get data e.g. kmin khour kday
            '''
            self.update_trade_day_dt()  # the start time will be effected...

            self.sched.add_job(self.create_kmin_of_cur, 'cron',
                               start_date=self.trade_day_start_dt +
                               timedelta(minutes=1),
                               end_date=self.trade_day_end_dt,
                               second=0,  # minutely
                               timezone=pytz.utc, jitter=None, id='MIN_ROUTINE')
            # 用signal?, start at next hour to acquire previous 1 hour
            self.sched.add_job(self.create_khour_of_cur, 'cron',
                               start_date=self.trade_day_start_dt +
                               timedelta(hours=1),
                               end_date=self.trade_day_end_dt,
                               minute=0,  # hourly
                               timezone=pytz.utc, jitter=None, id='HOUR_ROUTINE')

        else:
            warnings.warn(
                "the exchange doesn't open today, or there are some bug in your code or setting...", RuntimeWarning)

    def _listner(self, event):
        # print(event)
        if not event.exception:
            print('job_id:{}'.format(event.job_id))
        if event.job_id in ['HOUR_ROUTINE']:
            self.sched.print_jobs()

    def run(self):
        '''
        run the crawler with timer to create kmin, khour periodically.
        TODO:
        1.開shceduler 下個開市時間。如果scheduler是用subprocess 會需要query自己的data，且錯誤不會顯示在同一頁面，但是時間會準。
            create_khour_of_cur_from_local 會需要等kmin完成才被call
            1.要有機制可以確定今天有沒有開市，或這個時間點有沒有資料，否則一直浪費query。 query 台積 to check
            1-5.掃瞄最後更新資料的時間點和現在時間確定有沒有漏資料？ too costy, 且掃多少是個問題.
            2.確定以後直接開scheduler for 當天，kmin khour kday, 多開還是stack deep call，可以用crontab end的timedelta差值去
                check是否已經閉市。deep call比較好
                1.如果api 有query 限制，就必須按照限制去開subprocess
        '''
        cron_parts = Cron(self.tpe_exg['strt_cron_utc'], {
                          'output_weekday_names': True}).parts  # .schedule(reference)

        # apscheduler bug: https://github.com/agronholm/apscheduler/issues/286
        job = self.sched.add_job(self.trade_day_routine, 'cron',
                                 minute=cron_parts[0], hour=cron_parts[1],
                                 day=cron_parts[2], month=cron_parts[3],
                                 day_of_week=cron_parts[4], timezone=pytz.utc, jitter=None, id='TRADE_DAY_ROUTINE')  # cron_parts[4], 'mon-fri'
        if self.check_open():
            self.trade_day_routine()  # in trade day time, fire immediately

        self.sched.print_jobs()
        while True:
            time.sleep(10*60)

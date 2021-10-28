import requests
import os
from dotenv import load_dotenv
from urllib.parse import urljoin
import time
from datetime import datetime, timedelta
import json
import abc


load_dotenv()


class CrawBase(metaclass=abc.ABCMeta):
    def __init__(self):
        self.REQUEST_URL = 'https://openapi.twse.com.tw/v1/exchangeReport/STOCK_DAY_ALL'
        self.tpe_exg = self.get_tpe_exg()

    def get_tpe_exg(self):
        '''
        return object is in dict format
        '''
        exg = requests.get(urljoin(os.getenv('SERVER_URL'), 'stocks'), params={
            'code_names': 'TPE'}).json()[0]
        return exg

    def __get_khours(self):
        '''
        for test only
        '''
        response = requests.get(
            urljoin(os.getenv('SERVER_URL'), 'khours'))
        print(response.text)
        return response.text

    def add_tpe_stocks(self):
        r = requests.get(self.REQUEST_URL)
        official_stock_li = r.json()

        exg_id = self.get_tpe_exg_id()
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

    def list_exg_stocks(self, exg_id):
        '''
        list all stocks of specfic exg at local server
        '''
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
        pass

    @abc.abstractmethod
    def create_khour_of_cur(self):
        '''
        Should call outer api to get data, then store it to local server. 
        Expect to be called at the starting of each hour.
        Each outer api have its own return data structure, that why should code it seperately.
        '''
        pass

    def create_khour_of_cur_from_local(self):
        '''
        If it's promising to create khour from local kmin.
        call this function at implement "create_khour_of_hour" implement
        '''
        raise NotImplementedError

    @abc.abstractmethod
    def check_open(self):
        '''
        This method is design to check if the exchage is open,
        because it will at some nature specific holiday.
        This method is design to be used at the begining of trade day,
        rather than every minute, or the time exchage had been closed.
        '''
        pass

    def run(self):
        '''
        run the crawler with timer to create kmin, khour periodically.
        TODO:
        要有機制可以確定今天有沒有開市，或這個時間點有沒有資料，否則一直浪費query。 query 台積 to check
        
        '''

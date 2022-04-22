
from operator import ne
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

'''
最後執行日期4/4
'''

load_dotenv()

end_date = getenv('SCRIPT_END_DATE')
start_date = getenv('SCRIPT_START_DATE')
end_date=date(2022, 4, 4)
if end_date == None:
    end_date = datetime.utcnow().date()  # -timedelta(days=1)
if start_date == None:
    start_date = date.fromisoformat('2000-01-01')

# it's possible already get some stocks, to skip them, indicate stock_li
stock_skip_li = []  # ['2330','0050']
stock_start_id = 599  # 2 #489
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
            df = api.taiwan_stock_financial_statement(
                stock_id=symbol,
                start_date=start_date.isoformat(),
                end_date=end_date.isoformat(),
                timeout=timeout
            )
        except Exception as e:
            msg=e.args[0]
            # print(e.args)
            # print(e.__context__)
            # print(type(msg))
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
        # print(df)
        # print(df[['type','origin_name']].drop_duplicates(keep='last').sort_values(by=['type','origin_name'])) #show unique name
        df = df[df['type'] != '-']
        cols = sorted(list(df['type'].unique()))
        # print('\n')
        # print('\n'.join(cols))
        # print(len(cols), '\n')
        # raise
        df = df.replace({
            'CumulativeEffectOfChanges': 'CumulativeEffectOfChangesInAccountingPrinciple',
            'IncomeAfterTax': 'IncomeAfterTaxes',
        })
        map = {
            'AdjustmentItem': 'adjustment_item',
            'CostOfGoodsSold': 'cost_of_goods_sold',
            'CumulativeEffectOfChangesInAccountingPrinciple': 'cumulative_effect_of_changes_in_accounting_principle',
            'EPS': 'eps',
            'EquityAttributableToOwnersOfParent': 'equity_attributable_to_owners_of_parent',
            'ExtraordinaryItems': 'extraordinary_items',
            'GrossProfit': 'gross_profit',
            'IncomeAfterTaxes': 'income_after_taxes',
            'IncomeBeforeIncomeTax': 'income_before_income_tax',
            'IncomeBeforeTaxFromContinuingOperations': 'income_before_tax_from_continuing_operations',
            'IncomeFromContinuingOperations': 'income_from_continuing_operations',
            'IncomeLossFromDiscontinuedOperation': 'income_loss_from_discontinued_operation',
            'NetIncome': 'net_income',
            'NoncontrollingInterests': 'noncontrolling_interests',
            'OperatingExpenses': 'operating_expenses',
            'OperatingIncome': 'operating_income',
            'OtherComprehensiveIncome': 'other_comprehensive_income',
            'OTHNOE': 'other_nonoperating_expense_or_loss',
            'PreTaxIncome': 'pre_tax_income',
            'RealizedGain': 'realized_gain',
            'RealizedGainFromInterAffiliateAccounts': 'realized_gain_from_inter_affiliate_accounts',
            'Revenue': 'revenue',
            'TAX': 'tax',
            'TotalConsolidatedProfitForThePeriod': 'total_consolidated_profit_for_the_period',
            'TotalNonbusinessIncome': 'total_nonbusiness_income',
            'TotalNonoperatingIncomeAndExpense': 'total_nonoperating_income_and_expense',
            'TotalnonbusinessExpenditure': 'total_nonbusiness_expenditure',
            'UnrealizedGain': 'unrealized_gain',
            'UnrealizedGainFromInterAffiliateAccounts': 'unrealized_gain_from_inter_affiliate_accounts',
        }
        df = df.replace(map)
        cols=list(map.values())
        # print(cols)
        new_df=pd.DataFrame(columns=['date']+cols)
        # print(df[['type','origin_name']].drop_duplicates())
        new_df['date']= pd.Series(df['date'].unique()).sort_values()
        temp_new_df=new_df.copy()
        temp_new_df['date'] = pd.to_datetime(new_df['date'])
        temp_new_df=temp_new_df.set_index('date')
        for row in df.iterrows():
            row=row[1]
            # print(row)
            # print(type(row))
            col=row['type']
            d=pd.to_datetime(row['date'])
            # print(d,col,row['value'])
            temp_new_df.at[d,col]=row['value'] #same as df[col][d]
            # raise
            # break
        # print(temp_new_df)
        temp_new_df=temp_new_df.reset_index(drop=True)
        temp_new_df['date']=new_df['date']
        new_df=temp_new_df
        new_df['stock_id'] = stock_id
        new_df = new_df.fillna('')
        # print(new_df, )
        # print(new_df.max())
        # print(new_df.min())
        # raise

        #--> create dict for create request.
        body = new_df.to_dict(orient="records")
        body = [{k: v for k, v in el.items() if v!=None} for el in body]
        # body = [body[0]]
        # print(body[0])
        # raise
        try:
            print('upload to local...')
            response = requests.post(
                urljoin(getenv('SERVER_URL'), 'composite/cfs/'), json=body, timeout=timeout)
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

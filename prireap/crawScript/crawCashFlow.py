
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
import numpy as np

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
stock_start_id = 612  # 2 #489
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
        while True:
            try:
                df = api.taiwan_stock_cash_flows_statement(
                    stock_id=symbol,
                    start_date=start_date.isoformat(),
                    end_date=end_date.isoformat(),
                    timeout=timeout
                )
            except Exception as e:
                msg=e.args[0]
                if "Requests reach the upper limit" in msg:
                    print("block by server, redial...")
                    subprocess.call([r'C:\Users\exist\Desktop\redial.bat'])
                    sleep(10)
                    continue
                else:
                    raise Exception('unkown error')
            break
        # req_counter += 1

        if not df.shape[0]:
            warnings.warn("May be blocked by server.", RuntimeWarning)
        if df.empty:
            print("no data, pass")
            continue

        # -->modify to suit for table column
        # print(df.head)
        # print(df[['type','origin_name']].drop_duplicates(keep='last').sort_values(by=['type','origin_name'])) #show unique name
        # raise
        # df = df[df['type'] != '-']
        cols = sorted(list(df['type'].unique()))
        # print('\n')
        # print('\n'.join(cols))
        # print(len(cols), '\n')
        # raise
        # df = df.replace({
        #     'CumulativeEffectOfChanges': 'CumulativeEffectOfChangesInAccountingPrinciple',
        #     'IncomeAfterTax': 'IncomeAfterTaxes',
        # })
        map = {
            'AccountsPayable': 'accounts_payable',
            'AmortizationExpense': 'amortization_expense',
            'AmountDueToRelatedParties': 'amount_due_to_related_parties',
            'CashBalancesBeginningOfPeriod': 'cash_balances_beginning_of_period',
            'CashBalancesEndOfPeriod': 'cash_balances_end_of_period',
            'CashBalancesIncrease': 'cash_balances_increase',
            'CashFlowsFromOperatingActivities': 'cash_flows_from_operating_activities',
            'CashFlowsProvidedFromFinancingActivities': 'cash_flows_provided_from_financing_activities',
            'CashProvidedByInvestingActivities': 'cash_provided_by_investing_activities',
            'CashReceivedThroughOperations': 'cash_received_through_operations',
            'DecreaseInDepositDeposit': 'decrease_in_deposit_deposit',
            'DecreaseInShortTermLoans': 'decrease_in_short_term_loans',
            'Depreciation': 'depreciation',
            'HedgingFinancialLiabilities': 'hedging_financial_liabilities',
            'IncomeBeforeIncomeTaxFromContinuingOperations': 'income_before_income_tax_from_continuing_operations',
            'InterestExpense': 'interest_expense',
            'InterestIncome': 'interest_income',
            'InventoryIncrease': 'inventory_increase',
            'NetIncomeBeforeTax': 'net_income_before_tax',
            'OtherNonCurrentLiabilitiesIncrease': 'other_non_current_liabilities_increase',
            'PayTheInterest': 'pay_the_interest',
            'ProceedsFromLongTermDebt': 'proceeds_from_long_term_debt',
            'PropertyAndPlantAndEquipment': 'property_and_plant_and_equipment',
            'RealizedGain': 'realized_gain',
            'ReceivableIncrease': 'receivable_increase',
            'RedemptionOfBonds': 'redemption_of_bonds',
            'RentalPrincipalRepayments': 'rental_principal_repayments',
            'RepaymentOfLongTermDebt': 'repayment_of_long_term_debt',
            'TotalIncomeLossItems': 'total_income_loss_items',
            'UnrealizedGain': 'unrealized_gain',
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
            # if 'unrealized_gain' in col:
            #     print(row['value'])
            #     raise
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
        new_df = new_df.replace({np.nan: None}).fillna('')
        # print(new_df, )
        # print(new_df.head())
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
                urljoin(getenv('SERVER_URL'), 'composite/cash_flow/'), json=body, timeout=timeout)
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
            raise Exception('unkown error, plz fix.')
        # raise
        sleep(2)
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

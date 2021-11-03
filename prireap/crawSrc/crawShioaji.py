import shioaji as sj
import json
import pandas as pd
from dotenv import load_dotenv
import os

'''
already dead https://github.com/Sinotrade/Shioaji
'''

load_dotenv()

# with open('../.key.config.json') as f:
#     data = json.load(f)['ca']

api = sj.Shioaji()

accounts = api.login( os.getenv('SJ_PERSON_ID'), os.getenv('SJ_API_PWD'))
api.activate_ca(
    #take time to block at here, don't repeatly login
    ca_path='../'+os.getenv('SJ_PATH'),
    ca_passwd=os.getenv('SJ_PWD'),
    person_id=os.getenv('SJ_PERSON_ID'),
)

# streaming, wait and block to get data
# api.quote.subscribe(
#     api.Contracts.Stocks["2330"], 
#     quote_type = sj.constant.QuoteType.Tick, # or 'tick'
#     version = sj.constant.QuoteVersion.v1 # or 'v1'
# )


#======================================historical ticks========================================
# historical ticks
# ticks = api.ticks(
#     contract=api.Contracts.Stocks["2330"], 
#     date="2020-03-04", 
#     query_type=sj.constant.TicksQueryType.RangeTime,
#     time_start="09:00:00",
#     time_end="09:20:01"
# )
# # print(ticks)

#======================================historical kbar==========================================
# historical kbar
print('getting data....')
kbars = api.kbars(api.Contracts.Stocks["2330"], start="2019-09-01", end="2019-09-01")
df = pd.DataFrame({**kbars})
df.ts = pd.to_datetime(df.ts)
print(df)
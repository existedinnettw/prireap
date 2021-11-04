import requests
from dotenv import load_dotenv
from os import getenv
load_dotenv()
from FinMind.data import DataLoader



url = "https://api.finmindtrade.com/api/v4/login"
parload = {
    "user_id": getenv('FM_USER_ID'),
    "password": getenv('FM_PWD'),
}
data = requests.post(url, data=parload)
data = data.json()
print(data) #msg, status, token
token=data['token']

api = DataLoader()
api.login_by_token(api_token=token)
# api.login(user_id='user_id',password='password')
df = api.taiwan_stock_daily(
    stock_id='2330',
    start_date='2000-01-01',
    end_date='2020-04-12'
)
print(df)
'''
trading_volume: 成交股數
Trading_money：成交金額

'''

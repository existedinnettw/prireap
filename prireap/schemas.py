from typing import List, Optional
import datetime
from pydantic import BaseModel





class StockKBarCreate(BaseModel):
    '''
    suitable for StockKMin, StockKHour, StockKDay
    '''
    start_ts: datetime.datetime
    # interval: int
    volume :int
    turnover :int
    open : float
    high : float
    low : float
    close = float
    n_deals = int
    dividends = int
    stock_splits = int
    class Config:
        orm_mode=True

class StockKBar(BaseModel):
    id : int
    stock_id: int


class StockCreate(BaseModel):
    '''
    contain business logic only, no structure data.
    '''
    symbol:str
    class Config:
        orm_mode=True
class Stock(StockCreate):
    exchange_id: int
    id:int
# class stockQuery(BaseModel):
#     code_name: Optional[str]= "TPE"
#     symbols: str
#     class Config:
#         orm_mode=True

class ExchangeCreate(BaseModel):
    name: str
    code_name: str
    class Config:
        orm_mode=True
class Exchange(ExchangeCreate):
    id:int
    stocks:List[Stock]
class ExchangeResponse(ExchangeCreate):
    id:int

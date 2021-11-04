from typing import List, Optional
import datetime
from pydantic import BaseModel
from decimal import Decimal
from enum import Enum, auto


class Interval(str, Enum):
    min = 'min'  # min1?
    hour = 'hour'
    day = 'day'


class StockKBarBase(BaseModel):
    '''
    suitable for StockKMin, StockKHour, StockKDay
    '''
    stock_id: int
    start_ts: datetime.datetime

    open: Optional[Decimal] = None
    high: Optional[Decimal] = None
    low: Optional[Decimal] = None
    close: Optional[Decimal] = None
    volume: Optional[int] = None

    transaction: Optional[int] = None
    dividends: Optional[int] = None
    stock_splits: Optional[int] = None

    class Config:
        orm_mode = True


class StockKBarCreate(StockKBarBase):
    interval: Interval = Interval.day

# delattr(class, field_name)


class StockKBar(StockKBarBase):
    id: int


class StockCreate(BaseModel):
    '''
    contain business logic only, no structure data.
    '''
    exchange_id: int
    symbol: str
    name: Optional[str] = None

    class Config:
        orm_mode = True


class Stock(StockCreate):
    id: int
# class stockQuery(BaseModel):
#     code_name: Optional[str]= "TPE"
#     symbols: str
#     class Config:
#         orm_mode=True


class ExchangeCreate(BaseModel):
    name: str
    code_name: str
    strt_cron_utc: Optional[str] = None
    end_cron_utc: Optional[str] = None

    class Config:
        orm_mode = True


class Exchange(ExchangeCreate):
    id: int
    stocks: List[Stock]


class ExchangeResponse(ExchangeCreate):
    id: int

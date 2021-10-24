from sqlalchemy.orm import Session
# from sqlalchemy import or_, and_
from . import models, schemas
from typing import List, Optional, Callable
from datetime import datetime

# =============================exchages==========================================
def get_exchanges(db: Session):
    '''
    TODO: query.with_entities?
    fastapi 給的範例是全部(itmes)都會顯示
    '''
    return db.query(models.Exchange).all()


def get_exchange(db: Session, exchange_id: int):
    return db.query(models.Exchange).filter(models.Exchange.id == exchange_id).first()


def get_exchange_by_code_name(db: Session, code_names: Optional[List[str]] = None):
    return db.query(models.Exchange).filter(models.Exchange.code_name.in_(code_names)).all()


def delete_exchange(db: Session, exchange_id: int):
    db_exg = db.query(models.Exchange).filter(
        models.Exchange.id == exchange_id).first()
    db.delete(db_exg)
    db.commit()
    return


def create_exchange(db: Session, exchange: schemas.ExchangeCreate):
    # print(exchange)
    db_exchange = models.Exchange(**exchange.dict())
    db.add(db_exchange)
    db.commit()
    db.refresh(db_exchange)
    return db_exchange


def create_exchange_stock(db: Session, exchange_id: int, stock: schemas.StockCreate):
    # print("stock:",stock)
    # print("exchnage_id:",exchange_id)
    '''
    not need, actually, use create_stock directly
    '''
    db_stock = models.Stock(**stock.dict(), exchange_id=exchange_id)
    db.add(db_stock)
    db.commit()
    db.refresh(db_stock)
    return db_stock


def create_exchange_stocks(db: Session, exchange_id: int, stocks: List[schemas.StockCreate]):
    db_stocks = [models.Stock(**i.dict(), exchange_id=exchange_id)
                 for i in stocks]
    db.add_all(db_stocks)  # this use for loop of add
    db.commit()
    [db.refresh(i) for i in db_stocks]
    # rst=db.refresh(db_stocks)
    return db_stocks

# ========================stocks==================================================


def get_stock(db: Session, stock_id: int):
    return db.query(models.Stock).filter(models.Stock.id == stock_id).first()


def get_stock_by_exg_and_symbol(db: Session, exg_id: int, symbol: str):
    return db.query(models.Stock).filter((models.Stock.exchange_id == exg_id) & (models.Stock.symbol == symbol)).first()


def get_stocks(db: Session):
    return db.query(models.Stock).filter(True).all()  # this work


def crit_in_with_check_none(func: Callable, list: Optional[List[str]] = None):
    '''
    this simple function patch check none function for "in_" criteria
    '''
    if list == None:
        return True
    else:
        return func(list)


def get_stocks_by_symbols(db: Session, symbol_list: Optional[List[str]] = None, exchange_list: Optional[List[int]] = None):
    return db.query(models.Stock).filter(crit_in_with_check_none(models.Stock.symbol.in_, symbol_list),
                                         crit_in_with_check_none(models.Stock.exchange_id.in_,exchange_list)).all()


def create_stock(db: Session, stock: schemas.StockCreate):
    db_stock = models.Stock(**stock.dict())
    db.add(db_stock)
    db.commit()
    db.refresh(db_stock)
    return db_stock

# def create_stocks(db:Session, stocks:List[schemas.StockCreate]):
#     db_stocks= models.Stock(**stocks.dict())
#     db.add_all(db_stocks)
#     db.commit()
#     db.refresh(db_stocks)
#     return db_stocks


# =============================stockKMins=================================
#db:Session, stock_id_li=List[int]
def get_stockKMins(db: Session):
    return db.query(models.StockKMin).all()
#def get_stocks(db: Session):
    # return db.query(models.Stock).filter(True).all()  # this work

def get_stockKMin(db: Session, kmin_id: int):
    return db.query(models.StockKMin).filter(models.StockKMin.id == kmin_id).first()

def get_stockKMin_by_stock_and_start(db:Session, stock_id:int, start:datetime):
    return db.query(models.StockKMin).filter(models.StockKMin.stock_id==stock_id, models.StockKMin.start_ts==start).first()

def create_stockKMin(db: Session, stockKBar: schemas.StockKBarCreate):
    db_stockKBar = models.StockKMin(**stockKBar.dict())
    db.add(db_stockKBar)
    db.commit()
    db.refresh(db_stockKBar)
    return db_stockKBar
    # db_stock = models.Stock(**stock.dict())
    # db.add(db_stock)
    # db.commit()
    # db.refresh(db_stock)
    # return db_stock

def create_stockKMins(db: Session, stockKBar: List[schemas.StockKBarCreate]):
    db_stockKBars = models.StockKMin(**stockKBar.dict())
    db.add_all(db_stockKBars)
    db.commit()
    db.refresh(db_stockKBars)
    return db_stockKBars

# ==========================stockKHours===================================


def get_stocks_stockKHours(db: Session, stock_id_li=List[int]):
    return


def get_stocks_stockKDays(db: Session, stock_id_li=List[int]):
    return

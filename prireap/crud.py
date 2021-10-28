from sqlalchemy.orm import Session
# from sqlalchemy import or_, and_
from . import models, schemas
from typing import List, Optional, Callable
from datetime import datetime, timedelta

'''
改成一個資料夾，裡面有分開的crud?
'''

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

def modify_exchange(db:Session, exchange_id: int, exchange:schemas.ExchangeCreate):
    db_exchange = models.Exchange(**exchange.dict())
    print(db_exchange,'\n\n*\n', exchange, exchange.dict())
    db.query(models.Exchange).filter(models.Exchange.id==exchange_id).update(exchange.dict())
    db.commit()
    return 


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


def crit_in_with_check_none(func: Callable, crit_obj):
    '''
    this simple function patch check none function for "in_" criteria
    crit_obj: could be 1.list, 2.any single value e.g. int, str, float...
    '''
    if crit_obj == None:
        return True
    else:
        return func(crit_obj)


def get_stocks_by_symbols(db: Session, symbol_list: Optional[List[str]] = None, exchange_list: Optional[List[int]] = None):
    return db.query(models.Stock).filter(crit_in_with_check_none(models.Stock.symbol.in_, symbol_list),
                                         crit_in_with_check_none(models.Stock.exchange_id.in_, exchange_list)).all()


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
# db:Session, stock_id_li=List[int]
def get_stockKMins_with_filter(db: Session, stock_ids: Optional[List[int]] = None, start: datetime = None, end: datetime = None):
    '''
    '''
    # print('fff:', crit_in_with_check_none(
    #     models.StockKMin.start_ts.__ge__, start), '\n\n\n')
    # print('fff:', start, '\n\n\n')
    # print(models.StockKMin.stock_id.in_(stock_ids))
    if end != None:
        end -= timedelta(minutes=1)
        # print('fff:', end, '\n\n\n')
    return db.query(models.StockKMin).filter(
        crit_in_with_check_none(models.StockKMin.start_ts.__ge__, start),
        # nonetype can't delete
        crit_in_with_check_none(models.StockKMin.start_ts.__lt__, end),
        # models.StockKMin.start_ts >= start,
        crit_in_with_check_none(models.StockKMin.stock_id.in_, stock_ids)
    ).all()


def get_stockKMin(db: Session, kmin_id: int):
    return db.query(models.StockKMin).filter(models.StockKMin.id == kmin_id).first()


def get_stockKMin_by_stock_and_start(db: Session, stock_id: int, start: datetime):
    '''
    for any stockKMin, its stock id and start_ts should be unique, so we can query specific record by this, rather than by id.
    '''
    return db.query(models.StockKMin).filter(models.StockKMin.stock_id == stock_id, models.StockKMin.start_ts == start).first()


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
    '''
    not yet used
    '''
    db_stockKBars = models.StockKMin(**stockKBar.dict())
    db.add_all(db_stockKBars)
    db.commit()
    db.refresh(db_stockKBars)
    return db_stockKBars

# ==========================stockKHours===================================


def get_stockKHours_with_filter(db: Session, stock_ids: Optional[List[int]] = None, start: datetime = None, end: datetime = None):
    '''
    '''
    st_of_end=None
    if end != None:
        st_of_end = end-timedelta(hours=1)+timedelta(microseconds=1)
    print(stock_ids, start, end)
    return db.query(models.StockKHour).filter(
        crit_in_with_check_none(models.StockKHour.start_ts.__ge__, start),
        crit_in_with_check_none(models.StockKHour.start_ts.__lt__, st_of_end),
        crit_in_with_check_none(models.StockKHour.stock_id.in_, stock_ids)
    ).all()


def get_stockKHour(db: Session, khour_id: int):
    return db.query(models.StockKHour).filter(models.StockKHour.id == khour_id).first()


def get_stockKHour_by_stock_and_start(db: Session, stock_id: int, start: datetime):
    '''
    use id+start time to search rather than id
    '''
    return db.query(models.StockKHour).filter(models.StockKHour.stock_id == stock_id, models.StockKHour.start_ts == start).first()


def create_stockKHour(db: Session, stockKBar: schemas.StockKBarCreate):
    db_stockKBar = models.StockKHour(**stockKBar.dict())
    db.add(db_stockKBar)
    db.commit()
    db.refresh(db_stockKBar)
    return db_stockKBar


def create_stockKHours(db: Session, stockKBar: List[schemas.StockKBarCreate]):
    '''
    not yet used
    '''
    db_stockKBars = models.StockKHour(**stockKBar.dict())
    db.add_all(db_stockKBars)
    db.commit()
    db.refresh(db_stockKBars)
    return db_stockKBars

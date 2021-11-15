from sqlalchemy.orm import Session
# from starlette.responses import JSONResponse
# from sqlalchemy import or_, and_
from . import models, schemas
from typing import List, Optional, Callable
from datetime import datetime, timedelta
import pandas as pd
from sqlalchemy.dialects import postgresql
now = datetime.now

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


def modify_exchange(db: Session, exchange_id: int, exchange: schemas.ExchangeCreate):
    db_exchange = models.Exchange(**exchange.dict())
    # print(db_exchange, '\n\n*\n', exchange, exchange.dict())
    db.query(models.Exchange).filter(
        models.Exchange.id == exchange_id).update(exchange.dict())
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


def create_stockKMin(db: Session, stockKBar: schemas.StockKBarBase):
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


def create_stockKMins(db: Session, stockKBar: List[schemas.StockKBarBase]):
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
    st_of_end = None
    if end != None:
        st_of_end = end-timedelta(hours=1)+timedelta(microseconds=1)
    # print(stock_ids, start, end)
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


def create_stockKHour(db: Session, stockKBar: schemas.StockKBarBase):
    db_stockKBar = models.StockKHour(**stockKBar.dict())
    db.add(db_stockKBar)
    db.commit()
    db.refresh(db_stockKBar)
    return db_stockKBar


def create_stockKHours(db: Session, stockKBar: List[schemas.StockKBarBase]):
    '''
    not yet used
    '''
    db_stockKBars = models.StockKHour(**stockKBar.dict())
    db.add_all(db_stockKBars)
    db.commit()
    db.refresh(db_stockKBars)
    return db_stockKBars

# ==========================stockKDays===================================


# def get_stockKDays_with_filter(db: Session, stock_ids: Optional[List[int]] = None, start: datetime = None, end: datetime = None):
#     '''
#     https://stackoverflow.com/questions/34322471/sqlalchemy-engine-connection-and-session-difference
#     https://docs.sqlalchemy.org/en/14/orm/session_api.html#sqlalchemy.orm.Session
#     '''
#     st_of_end = None
#     if end != None:
#         st_of_end = end-timedelta(hours=1)+timedelta(microseconds=1)
#     con=db.connection().connection #from session back to lower level(no orm). #sqlalchemy.pool.base._ConnectionFairy
#     print('start sqlalchemy query')
#     query_obj= db.query(models.StockKDay).filter(
#         crit_in_with_check_none(models.StockKDay.start_ts.__ge__, start),
#         crit_in_with_check_none(models.StockKDay.start_ts.__lt__, st_of_end),
#         crit_in_with_check_none(models.StockKDay.stock_id.in_, stock_ids)
#     )
#     stmt=str(query_obj.statement.compile(compile_kwargs={"literal_binds": True}))
#     print('type:',type(con))
#     pd_kbars=pd.read_sql(stmt,con=con)
#     print('finish db query')
#     return pd_kbars

    # pd_kbars=rawCrud.get_stockKDays_with_filter(db, start=from_ts, stock_ids=stock_ids, end=to_ts)
    # print('finish getting')
    # json=pd_kbars.to_json(orient="records") # need to be response type
    # return JSONDataResponse(content=json)

def rows_to_dict(cursor, rows):
    description=[i.name for i in cursor.description]
    list_of_dicts = [{description[j]:row[j] for j in range(len(row))} for row in rows]
    return list_of_dicts

def get_stockKDays_with_filter(db: Session, stock_ids: Optional[List[int]] = None, start: datetime = None, end: datetime = None):
    st_of_end = None
    if end != None:
        st_of_end = end-timedelta(hours=1)+timedelta(microseconds=1)

    
    con=db.connection().connection #from session back to lower level(no orm). #sqlalchemy.pool.base._ConnectionFairy
    cursor=con.cursor()
    print('start sqlalchemy query')
    query_obj= db.query(models.StockKDay).filter(
        crit_in_with_check_none(models.StockKDay.start_ts.__ge__, start),
        crit_in_with_check_none(models.StockKDay.start_ts.__lt__, st_of_end),
        crit_in_with_check_none(models.StockKDay.stock_id.in_, stock_ids)
    )
    stmt=str(query_obj.statement.compile(compile_kwargs={"literal_binds": True}))
    ts=now()

    cursor.execute(stmt)
    rows = cursor.fetchall()
    tf=now()
    print('finish db query', tf-ts)

    list_of_dicts=rows_to_dict(cursor, rows)
    td=now()
    print('finish to dict', td-tf)
    return list_of_dicts

def get_stockKDay(db: Session, kday_id: int):
    return db.query(models.StockKDay).filter(models.StockKDay.id == kday_id).first()


def get_stockKDay_by_stock_and_start(db: Session, stock_id: int, start: datetime):
    '''
    use id+start time to search rather than id
    '''
    return db.query(models.StockKDay).filter(models.StockKDay.stock_id == stock_id, models.StockKDay.start_ts == start).first()


def create_stockKDay(db: Session, stockKBar: schemas.StockKBarBase):

    db_stockKBar = models.StockKDay(**stockKBar.dict())
    db.add(db_stockKBar)
    db.commit()
    db.refresh(db_stockKBar)
    return db_stockKBar


def list_kdays_dupli(db: Session, stockKBars: schemas.List[schemas.StockKBarCreate]):
    dupli_kdays=[]
    for i in stockKBars:
        db_kbar=get_stockKDay_by_stock_and_start(db=db, stock_id=i.stock_id, start=i.start_ts) #too slow
        if db_kbar:
            dupli_kdays.append({'stock_id':i.stock_id,'start_ts':i.start_ts})
        # print('fin one check')

    return dupli_kdays
            


def create_stockKDays(db: Session, stockKBars: List[schemas.StockCreate]):
    '''
    可以用transaction
    https://stackoverflow.com/questions/34322471/sqlalchemy-engine-connection-and-session-difference
    '''
    db_stockKBars = [models.StockKDay(**i.dict()) for i in stockKBars]
    db.add_all(db_stockKBars)  # this use for loop of add
    db.commit()
    [db.refresh(i) for i in db_stockKBars]
    # rst=db.refresh(db_stockKBars)
    return db_stockKBars


def delete_kday(db: Session, kday_id: int):
    db_kday = db.query(models.StockKDay).filter(
        models.StockKDay.id == kday_id).first()
    db.delete(db_kday)
    db.commit()
    return


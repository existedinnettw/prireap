from sqlalchemy.orm import Session
from . import models, schemas
from typing import List, Optional


#=============================exchages==========================================
def get_exchanges(db:Session):
    '''
    TODO: query.with_entities?
    fastapi 給的範例是全部(itmes)都會顯示
    '''
    return db.query(models.Exchange).all()
def get_exchange(db:Session, exchange_id:int ):
    return db.query(models.Exchange).filter(models.Exchange.id==exchange_id).first()
def get_exchange_by_code_name(db:Session, code_name:str):
    return db.query(models.Exchange).filter(models.Exchange.code_name==code_name.upper()).first()

def delete_exchange_by_code_name(db:Session, code_name:str):
    db_exg = db.query(models.Exchange).filter(models.Exchange.code_name==code_name.upper()).first()
    db.delete(db_exg)
    db.commit()
    return 

def create_exchange(db:Session, exchange:schemas.ExchangeCreate ):
    # print(exchange)
    db_exchange= models.Exchange(**exchange.dict())
    db.add(db_exchange)
    db.commit()
    db.refresh(db_exchange)
    return db_exchange

def create_stocks_exchange(db:Session, exchange_id:int, stock:schemas.StockCreate):
    print("stock:",stock)
    print("exchnage_id:",exchange_id)
    db_stock = models.Stock(**stock.dict(), exchange_id=exchange_id)
    db.add(db_stock)
    db.commit()
    db.refresh(db_stock)
    return db_stock

#========================stocks==================================================
def create_stock(db:Session, stock:schemas.StockCreate):
    db_stock= models.Stock(**stock.dict())
    db.add(db_stock)
    db.commit()
    db.refresh(db_stock)
    return db_stock

def create_stocks(db:Session, stocks:List[schemas.StockCreate]):
    db_stocks= models.Stock(**stocks.dict())
    db.add_all(db_stocks)
    db.commit()
    db.refresh(db_stocks)
    return db_stocks

def get_stocks_stockKMins(db:Session, stock_id_li=List[int] ):
    return db.query(models.StockKMin).filter(models.Exchange.id.in_(stock_id_li))

def create_stockKMins(db:Session, stockKBar:List[schemas.StockKBarCreate]):
    db_stockKBars= models.StockKMin(**stockKBar.dict())
    db.add_all(db_stockKBars)
    db.commit()
    db.refresh(db_stockKBars)
    return db_stockKBars

def get_stocks_stockKHours(db:Session, stock_id_li=List[int] ):
    return

def get_stocks_stockKDays(db:Session, stock_id_li=List[int] ):
    return
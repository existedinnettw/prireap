from fastapi import APIRouter, Depends, HTTPException, status, Query
from .. import schemas, crud, models
from ..dependencies import get_db
from typing import List, Optional
from sqlalchemy.orm import Session

router = APIRouter(
    tags=["stocks"],
    # responses={404: {"description": "Not found"}},
)


@router.get(
    "/stocks/",
    response_model=List[schemas.Stock]
)
def get_stocks(db: Session = Depends(get_db),
               symbols: Optional[List[str]] = Query(None),
               exchanges: Optional[List[int]] = Query(None)):
    '''
    會列出所有exchange的所有stocks
    更常用的是filter by symbol
    TODO: 如何處理 單一symbol, exchange_id 和 多個symbol, exchange_id 還有 None？
        目前是直接把有給的就直接加入 in list filter
    '''
    db_stocks = []
    # if symbols:
    #     db_stocks = crud.get_stocks_by_symbols(db, symbol_list=symbols)
    # else:
    #     db_stocks = crud.get_stocks(db)
    db_stocks = crud.get_stocks_by_symbols(
        db, symbol_list=symbols, exchange_list=exchanges)
    # print('this is db stocks:',db_stocks, '\n\n\n')
    return db_stocks


@router.get(
    "/stocks/{stock_id}",
    response_model=schemas.Stock
)
def get_stock_by_id(stock_id: int, db: Session = Depends(get_db)):
    db_stock = crud.get_stock(db, stock_id)
    if db_stock is None:
        raise HTTPException(status_code=404, detail="stock not found")
    return db_stock


@router.post(
    "/stocks/",
    response_model=schemas.Stock
)
def create_stock(stock_create: schemas.StockCreate, db: Session = Depends(get_db)):
    '''
    similar to create_exchange_stock
    '''
    db_exg = crud.get_exchange(db, stock_create.exchange_id)
    if not db_exg:
        raise HTTPException(
            status_code=404, detail="exchanger not exist, create exchange first")
    db_stock = crud.get_stock_by_exg_and_symbol(
        db, exg_id=stock_create.exchange_id, symbol=stock_create.symbol)
    if db_stock:
        raise HTTPException(status_code=400, detail="stock already exist")
    return crud.create_stock(db=db, stock=stock_create)

# @router.delete(
#     "/stocks/{code_name}",
#     status_code=status.HTTP_204_NO_CONTENT
# )
# def delete_exchange(code_name:str, db:Session=Depends(get_db)):
#     db_exg = crud.get_exchange_by_code_name(db, code_name)
#     if not db_exg:
#         raise HTTPException(status_code=400, detail="exchanger not yet exist")
#     if db_exg.stocks:
#         raise HTTPException(status_code=403, detail="exchanger still contain stocks")
#     return crud.delete_exchange_by_code_name(db=db, code_name=code_name)

@router.post(
     "/composite/stocks/",
     response_model=List[schemas.Stock]
)
def create_stocks():
    '''
    not implement yet, don't use
    '''
    raise NotImplementedError
    return


# @router.post(
#     "/stocks/{stock_id}/kmins",
#     response_model=schemas.StockKBar
# )
# def create_stockKmins_for_stocks(stock_id:int, stock:schemas.StockCreate, db:Session=Depends(get_db)):
#     '''
#     有點問題，stocks 底下有Kmins, Khours, ...，如何知道是誰？
#     query 的schemas 直接加上interval 如何? <--那db分開的意義？ <--db是為了可能用算的就達到hr，本就沒必要一樣
#     不然直接在 Kmins level 去做create。
#     '''
#     # rst= crud.create_exchange_stock(db, exchange_id=exchange_id, stock=stock)
#     # return rst
#     pass

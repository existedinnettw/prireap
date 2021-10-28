from fastapi import APIRouter, Depends, HTTPException, status, Query
from .. import schemas, crud, models
from ..dependencies import get_db
from typing import List, Optional
from sqlalchemy.orm import Session

router = APIRouter(
    tags=["exchanges"],
    # responses={404: {"description": "Not found"}},
)


@router.get(
    "/exchanges/",
    response_model=List[schemas.ExchangeResponse]  # schemas.Exchange
)
def get_exchanges(db: Session = Depends(get_db), code_names: Optional[List[str]] = Query(None)):
    '''
    得到所有exchanges，目前不顯示stocks
    '''
    db_exg = []
    if code_names:
        db_exg = crud.get_exchange_by_code_name(db, code_names)
    else:
        db_exg = crud.get_exchanges(db)
    return db_exg


@router.get(
    "/exchanges/{exchange_id}",
    response_model=schemas.Exchange
)
def get_exchange_by_id(exchange_id: int, db: Session = Depends(get_db)):
    db_exg = crud.get_exchange(db, exchange_id)
    if db_exg is None:
        raise HTTPException(status_code=404, detail="exchange not found")
    return db_exg


@router.post(
    "/exchanges/",
    response_model=schemas.Exchange
)
def create_exchange(exg_create: schemas.ExchangeCreate, db: Session = Depends(get_db)):
    db_exg = crud.get_exchange_by_code_name(db, exg_create.code_name)
    if db_exg:
        raise HTTPException(status_code=400, detail="exchanger already exist")
    return crud.create_exchange(db=db, exchange=exg_create)

@router.put(
    "/exchanges/{exchange_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def modify_exchange(exchange_id:int, exg_create:schemas.ExchangeCreate, db:Session=Depends(get_db)):
    db_exg = crud.get_exchange(db, exchange_id)
    if not db_exg:
        raise HTTPException(status_code=400, detail="exchanger not yet exist")
    crud.modify_exchange(db, exchange_id=exchange_id, exchange=exg_create)


@router.delete(
    "/exchanges/{exchange_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_exchange(exchange_id: int, db: Session = Depends(get_db)):
    '''
    應該用exchange id 而非code_name
    '''
    db_exg = crud.get_exchange(db, exchange_id)
    if not db_exg:
        raise HTTPException(status_code=400, detail="exchanger not yet exist")
    if db_exg.stocks[0]:
        raise HTTPException(
            status_code=403, detail="exchanger still contain stocks")
    return crud.delete_exchange(db=db, exchange_id=exchange_id)


@router.post(
    "/exchanges/{exchange_id}/stocks",
    response_model=schemas.Stock
)
def create_stock_for_exchange(exchange_id: int, stock: schemas.StockCreate, db: Session = Depends(get_db)):
    rst = crud.create_exchange_stock(db, exchange_id=exchange_id, stock=stock)
    return rst


@router.post(
    "/composite/exchanges/{exchange_id}/stocks",
    response_model=List[schemas.Stock]
)
def create_stocks_for_exchange(exchange_id:int, stocks:List[schemas.StockCreate], db:Session=Depends(get_db)):
    '''
    TODO: check first
    '''
    rst= crud.create_exchange_stocks(db, exchange_id=exchange_id, stocks=stocks)
    # print("rst:",rst,'\n\n')
    return rst
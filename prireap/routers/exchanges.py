from fastapi import APIRouter, Depends, HTTPException, status
from .. import schemas, crud, models
from ..dependencies import get_db
from typing import List, Optional
from sqlalchemy.orm import Session

router = APIRouter(
    prefix="/exchanges",
    tags=["exchanges"],
    # responses={404: {"description": "Not found"}},
)


@router.get(
    "/",
    response_model=List[schemas.ExchangeResponse] #schemas.Exchange
)
def get_exchanges(db:Session=Depends(get_db)):
    '''
    得到所有exchanges，目前不顯示stocks
    '''
    db_exg = crud.get_exchanges(db)
    return db_exg
@router.get(
    "/{exchange_id}",
    response_model=schemas.Exchange
)
def get_exchange_by_id(exchange_id:int, db:Session=Depends(get_db)):
    db_exg = crud.get_exchange(db, exchange_id)
    if db_exg is None:
        raise HTTPException(status_code=404, detail="exchange not found")
    return db_exg
# @router.get(
#     "/{code_name}",
#     response_model=schemas.Exchange
# )
# def get_exchange_by_code_name(code_name:str, db:Session=Depends(get_db)):
#     '''
#     按照正統的restful api 似乎不能用id以外的東西
#     '''
#     db_exg = crud.get_exchange_by_code_name(db, code_name)
#     if db_exg is None:
#         raise HTTPException(status_code=404, detail="exchange not found")
#     return db_exg

@router.post(
    "/",
    response_model=schemas.Exchange
)
def create_exchange(exg_create:schemas.ExchangeCreate, db: Session = Depends(get_db)):
    db_exg = crud.get_exchange_by_code_name(db, exg_create.code_name)
    if db_exg:
        raise HTTPException(status_code=400, detail="exchanger already exist")
    return crud.create_exchange(db=db, exchange=exg_create)
@router.delete(
    "/{code_name}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_exchange(code_name:str, db:Session=Depends(get_db)):
    db_exg = crud.get_exchange_by_code_name(db, code_name)
    if not db_exg:
        raise HTTPException(status_code=400, detail="exchanger not yet exist")
    if db_exg.stocks:
        raise HTTPException(status_code=403, detail="exchanger still contain stocks")
    return crud.delete_exchange_by_code_name(db=db, code_name=code_name)

@router.post(
    "/{exchange_id}/stocks",
    response_model=schemas.Stock
)
def create_stock_for_exchange(exchange_id:int, stock:schemas.StockCreate, db:Session=Depends(get_db)):
    rst= crud.create_stocks_exchange(db, exchange_id=exchange_id, stock=stock)
    return rst

# @router.post(
#     "/composite/{}"
# )
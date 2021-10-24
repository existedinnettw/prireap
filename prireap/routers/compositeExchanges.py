from fastapi import APIRouter, Depends, HTTPException, status
from .. import schemas, crud, models
from ..dependencies import get_db
from typing import List, Optional
from sqlalchemy.orm import Session

router = APIRouter(
    prefix="/composite/exchanges",
    tags=["exchanges"],
    # responses={404: {"description": "Not found"}},
)

@router.post(
    "/{exchange_id}/stocks",
    response_model=List[schemas.Stock]
)
def create_stocks_for_exchange(exchange_id:int, stocks:List[schemas.StockCreate], db:Session=Depends(get_db)):
    '''
    TODO: check first
    '''
    rst= crud.create_exchange_stocks(db, exchange_id=exchange_id, stocks=stocks)
    # print("rst:",rst,'\n\n')
    return rst
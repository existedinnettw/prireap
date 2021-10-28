from fastapi import APIRouter, Depends, HTTPException, status, Query
from .. import schemas, crud, models
from ..dependencies import get_db
from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime

router = APIRouter(
    tags=["kmins"],
    # responses={404: {"description": "Not found"}},
)


@router.get(
    "/kmins/",
    response_model=List[schemas.StockKBar]
)
def get_kmins(from_ts: Optional[datetime] = Query(None),
              to_ts: Optional[datetime] = Query(None),
              stock_ids: List[Optional[int]] = Query(None),
              db: Session = Depends(get_db)):
    '''
    搭配query parameter 很有用
    stock_ids: array?
    '''
    db_kmins = []
    db_kmins = crud.get_stockKMins_with_filter(
        db, start=from_ts, stock_ids=stock_ids, end=to_ts)
    return db_kmins


@router.get(
    "/kmins/{kmin_id}",
    response_model=schemas.StockKBar
)
def get_kmin_by_id(kmin_id: int,
                   db: Session = Depends(get_db)):
    db_kmin = crud.get_stockKMin(db, kmin_id)
    if db_kmin is None:
        raise HTTPException(status_code=404, detail="kmin not found")
    return db_kmin


@router.post(
    "/kmins/",
    response_model=schemas.StockKBar
)
def create_kmin(kmin_create: schemas.StockKBarCreate, db: Session = Depends(get_db)):
    db_stock = crud.get_stock(db, kmin_create.stock_id)
    if not db_stock:
        raise HTTPException(
            status_code=404, detail="stock not exist, create stock first")

    db_kmin = crud.get_stockKMin_by_stock_and_start(
        db, stock_id=kmin_create.stock_id, start=kmin_create.start_ts)
    if db_kmin:
        raise HTTPException(status_code=400, detail="kmin already exist")
    print(kmin_create.high, kmin_create.low, '\n\n\n')
    return crud.create_stockKMin(db=db, stockKBar=kmin_create)


@router.post(
    "/composite/kmins/",
    response_model=List[schemas.StockKBar]
)
def create_kmins():
    return
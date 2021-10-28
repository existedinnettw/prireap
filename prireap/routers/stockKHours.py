from fastapi import APIRouter, Depends, HTTPException, status, Query
from .. import schemas, crud, models
from ..dependencies import get_db
from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime

router = APIRouter(
    tags=["khours"],
    # responses={404: {"description": "Not found"}},
)


@router.get(
    "/khours/",
    response_model=List[schemas.StockKBar]
)
def get_khours(from_ts: Optional[datetime] = Query(None),
              to_ts: Optional[datetime] = Query(None),
              stock_ids: List[Optional[int]] = Query(None),
              db: Session = Depends(get_db)):
    '''
    搭配query parameter 很有用
    stock_ids: array?
    '''
    db_khours = []
    db_khours = crud.get_stockKHours_with_filter(
        db, start=from_ts, stock_ids=stock_ids, end=to_ts)
    return db_khours


@router.get(
    "/khours/{khour_id}",
    response_model=schemas.StockKBar
)
def get_khour_by_id(khour_id: int,
                   db: Session = Depends(get_db)):
    db_khour = crud.get_stockKHour(db, khour_id)
    if db_khour is None:
        raise HTTPException(status_code=404, detail="khour not found")
    return db_khour


@router.post(
    "/khours/",
    response_model=schemas.StockKBar
)
def create_khour(khour_create: schemas.StockKBarCreate, db: Session = Depends(get_db)):
    db_stock=crud.get_stock(db,khour_create.stock_id)
    if not db_stock:
        raise HTTPException(
            status_code=404, detail="stock not exist, create stock first")

    db_khour = crud.get_stockKHour_by_stock_and_start(
        db, stock_id=khour_create.stock_id, start=khour_create.start_ts )
    if db_khour:
        raise HTTPException(status_code=400, detail="khour already exist")
    print(khour_create.high, khour_create.low,'\n\n\n')
    return crud.create_stockKHour(db=db, stockKBar=khour_create)

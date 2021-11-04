'''
之所以把khour,kmin,kday合成單一kbar，是希望視kbar為單一的resouce，其interval可以隨意變成e.g. 5min, 30min...
目前不確定是不是好的design
'''

from fastapi import APIRouter, Depends, HTTPException, status, Query, Response
from .. import schemas, crud, models
from ..dependencies import get_db
from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime

router = APIRouter(
    tags=["kbars"],
    # responses={404: {"description": "Not found"}},
)


@router.get(
    "/kbars/",
    response_model=List[schemas.StockKBar]
)
def get_kbars(
        interval: schemas.Interval = Query(schemas.Interval.day),
        from_ts: Optional[datetime] = Query(None),
        to_ts: Optional[datetime] = Query(None),
        stock_ids: List[Optional[int]] = Query(None),
        db: Session = Depends(get_db)):
    '''
    搭配query parameter 很有用
    stock_ids: array?
    '''
    if interval == schemas.Interval.min:
        db_kmins = []
        db_kmins = crud.get_stockKMins_with_filter(
            db, start=from_ts, stock_ids=stock_ids, end=to_ts)
        return db_kmins
    elif interval == schemas.Interval.hour:
        db_kbars = []
        db_kbars = crud.get_stockKHours_with_filter(
            db, start=from_ts, stock_ids=stock_ids, end=to_ts)
        return db_kbars
    elif interval == schemas.Interval.day:
        db_kbars = []
        db_kbars = crud.get_stockKDays_with_filter(
            db, start=from_ts, stock_ids=stock_ids, end=to_ts)
        return db_kbars
    else:
        raise HTTPException(
            status=404, detail="unavailable query parameter:interval ")


@router.get(
    "/kbars/{kbar_id}",
    response_model=schemas.StockKBar
)
def get_kbar_by_id(
        kbar_id: int,
        interval: schemas.Interval = Query(schemas.Interval.day),
        db: Session = Depends(get_db)):
    if interval == schemas.Interval.min:
        db_kmin = crud.get_stockKMin(db, kbar_id)
        if db_kmin is None:
            raise HTTPException(status_code=404, detail="kmin not found")
        return db_kmin
    elif interval == schemas.Interval.hour:
        db_khour = crud.get_stockKHour(db, kbar_id)
        if db_khour is None:
            raise HTTPException(status_code=404, detail="khour not found")
        return db_khour
    elif interval == schemas.Interval.day:
        db_kbar = crud.get_stockKDay(db, kbar_id)
        if db_kbar is None:
            raise HTTPException(status_code=404, detail="khour not found")
        return db_kbar
    else:
        raise HTTPException(
            status=404, detail="unavailable query parameter:interval ")


@router.post(
    "/kbars/",
    response_model=schemas.StockKBar
)
def create_kbar(
        kbar_create: schemas.StockKBarCreate,
        db: Session = Depends(get_db)):
    interval = kbar_create.interval
    del kbar_create.interval

    db_stock = crud.get_stock(db, kbar_create.stock_id)
    if not db_stock:
        raise HTTPException(
            status_code=404, detail="stock not exist, create stock first")

    if interval == schemas.Interval.min:
        kmin_create = kbar_create

        db_kmin = crud.get_stockKMin_by_stock_and_start(
            db, stock_id=kmin_create.stock_id, start=kmin_create.start_ts)
        if db_kmin:
            raise HTTPException(status_code=400, detail="kmin already exist")
        # print(kmin_create.high, kmin_create.low, '\n\n\n')
        return crud.create_stockKMin(db=db, stockKBar=kmin_create)
    elif interval == schemas.Interval.hour:
        khour_create = kbar_create

        db_khour = crud.get_stockKHour_by_stock_and_start(
            db, stock_id=khour_create.stock_id, start=khour_create.start_ts)
        if db_khour:
            raise HTTPException(status_code=400, detail="khour already exist")
        # print(khour_create.high, khour_create.low, '\n\n\n')
        return crud.create_stockKHour(db=db, stockKBar=khour_create)
    elif interval == schemas.Interval.day:

        db_kbar = crud.get_stockKDay_by_stock_and_start(
            db, stock_id=kbar_create.stock_id, start=kbar_create.start_ts)
        if db_kbar:
            raise HTTPException(status_code=400, detail="kday already exist")
        # print(kbar_create.high, kbar_create.low, '\n\n\n')
        return crud.create_stockKDay(db=db, stockKBar=kbar_create)
    else:
        raise HTTPException(
            status=404, detail="unavailable query parameter:interval ")


@router.delete(
    "/kbars/{kbar_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_kbar(kbar_id: int, interval: schemas.Interval, db: Session = Depends(get_db)):  # similar to GET?
    '''
    not yet implement\n
    用query parameter 來得到interval 總覺得有點怪，這樣可行嗎?\n
    還是應該用 uuid (sqlite,mysql not support, pg support) 去查三個kbar混合起來的table?\n
    目前還是先用query parameter\n
    '''
    if interval == schemas.Interval.min:
        return
    elif interval == schemas.Interval.hour:
        return
    elif interval == schemas.Interval.day:
        crud.delete_kday(db=db, kday_id=kbar_id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    else:
        raise HTTPException(
            status=404, detail="unavailable query parameter:interval ")
    # db_exg = crud.get_exchange(db, kbar_id)
    # if not db_exg:
    #     raise HTTPException(status_code=400, detail="exchanger not yet exist")
    # if db_exg.stocks[0]:
    #     raise HTTPException(
    #         status_code=403, detail="exchanger still contain stocks")
    # return crud.delete_exchange(db=db, exchange_id=kbar_id)


@router.post(
    "/composite/kbars/",
    response_model=List[schemas.StockKBar]
)
def create_kbars():
    '''
    not yet implement
    '''
    interval = None
    if interval == schemas.Interval.min:
        return
    elif interval == schemas.Interval.hour:
        return
    elif interval == schemas.Interval.day:
        return
    else:
        raise HTTPException(
            status=404, detail="unavailable query parameter:interval ")


'''
    if interval == schemas.Interval.min:
        return
    elif interval == schemas.Interval.hour:
        return
    elif interval == schemas.Interval.day:
        return
    else:
        raise HTTPException(
            status=404, detail="unavailable query parameter:interval ")
'''

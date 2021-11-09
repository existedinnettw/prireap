'''
之所以把khour,kmin,kday合成單一kbar，是希望視kbar為單一的resouce，其interval可以隨意變成e.g. 5min, 30min...
目前不確定是不是好的design
'''

from fastapi import APIRouter, Depends, HTTPException, status, Query, Response
from fastapi.responses import JSONResponse#, ORJSONResponse
from .. import schemas, crud, models
from ..dependencies import get_db
from typing import List, Optional, Any
from sqlalchemy.orm import Session
from datetime import datetime
import collections
import orjson
import decimal

router = APIRouter(
    tags=["kbars"],
    # responses={404: {"description": "Not found"}},
)

def decimal_default(obj):
    if isinstance(obj, decimal.Decimal):
        return float(obj)
    raise TypeError

class ORJSONResponse(JSONResponse):
    media_type = "application/json"

    def render(self, content: Any) -> bytes:
        return orjson.dumps(content, default=decimal_default)


@router.get(
    "/kbars/",
    # response_model=List[schemas.StockKBar]
    # response_class=ORJSONResponse
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
        '''
        db query(1.5min, 用yield_per 之後) 和 return response(8min) 花非常多時間，特別是return
        db部份實際用sql query是10s
        return response 會那麼久我猜是花一堆時間和memory在pydantic model 上。
        現在看起來用python 做backend也是很錯誤的，任何compile language 都好
        # 改進
        * https://fastapi.tiangolo.com/advanced/response-directly/
        * https://github.com/tiangolo/fastapi/issues/788
        改完之後只要30s，大部份時間花在 to json
        '''
        db_kbars = []
        db_kbars = crud.get_stockKDays_with_filter(
            db, start=from_ts, stock_ids=stock_ids, end=to_ts) #return in db model object
        print('finish getting')
        # print(vars(db_kbars[0]))
        list_of_dicts = [ row.__dict__ for row in db_kbars]
        [ row.pop('_sa_instance_state') for row in list_of_dicts]
        print('finish to dict')
        # dictret.pop('_sa_instance_state', None)
        # print(list_of_dicts)
        json_resp = ORJSONResponse(list_of_dicts) #if use this directly, need to patch decimal stringnify 
        # # print(json_resp)
        # print('finish to json')
        return json_resp
        # return list_of_dicts
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
    # status_code=status.HTTP_204_NO_CONTENT
)
def delete_kbar(kbar_id: int, interval: schemas.Interval, db: Session = Depends(get_db)):  # similar to GET?
    '''
    用query parameter 來得到interval 總覺得有點怪，這樣可行嗎?\n
    還是應該用 uuid (sqlite,mysql not support, pg support) 去查三個kbar混合起來的table?\n
    目前還是先用query parameter\n
    '''
    if interval == schemas.Interval.min:
        raise HTTPException(status_code=500, detail="Not yet implement")
    elif interval == schemas.Interval.hour:
        raise HTTPException(status_code=500, detail="Not yet implement")
    elif interval == schemas.Interval.day:
        db_kbar = crud.get_stockKDay(kday_id=kbar_id, db=db)
        if not db_kbar:
            raise HTTPException(status_code=400, detail="kday not exist")
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


@router.delete(
    "/kbars/",
    # status_code=status.HTTP_204_NO_CONTENT
)
def delete_kbars(stock_id: int, interval: schemas.Interval, from_ts: Optional[datetime] = Query(None),
                 to_ts: Optional[datetime] = Query(None), db: Session = Depends(get_db)):  # similar to GET?
    '''
    not yet implement\n
    delete whole kbar with specific id in that interval.\n
    * 這個function刪掉大量資料也蠻慢的，證明每一次DB操作都很耗時。沒有試過synchronous 單一delete requests會多慢。
    '''
    db_stock = crud.get_stock(stock_id=stock_id, db=db)
    if not db_stock:
        raise HTTPException(
            status_code=400, detail="stock with assigned stock_id not exist")

    if interval == schemas.Interval.min:
        raise HTTPException(status_code=500, detail="Not yet implement")
    elif interval == schemas.Interval.hour:
        raise HTTPException(status_code=500, detail="Not yet implement")
    elif interval == schemas.Interval.day:
        db_kbars = crud.get_stockKDays_with_filter(
            db, start=from_ts, stock_ids=[stock_id], end=to_ts)
        for i in db_kbars:
            crud.delete_kday(db=db, kday_id=i.id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    else:
        raise HTTPException(
            status=404, detail="unavailable query parameter:interval ")


@router.post(
    "/composite/kbars/",
    response_model=List[schemas.StockKBar]
)
def create_kbars(kbar_creates: List[schemas.StockKBarCreate], db: Session = Depends(get_db)):
    '''
    not yet implement
    '''
    for i in kbar_creates:
        db_stock = crud.get_stock(db, i.stock_id)
        if not db_stock:
            raise HTTPException(
                status_code=404, detail="stock not exist, create stock first")

    interval = kbar_creates[0].interval
    if interval == schemas.Interval.min:
        return
    elif interval == schemas.Interval.hour:
        return
    elif interval == schemas.Interval.day:

        with_wrong_intervals = [
            i for i in kbar_creates if i.interval != schemas.Interval.day]
        if with_wrong_intervals:
            raise HTTPException(
                status_code=400, detail="contain wrong interval {}.".format(with_wrong_intervals))
        for i in range(len(kbar_creates)):
            del kbar_creates[i].interval

        # 要確定pass in 的本身有無重複，其中start_ts是datetime
        print('check repeat in request body')
        create_simp = [str(i.stock_id)+i.start_ts.isoformat()
                       for i in kbar_creates]
        if len(kbar_creates) != len(set(create_simp)):
            raise HTTPException(
                status_code=400, detail="duplicate in request list.")

        print('list duplicate in db') #this process stuck
        dupli_kdays = crud.list_kdays_dupli(db=db, stockKBars=kbar_creates)
        if dupli_kdays:
            # 要不要直接create沒有重複的？
            raise HTTPException(
                status_code=400, detail="following kdays already exist {}.".format(dupli_kdays))
        # print(kbar_create.high, kbar_create.low, '\n\n\n')
        print('creating')
        return crud.create_stockKDays(db=db, stockKBars=kbar_creates)

        # for i in kbar_creates:
        #     #這個方法如果中間有問題e.g.重複，前面的會直接先insert
        #     create_kbar(db=db, kbar_create=i)
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

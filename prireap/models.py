# import asyncio
from email.policy import default
import os
from dotenv import load_dotenv
from fastapi import FastAPI
from pytz import timezone
from sqlalchemy import create_engine
# numeric type contain decimal in sql
from sqlalchemy import Column, Integer, BigInteger, String, Enum, Numeric, DateTime, TIMESTAMP, Sequence, Date, Index, Float  # , Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import ForeignKey, ForeignKeyConstraint, UniqueConstraint
from sqlalchemy.orm import relationship, backref, validates, sessionmaker
from .database import Base, SessionLocal, engine

'''
TODO:
    may need alembic for migration
'''

load_dotenv()
# print(os.getenv('DBHOST'))


class Exchange(Base):
    '''
    code_name: e.g. TPE
    * crontab:
        although crontab is accept to be null, it is highly recommend to be filled to simplify program use.
        the datetime is base on UTC (without timezone).
        can add validates
    '''
    __tablename__ = 'exchange'
    id = Column(Integer, Sequence('exg_id_seq'), primary_key=True)
    name = Column(String, nullable=False, unique=True)
    code_name = Column(String, nullable=False, unique=True)
    strt_cron_utc = Column(String, nullable=True)
    end_cron_utc = Column(String, nullable=True)

    stocks = relationship("Stock", back_populates="exchange")

    @validates('code_name')
    def convert_upper(self, key, value):
        return value.upper()


class Stock(Base):
    '''
    symbol: 2330, GOOGL, APPL
    name: 台積電, 精英, apple inc
    '''
    __tablename__ = 'stock'
    id = Column(Integer, Sequence('stock_id_seq'), primary_key=True)
    symbol = Column(String, nullable=False)  # e.g. 2330, GOOGL
    name = Column(String, nullable=True)
    exchange_id = Column(Integer, ForeignKey(
        'exchange.id', onupdate="CASCADE", ondelete="RESTRICT"), nullable=False)
    exchange = relationship("Exchange", back_populates="stocks")
    # adr parent id
    UniqueConstraint('symbol', 'exchange_id', name='uq_sym_exg')

#SQL 標準中要求 timestamp 的效果等同於 timestamp without time zone，對此 PostgreSQL 尊重這個行為。
#同時 PostgreSQL 額外擴充了 timestamptz 作為 timestamp with time zone 的縮寫。
# 是不是應該存的時候沒有timezone，query時自己加?
class StockKMin(Base):
    __tablename__ = 'stock_k_min'
    id = Column(Integer, Sequence('kmin_id_seq'), primary_key=True)
    stock_id = Column(Integer, ForeignKey(
        'stock.id', onupdate="CASCADE", ondelete="RESTRICT"), nullable=False)
    start_ts = Column(TIMESTAMP(timezone=True), nullable=False)
    # interval = Column(Integer, nullable=False )
    open = Column(Numeric(scale=2), nullable=True) #０.０１元至１０元，以０.０１元為升降單位
    high = Column(Numeric(scale=2), nullable=True)
    low = Column(Numeric(scale=2), nullable=True)
    close = Column(Numeric(scale=2), nullable=True)
    volume = Column(Integer, nullable=True)
    transaction = Column(Integer, nullable=True) #transaction
    # dividends = Column(Integer, nullable=True)
    # stock_splits = Column(Integer, nullable=True)
    # UniqueConstraint('stock_id', 'start_ts', name='uq_stkm_stk_ts')
Index('kmin_stockid_startts', StockKMin.stock_id, StockKMin.start_ts, unique=True) #, unique=True
#query時，要同時指定stock_id和start_ts才有加速效果，只有指定start_ts沒用
#CREATE UNIQUE INDEX kmin_stockid_startts ON public.stock_k_min USING btree (stock_id, start_ts);

class StockKHour(Base):
    __tablename__ = 'stock_k_hr'
    id = Column(Integer, Sequence('khr_id_seq'), primary_key=True)
    stock_id = Column(Integer, ForeignKey(
        'stock.id', onupdate="CASCADE", ondelete="RESTRICT"), nullable=False)
    start_ts = Column(TIMESTAMP(timezone=True), nullable=False)
    # interval = Column(Integer, nullable=False )
    open = Column(Numeric(scale=2), nullable=True)
    high = Column(Numeric(scale=2), nullable=True)
    low = Column(Numeric(scale=2), nullable=True)
    close = Column(Numeric(scale=2), nullable=True)
    volume = Column(Integer, nullable=True)
    transaction = Column(Integer, nullable=True)
    # dividends = Column(Integer, nullable=True)
    # stock_splits = Column(Integer, nullable=True)
    # UniqueConstraint('stock_id', 'start_ts', name='uq_stkh_stk_ts') #有加 index 了
Index('khr_stockid_startts', StockKHour.stock_id, StockKHour.start_ts, unique=True) #, unique=True
#CREATE UNIQUE INDEX khr_stockid_startts ON public.stock_k_hr USING btree (stock_id, start_ts);

class StockKDay(Base):
    __tablename__ = 'stock_k_day'
    id = Column(Integer, Sequence('kday_id_seq'), primary_key=True)
    stock_id = Column(Integer, ForeignKey(
        'stock.id', onupdate="CASCADE", ondelete="RESTRICT"), nullable=False)
    start_ts = Column(TIMESTAMP(timezone=True), nullable=False) #sqlalchemy.types.Date, 會造成column type 和kmin, khour 不同
    open = Column(Numeric(scale=2), nullable=True)
    high = Column(Numeric(scale=2), nullable=True)
    low = Column(Numeric(scale=2), nullable=True)
    close = Column(Numeric(scale=2), nullable=True)
    volume = Column(Integer, nullable=True)
    transaction = Column(Integer, nullable=True)
    # dividends = Column(Integer, nullable=True)
    # stock_splits = Column(Integer, nullable=True)
    # UniqueConstraint('stock_id', 'start_ts', name='uq_stkd_stk_ts')
Index('kday_stockid_startts', StockKDay.stock_id, StockKDay.start_ts, unique=True) #, unique=True
#CREATE UNIQUE INDEX kday_stockid_startts ON public.stock_k_day USING btree (stock_id, start_ts);

class CFS(Base):
    '''
    綜合損益表
    Consolidated Financial Statements(Consolidated Income Statement)
    '''
    __tablename__='consolid_stat'
    id = Column(Integer, Sequence('cfs_id_seq'), primary_key=True)
    stock_id = Column(Integer, ForeignKey(
        'stock.id', onupdate="CASCADE", ondelete="RESTRICT"), nullable=False)
    date=Column(Date,nullable=False) #date 不支援 timezone

    adjustment_item=Column(BigInteger, nullable=True) #調整項目
    cost_of_goods_sold=Column(BigInteger, nullable=True) #營業成本
    cumulative_effect_of_changes_in_accounting_principle=Column(BigInteger, nullable=True) #累積影響數
    eps=Column(Float, nullable=True) #每股稅後盈餘(元)
    equity_attributable_to_owners_of_parent = Column(BigInteger, nullable=True) #綜合損益總額歸屬於母公司業主
    extraordinary_items=Column(BigInteger, nullable=True) #非常損益
    gross_profit=Column(BigInteger, nullable=True)  #營業毛利
    income_after_taxes=Column(BigInteger, nullable=True) #稅後純益
    income_before_income_tax=Column(BigInteger, nullable=True) #稅前利潤
    income_before_tax_from_continuing_operations=Column(BigInteger, nullable=True) # 繼續營業單位稅前淨利
    income_from_continuing_operations =Column(BigInteger, nullable=True) #繼續營業單位本期淨利（淨損）
    income_loss_from_discontinued_operation=Column(BigInteger, nullable=True) #停業部門損益
    net_income=Column(BigInteger, nullable=True) #淨利潤
    noncontrolling_interests = Column(BigInteger, nullable=True)#綜合損益總額歸屬於非控制權益
    operating_expenses=Column(BigInteger, nullable=True) #營業費用
    operating_income=Column(BigInteger, nullable=True) #營業收入淨額
    other_comprehensive_income=Column(BigInteger, nullable=True) #其他綜合損益（淨額）
    other_nonoperating_expense_or_loss=Column(BigInteger, nullable=True) # 其他收益及費損淨額(OTHNOE)
    pre_tax_income=Column(BigInteger, nullable=True) #稅前純益
    realized_gain=Column(BigInteger, nullable=True) #已實現銷貨（損）益
    realized_gain_from_inter_affiliate_accounts=Column(BigInteger, nullable=True) #聯屬公司間已實現利益淨額
    revenue=Column(BigInteger, nullable=True)# 營業收入
    tax=Column(BigInteger, nullable=True) #所得稅(利益)
    total_consolidated_profit_for_the_period=Column(BigInteger, nullable=True)# 本期綜合損益總額
    total_nonbusiness_income=Column(BigInteger, nullable=True) #營業外收入
    total_nonoperating_income_and_expense=Column(BigInteger, nullable=True) #營業外收入及支出
    total_nonbusiness_expenditure=Column(BigInteger, nullable=True) #營業外支出
    unrealized_gain=Column(BigInteger, nullable=True) #未實現損益
    unrealized_gain_from_inter_affiliate_accounts=Column(BigInteger, nullable=True) #聯屬公司間未實現利益淨額
    UniqueConstraint('stock_id', 'date', name='uq_cfs_stk_d')

class CashFlow(Base):
    '''
    現金流量表
    '''
    __tablename__='cash_flow_stat'
    id = Column(Integer, Sequence('cf_id_seq'), primary_key=True)
    stock_id = Column(Integer, ForeignKey(
        'stock.id', onupdate="CASCADE", ondelete="RESTRICT"), nullable=False)
    date=Column(Date,nullable=False) #date 不支援 timezone

    adjustment_item=Column(BigInteger, nullable=True) #調整項目
    accounts_payable=Column(BigInteger, nullable=True) #應付帳款增加(減少)
    amortization_expense=Column(BigInteger, nullable=True) #攤銷費用
    amount_due_to_related_parties=Column(BigInteger, nullable=True) #應付帳款-關係人增加(減少)
    cash_balances_beginning_of_period=Column(BigInteger, nullable=True) #期初現金及約當現金餘額
    cash_balances_end_of_period=Column(BigInteger, nullable=True) #期末現金及約當現金餘額
    cash_balances_increase=Column(BigInteger, nullable=True) #本期現金及約當現金增加（減少）數
    cash_flows_from_operating_activities=Column(BigInteger, nullable=True) #營業活動之淨現金流入(流出)
    cash_flows_provided_from_financing_activities=Column(BigInteger, nullable=True) #籌資活動之淨現金流入（流出）
    cash_provided_by_investing_activities=Column(BigInteger, nullable=True) #投資活動之淨現金流入（流出）
    cash_received_through_operations=Column(BigInteger, nullable=True) #營運產生之現金流入（流出）
    decrease_in_deposit_deposit=Column(BigInteger, nullable=True) #存出保證金減少
    decrease_in_short_term_loans=Column(BigInteger, nullable=True) #短期借款減少
    depreciation=Column(BigInteger, nullable=True) #折舊費用
    hedging_financial_liabilities=Column(BigInteger, nullable=True) #除列避險之金融負債
    income_before_income_tax_from_continuing_operations=Column(BigInteger, nullable=True) #繼續營業單位稅前淨利（淨損）
    interest_expense=Column(BigInteger, nullable=True) #利息費用
    interest_income=Column(BigInteger, nullable=True) #利息收入
    inventory_increase=Column(BigInteger, nullable=True) #存貨（增加）減少
    net_income_before_tax=Column(BigInteger, nullable=True) #本期稅前淨利（淨損）
    other_non_current_liabilities_increase=Column(BigInteger, nullable=True) #其他流動資產(增加)減少
    pay_the_interest=Column(BigInteger, nullable=True) #支付之利息
    proceeds_from_long_term_debt=Column(BigInteger, nullable=True) #舉借長期借款
    property_and_plant_and_equipment=Column(BigInteger, nullable=True) #取得不動產、廠房及設備
    realized_gain=Column(BigInteger, nullable=True) #已實現銷貨損失（利益）
    receivable_increase=Column(BigInteger, nullable=True) #應收帳款（增加）減少
    redemption_of_bonds=Column(BigInteger, nullable=True) #償還公司債
    rental_principal_repayments=Column(BigInteger, nullable=True) #租賃本金償還
    total_income_loss_items=Column(BigInteger, nullable=True) #收益費損項目合計
    unrealized_gain=Column(BigInteger, nullable=True) #未實現銷貨利益（損失）
    UniqueConstraint('stock_id', 'date', name='uq_cf_stk_d')

class DvdEtSplt(Base):
    '''
    Dividends & Stock Splits
    '''
    __tablename__='dvd_et_splt'
    id = Column(Integer, Sequence('dvd_et_splt_id_seq'), primary_key=True)
    stock_id = Column(Integer, ForeignKey(
        'stock.id', onupdate="CASCADE", ondelete="RESTRICT"), nullable=False)
    trade_date=Column(Date,nullable=False) #date 不支援 timezone
    interval_annual_ratio=Column(Float, nullable=False)
    dividends=Column(Numeric(scale=2), nullable=True)
    stock_split=Column(Float, nullable=True)
    UniqueConstraint('stock_id', 'trade_date', name='uq_dvds_stk_d')

# class EqtyDispersion(Base):
#     '''
#     集保戶股權分散表(股權持股分級表)
#     '''
# class StockMrgShrt(Base):
#     '''
#     個股融資融劵表
#     '''
# class StockInstDiff(Base):
#     '''
#     個股三大法人買賣表
#     '''
# class StockDealerDiff(Base):
#     '''
#     自營商買賣超彙總表
#     '''




if __name__ == '__main__':

    # # drop table if exist
    # Base.metadata.drop_all(engine, tables=[
    #                        Exchange.__table__, Stock.__table__, StockKMin.__table__, StockKHour.__table__, StockKDay.__table__], checkfirst=True)
    Base.metadata.create_all(bind=engine, checkfirst=True)  # create table


    with SessionLocal() as session:
        # insert
        session.add(Exchange(name='台灣證券交易所', code_name='TPE'))
        session.add(Stock(exchange_id=1, symbol='2330', name='台積電'))
        session.commit()

        rows = session.query(Exchange)
        # row=rows[0]
        # print(row.fee ,row.loan)
        print(rows)

        for row in rows:
            print(row.id, row.name, row.code_name)
            # print(row.product_id, row.deal_dt, row.price, row.qty, row.trade_type, row.total_price)

        # #kbar test
        # session.add(StockKMin(stock_id=1,
        #                 start_ts="2021-10-21T23:01:12.560Z",
        #                 volume=33,
        #                 open=800,
        #                 high=804,
        #                 low=799,
        #                 close=800,
        #                 dividends=5,
        #                 stock_splits=0))
        # session.commit()
        # rows = session.query(StockKMin)
        # for row in rows:
        #     print(row.id, row.stock_id, row.volume, row.high)

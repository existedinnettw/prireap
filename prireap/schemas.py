from typing import List, Optional
import datetime
from pydantic import BaseModel
from decimal import Decimal
from enum import Enum, auto


class Interval(str, Enum):
    min = 'min'  # min1?
    hour = 'hour'
    day = 'day'


class StockKBarBase(BaseModel):
    '''
    suitable for StockKMin, StockKHour, StockKDay
    '''
    stock_id: int
    start_ts: datetime.datetime

    open: Optional[Decimal] = None
    high: Optional[Decimal] = None
    low: Optional[Decimal] = None
    close: Optional[Decimal] = None
    volume: Optional[int] = None

    transaction: Optional[int] = None
    # dividends: Optional[int] = None
    # stock_splits: Optional[int] = None

    class Config:
        orm_mode = True


class StockKBarCreate(StockKBarBase):
    interval: Interval = Interval.day

# delattr(class, field_name)


class StockKBar(StockKBarBase):
    id: int


class StockCreate(BaseModel):
    '''
    contain business logic only, no structure data.
    '''
    exchange_id: int
    symbol: str
    name: Optional[str] = None

    class Config:
        orm_mode = True


class Stock(StockCreate):
    id: int
# class stockQuery(BaseModel):
#     code_name: Optional[str]= "TPE"
#     symbols: str
#     class Config:
#         orm_mode=True


class ExchangeCreate(BaseModel):
    name: str
    code_name: str
    strt_cron_utc: Optional[str] = None
    end_cron_utc: Optional[str] = None

    class Config:
        orm_mode = True


class Exchange(ExchangeCreate):
    id: int
    stocks: List[Stock]


class ExchangeResponse(ExchangeCreate):
    id: int


class DvdEtSpltCreate(BaseModel):
    '''
    Dividends & Stock Splits
    '''
    # id : Column(Integer, Sequence('dvd_et_splt_id_seq'), primary_key=True)
    stock_id: int
    trade_date: datetime.date
    interval_annual_ratio: float
    dividends: Optional[Decimal] = None
    stock_split: Optional[float] = None
    

    class Config:
        orm_mode = True


class DvdEtSplt(DvdEtSpltCreate):
    id: int


class CFSCreate(BaseModel):
    '''
    綜合損益表
    Consolidated Financial Statements(Consolidated Income Statement)
    '''
    stock_id: int
    date: datetime.date  # date 不支援 timezone

    adjustment_item: Optional[int] = None #調整項目
    cost_of_goods_sold: Optional[int] = None #營業成本
    cumulative_effect_of_changes_in_accounting_principle: Optional[int] = None #累積影響數
    eps: Optional[float] = None #每股稅後盈餘(元)
    equity_attributable_to_owners_of_parent: Optional[int] = None #綜合損益總額歸屬於母公司業主
    extraordinary_items: Optional[int] = None #非常損益
    gross_profit: Optional[int] = None  #營業毛利
    income_after_taxes: Optional[int] = None #稅後純益
    income_before_income_tax: Optional[int] = None #稅前利潤
    income_before_tax_from_continuing_operations: Optional[int] = None # 繼續營業單位稅前淨利
    income_from_continuing_operations : Optional[int] = None #繼續營業單位本期淨利（淨損）
    income_loss_from_discontinued_operation: Optional[int] = None #停業部門損益
    net_income: Optional[int] = None #淨利潤
    noncontrolling_interests: Optional[int] = None #綜合損益總額歸屬於非控制權益
    operating_expenses: Optional[int] = None #營業費用
    operating_income: Optional[int] = None #營業收入淨額
    other_comprehensive_income: Optional[int] = None #其他綜合損益（淨額）
    other_nonoperating_expense_or_loss: Optional[int] = None # 其他收益及費損淨額(OTHNOE)
    pre_tax_income: Optional[int] = None #稅前純益
    realized_gain: Optional[int] = None #已實現銷貨（損）益
    realized_gain_from_inter_affiliate_accounts: Optional[int] = None #聯屬公司間已實現利益淨額
    revenue: Optional[int] = None# 營業收入
    tax: Optional[int] = None #所得稅(利益)
    total_consolidated_profit_for_the_period: Optional[int] = None# 本期綜合損益總額
    total_nonbusiness_income: Optional[int] = None #營業外收入
    total_nonoperating_income_and_expense: Optional[int] = None #營業外收入及支出
    total_nonbusiness_expenditure: Optional[int] = None #營業外支出
    unrealized_gain: Optional[int] = None #未實現損益
    unrealized_gain_from_inter_affiliate_accounts: Optional[int] = None #聯屬公司間未實現利益淨額

    class Config:
        orm_mode = True


class CFS(CFSCreate):
    id: int


class CashFlowCreate(BaseModel):
    '''
    現金流量表
    '''
    stock_id: int
    date: datetime.date  # date 不支援 timezone

    accounts_payable: Optional[int] = None  # 應付帳款增加(減少)
    amortization_expense: Optional[int] = None  # 攤銷費用
    amount_due_to_related_parties: Optional[int] = None  # 應付帳款-關係人增加(減少)
    cash_balances_beginning_of_period: Optional[int] = None  # 期初現金及約當現金餘額
    cash_balances_end_of_period: Optional[int] = None  # 期末現金及約當現金餘額
    cash_balances_increase: Optional[int] = None  # 本期現金及約當現金增加（減少）數
    cash_flows_from_operating_activities: Optional[int] = None  # 營業活動之淨現金流入(流出)
    cash_flows_provided_from_financing_activities: Optional[int] = None # 籌資活動之淨現金流入（流出）
    cash_provided_by_investing_activities: Optional[int] = None  # 投資活動之淨現金流入（流出）
    cash_received_through_operations: Optional[int] = None  # 營運產生之現金流入（流出）
    decrease_in_deposit_deposit: Optional[int] = None  # 存出保證金減少
    decrease_in_short_term_loans: Optional[int] = None  # 短期借款減少
    depreciation: Optional[int] = None  # 折舊費用
    hedging_financial_liabilities: Optional[int] = None  # 除列避險之金融負債
    income_before_income_tax_from_continuing_operations: Optional[int] = None # 繼續營業單位稅前淨利（淨損）
    interest_expense: Optional[int] = None  # 利息費用
    interest_income: Optional[int] = None  # 利息收入
    inventory_increase: Optional[int] = None  # 存貨（增加）減少
    net_income_before_tax: Optional[int] = None  # 本期稅前淨利（淨損）
    other_non_current_liabilities_increase: Optional[int] = None  # 其他流動資產(增加)減少
    pay_the_interest: Optional[int] = None  # 支付之利息
    proceeds_from_long_term_debt: Optional[int] = None  # 舉借長期借款
    property_and_plant_and_equipment: Optional[int] = None  # 取得不動產、廠房及設備
    realized_gain: Optional[int] = None  # 已實現銷貨損失（利益）
    receivable_increase: Optional[int] = None  # 應收帳款（增加）減少
    redemption_of_bonds: Optional[int] = None  # 償還公司債
    rental_principal_repayments: Optional[int] = None  # 租賃本金償還
    repayment_of_long_term_debt: Optional[int] = None  #償還長期借款
    total_income_loss_items: Optional[int] = None  # 收益費損項目合計
    unrealized_gain: Optional[int] = None  # 未實現銷貨利益（損失）

    class Config:
        orm_mode = True


class CashFlow(CashFlowCreate):
    id: int


class EqtyDispCreate(BaseModel):
    stock_id: int
    date: datetime.date  # date 不支援 timezone
    l1_nper : Optional[int]=None
    l1_n: Optional[int]=None
    l2_nper : Optional[int]=None
    l2_n: Optional[int]=None
    l3_nper : Optional[int]=None
    l3_n: Optional[int]=None
    l4_nper : Optional[int]=None
    l4_n: Optional[int]=None
    l5_nper : Optional[int]=None
    l5_n: Optional[int]=None
    l6_nper : Optional[int]=None
    l6_n: Optional[int]=None
    l7_nper : Optional[int]=None
    l7_n: Optional[int]=None
    l8_nper : Optional[int]=None
    l8_n: Optional[int]=None
    l9_nper : Optional[int]=None
    l9_n: Optional[int]=None
    l10_nper : Optional[int]=None
    l10_n: Optional[int]=None
    l11_nper : Optional[int]=None
    l11_n: Optional[int]=None
    l12_nper : Optional[int]=None
    l12_n: Optional[int]=None
    l13_nper : Optional[int]=None
    l13_n: Optional[int]=None
    l14_nper : Optional[int]=None
    l14_n: Optional[int]=None
    l15_nper : Optional[int]=None
    l15_n: Optional[int]=None
    diff_n: Optional[int]=None

    class Config:
        orm_mode = True

class EqtyDisp(EqtyDispCreate):
    id:int
# data Sources



最重要的就是確立原始資料是什麼樣子，因為之後的衍生的資料將會千變萬化

# overview

* [用 Python 打造自己的股市資料庫 — 美股篇](https://medium.com/ai%E8%82%A1%E4%BB%94/%E7%94%A8-python-%E6%89%93%E9%80%A0%E8%87%AA%E5%B7%B1%E7%9A%84%E8%82%A1%E5%B8%82%E8%B3%87%E6%96%99%E5%BA%AB-%E7%BE%8E%E8%82%A1%E7%AF%87-e3e896659fd6)

要從strategy 的角度去思考，會需要什麼要的data

可以參考下面去分table

* mean shift 股價&量
  * 預計用分K，再根據每個model 自己的需要去改成自己要用的data
  * 股價如果 standardization，可能無法看出到底上漲多少倍，成交量也是同樣的道理。
    * 如果只有zero mean 股價高的股票，看起來會漲跌很多
    * standardization 可能還是有效果，因為可以看出pattern，就是技術指標的形態方法
    * normalization 則可能要注易極端值而整體變很怪，但股價的極端值是有意義的不能說刪就刪
    * 或是把股價以第一天或最後一天同除自己得1，其它的依此類推
      * 股量有可能完全沒交易=0，同除會變zero division，可能還是要用standerdization
  * 或是說把成交量除以當日總成交量？不過這樣就變成要有該股市的日成交量資料
  * 技術指標 e.g. kd 都可以從股價衍生出來。
* 基本面指標
  * 公司的分類
    * 這個分類也是很麻煩，一個公司可能有很多的業務，而且會有新的業務產生
* 其它東西的價格可能也可以考慮納入 e.g. 鋼鐵、銅價上漲，中鋼的股價也上漲，但這樣會變得更為複雜，因為價格是序列化資料，資料量會增很多
  * 同時追蹤美股、歐股大盤?
  * ml 系列的演算法 通常對這種序列化資料無法很好的利用。
* 目前發現，**基本面是不可或缺的**，籌碼面的效果也很好
* 基本上目前的可靠來源只有**finmind**，所以只能它有什麼就抄什麼

如果我一直糾結在用那些資料，就永遠無法開始





# exchanger

把 交易所的工作時間用crontab 記錄? 如果用crontab了話，要同時用兩個，一個for start time, another for end time

另一個辦法，hour資料直接表示區間，minute 的 \* ，表示所有時間而非單一min，但這無法處理台股開到 30分，所以不是很理想。

# stock

| id   | exg_id | symbol        | name |      |
| ---- | ------ | ------------- | ---- | ---- |
|      |        | str(e.g.2330) |      |      |

# stock data

| id   | stock_id | 資本額(億) | 上市櫃日期 | 產業類型 |
| ---- | -------- | ---------- | ---------- | -------- |
|      |          |            |            |          |

* 可以用這個來排除etf
* 有上市櫃日期可以避免去找不存在的資料

# kbar

目前分k的資料為主，或說分k 就是暫時的最後目標，當沖的回測也是用分K而已。

有了分k，hour k 和 日k，都只要簡單加起來就好

* [01 用 Python 串接券商 API 取得歷史 Tick 資料與 K 棒](https://www.youtube.com/watch?v=gsAfVWrbs7g)
  * 分K是最者符合我的預測，永豐API甚至只有分K
* [ 第一章  中國證券交易統計資料庫簡介](http://www.aremos.org.tw/tedc/china/csto/ch1.htm)
  * 

以下是 kbar 應該有的表格

| stock_id | market_id | name | start_ts | interval | volume | turnover | open | high | low  | close | n_deals | dividends | stock_splits |
| -------- | --------- | ---- | -------- | -------- | ------ | -------- | ---- | ---- | ---- | ----- | ------- | --------- | ------------ |
|          |           |      |          |          |        |          |      |      |      |       |         |           |              |
|          |           |      |          |          |        |          |      |      |      |       |         |           |              |
|          |           |      |          |          |        |          |      |      |      |       |         |           |              |

* market_id
  * 就是交易所代號，以交易所為主，而非國家，就算兩地市場也 ok
    * [兩地上市- MBA智库百科](https://www.google.com/url?sa=t&rct=j&q=&esrc=s&source=web&cd=&ved=2ahUKEwi53rSJm8nwAhUCyYsBHa3fBb4QFjAAegQIAxAD&url=https%3A%2F%2Fwiki.mbalib.com%2Fzh-tw%2F%E4%B8%A4%E5%9C%B0%E4%B8%8A%E5%B8%82&usg=AOvVaw2_lzxr79iW_aoVAs9ugGCF)
  * [免責聲明– Google 財經](https://www.google.com/url?sa=t&rct=j&q=&esrc=s&source=web&cd=&ved=2ahUKEwjevM2amsnwAhXRBKYKHYGvBxUQFjABegQIBhAD&url=https%3A%2F%2Fwww.google.com%2Fintl%2Fzh-TW%2Fgooglefinance%2Fdisclaimer%2F&usg=AOvVaw2cVE8E0tJ-G7zTH-n_n_o5)
  * [一、交易地區及交易所代碼對照表](https://www.google.com/url?sa=t&rct=j&q=&esrc=s&source=web&cd=&ved=2ahUKEwiV5bfFmsnwAhVrKqYKHcqBBoYQFjAAegQIBBAD&url=http%3A%2F%2Fsec2.twsa.org.tw%2Fdoc%2F2%2F%E4%BA%A4%E6%98%93%E5%9C%B0%E5%8D%80%E5%8F%8A%E4%BA%A4%E6%98%93%E6%89%80%E4%BB%A3%E7%A2%BC%E5%B0%8D%E7%85%A7%E8%A1%A8_%E5%AE%9A%E7%BE%A9.pdf&usg=AOvVaw2iO9kuJ_XUxzApV4pnDosU)
  * 這同時表示需要 market table，記錄一些資料，比如開盤、關盤時間
* start timestamp
  * 永api time stamp 是類似用 big int
* interval
  * 這筆是 分、時、日?
  * 這可能原始是分bar table，有view 轉成其它的要用
  * 或分成三個table? 就不用這一項
  * yahoo finance # valid intervals: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo
    * 這些是api ，所以models 不一定要有一樣的pattern，不過可以看到它是用 query parameter而非分開resource
    * 有這麼多項不太可能都是分別的
    * 
* data
  * **open**
    * 小到沒有交易就會null
  * **high** 
  * **low**
  * **close**
  * **volume**
    * 成交量（股數）
  * ~~trading money, trade value~~
    * 成交金額，有時候是寫amount。volume\* close 約等於，但每一筆成交價不同所以還是會差一點
  * n_deals, transaction,  Trading_turnover
    * 成交筆數, 幾筆交易
* ~~dividends~~
  * 股息
* ~~stock_splits~~
  * 股票分割, 除權
* stock_splits和dividends很糾結，這兩個對simulation 是必要的，
  * 




dividends 和 kbar 是和"天“相關的，其實可以和kbar分開（特別是kmin, khour）。yfinance有action，專門列出所有 dividens & kbar & 對應日期，可見db 裡可能是分開存放。目前為了簡化，先放一起。
有部份API是直接用 [adj close](https://www.investopedia.com/terms/a/adjusted_closing_price.asp) ，我看它的說明感覺是一個動作全部都會影響到，所以記錄當下的adj close感覺是沒意義的？

# tick

tick 資料還是有意義的，特別是在分析主力的時候。

tick資料就是原始資料，當tick 資料蒐集完整之後，甚至能直接query 出 kbar 資料。

但目前為止，還做不到那裡，我還是先把主力放在kbar

要完美的記錄世界各地，甚至只有台灣的每一比 tick 資料對我來說也是太困難了，可能只能partial 存下台股某幾檔。這表示DB和整個程式不能要求完整性，而是有多少資料做多少事。

換句話說tick 資料絕對會和k bar 並行，且絕對不會成為主軸

付錢給專業的API也是辦法

* [01 用 Python 串接券商 API 取得歷史 Tick 資料與 K 棒](https://www.youtube.com/watch?v=gsAfVWrbs7g)
* timestamp, close, volume, 委買價, 委買量, 委賣價, 委賣量

|      |      |      |      |      |      |
| ---- | ---- | ---- | ---- | ---- | ---- |
|      |      |      |      |      |      |



# fundamental

| id   | 日期 | stock_id |      |      |      |      |
| ---- | ---- | -------- | ---- | ---- | ---- | ---- |
| int  | date | int      |      |      |      |      |

基本面

* 如果要有基本面，db 要有 company 的table

* finmind
  * **綜合損益表**
  * **現金流量表**
    * JG有說，資本支出(投資活動之淨現金流入)特別重要
    * [你也可以看懂財報，靠自己找出下一檔台積電 - 今周刊](https://www.google.com/url?sa=t&rct=j&q=&esrc=s&source=web&cd=&cad=rja&uact=8&ved=2ahUKEwjkkI_N3-z2AhXBxGEKHUY3CJ04ChAWegQIBBAB&url=https%3A%2F%2Fwww.businesstoday.com.tw%2Farticle%2Fcategory%2F80402%2Fpost%2F201505150015%2F&usg=AOvVaw25Fs4Z9kTaT-wfWxXzG4Xf)
    * [如何利用現金流量表解讀財務分析及防止舞弊](https://www.google.com/url?sa=t&rct=j&q=&esrc=s&source=web&cd=&cad=rja&uact=8&ved=2ahUKEwjiptbd4Oz2AhW8wosBHZaZD9MQFnoECAcQAQ&url=https%3A%2F%2Fwww.tpex.org.tw%2Fweb%2Fabout%2Fpublish%2Fmonthly%2Fmonthly_dl.php%3Fl%3Dzh-tw%26DOC_ID%3D582&usg=AOvVaw0N7e_NaD4Gv48dNKhKWAah)
  * 資產負債表 （先不要
  * 股利政策表 (先不要)
  * 除權除息結果表
    * 
  * **月營收表**
  
* 除權息和糾結
  * 算法，e.g. 股價18.3, 現金股利0.5552，股票股利0.4543，持有股數=1000
    * [存股必看！從股利通知單教你算：除權息到底領多少？如何避開2.11％⼆代健保費？](https://lohas.edh.tw/article/20996)
    
      * [什麼是除權息？ - 理財小學堂｜投資小學堂 - 理財寶](https://www.cmoney.tw/learn/course/cmoney/topic/124)
    
        * 有錯的部份
    
      * [股票除權除息參考價計算說明](https://www.google.com/url?sa=t&rct=j&q=&esrc=s&source=web&cd=&cad=rja&uact=8&ved=2ahUKEwiCvraA3-j2AhVbUPUHHRmFDF4QFnoECAYQAQ&url=https%3A%2F%2Finvestoredu.twse.com.tw%2FFileSystem%2FeBook%2F12_%E8%82%A1%E7%A5%A8%E9%99%A4%E6%AC%8A%E9%99%A4%E6%81%AF%E5%8F%83%E8%80%83%E5%83%B9%E8%A8%88%E7%AE%97%E8%AA%AA%E6%98%8E.pdf&usg=AOvVaw1CDZ1gi7RPCM130Trlwfkj)
    
        * 最準確
    
        * $$
          \frac{(除權前一日收盤價格 - 現金股利)+(現金增資認購價 × 現金增資配股率)}{1+無償配股率(盈餘及法定盈餘公積、資本公積配股率)+現金增資配股率}
          $$
    
          * $$
            \frac{57.6-3.0250729+0\times0}{1+(0.0201671529+0.0302507293)+0}
            $$
    
          * 
    
    * [除權除息參考價試算](https://www.tpex.org.tw/web/stock/exright/exref/rightref.php?l=zh-tw)
    
    * **配股率**=(股票股利/10)=0.4543/10
      * 沒有標準的英文，因為美國根本就只有分割，allotment_rate 可能是最接近的
      * 其實也可以考慮用stock split，stock split-1=allotment rate
        * 如果直接換算，stock split 有個麻煩是理論上每天的stock split 都要是1，但yahoo 是沒有分配了話是0。好處是可以區分是沒有資料、沒有分配、有分配。
    
    * 除權息的股票數：配股率x持有股數=0.4543/10x1000=45.43
    
    * 除權息的現金股利：0.5552x1000=555.2
    
    * 除權息後價格：(18.3-0.5552)/(1+0.4543/10)=16.973
    
    * 18.3x1000~=555.2+(1000+45)*16.973
    
  * 台股只有除權，美股只有股票分割，不是共通的所以不能共用。但是配股率可以，e.g. 台股除權10塊=配股率1=股票分割2:1
  
  * 上述的資料牽涉到adj close 的計算。
    * [ [理財] Yahoo Adjusted Close 計算方式 ](https://zwindr.blogspot.com/2020/12/yahoo-adjusted-close.html)
      * 其實就是因除權息前後總價值不變，所以把以前價格乘百分比回去。這只需要知道除權息前的價格和除權息後的參考價就好。
      * [Vectorizing Adjusted Close with Python](https://joshschertz.com/2016/08/27/Vectorizing-Adjusted-Close-with-Python/)
        * 0.039s算完一檔，其實還是有點慢，1000檔要39s
    * 還原股價（含backtest）和殖利率是兩個除權息會用到的應用。
      * 殖利率就把整年現金股利相加/目前股價。如果要短期的就麻煩了，可能是每季（x4），半年，每年，但是沒有分析了話很難知道。
      * adj close 的計算本身就是和 stock split, divident 在一起會比較方便
      * 綜上分析，可能還是把 除權息 資料和K線放一起應該不會有什麼問題。不過**分開**了話可以存更少的資料，比較傾向這個。
    * 實際在台股會有個問題，2008以前的股利的算法公式是不一樣的，還有員工配股之類的東西。
      * [員工分紅費用化新制上路 - 金管會](https://www.google.com/url?sa=t&rct=j&q=&esrc=s&source=web&cd=&cad=rja&uact=8&ved=2ahUKEwi9zd-Fken2AhVMA94KHUAHBMEQFnoECAoQAQ&url=https%3A%2F%2Fwww.fsc.gov.tw%2Ffckdowndoc%3Ffile%3D%2F%E5%93%A1%E5%B7%A5%E5%88%86%E7%B4%85%E8%B2%BB%E7%94%A8%E5%8C%96%E6%96%B0%E5%88%B6%E4%B8%8A%E8%B7%AF.pdf%26flag%3Ddoc&usg=AOvVaw2RLj3vT41RR_75oeHuf0Yt)
        * [員工分紅費用化新制之介紹](http://webline.sfi.org.tw/download/lib_ftp/97年座談會/20080325員工分紅費用化宣導會/員工分紅費用化之推動情形.pdf)
        * 2008-1-1 實施，2009是發2008的股利，所以從**2010開始**的比較正常。
      * 對於adj close 來說，只要前後的股價知道就好，對於殖利率，以前其實也偏向都當作是一種股利（福利），而非股價分割。也就是其實可以把以前的難算東西全部都算作現金股利，只要backtest的時候都用adj close。
      * 資料的部份，目前是想全部來自**goodinfo**，2010年以前的股票股利算法不同，花了一堆時間解不開，還是算了。
    * 還原股價永遠是以目前股價為準，往前還原。
  
* 基本面資料本身的週期是不太固定的，有的每季，有的每年。和kbar的每天分析有點難融合。

* [第一章台灣股票上櫃公司財務報表資料庫簡介](https://www.google.com/search?channel=trow5&client=firefox-b-d&q=OTHNOE)

  * [進入使用 台灣股票上市公司財務報表 (COMP) 資料庫「網路版」](https://net-comp.tedc.org.tw)
  * 三個表的column 都有

* finmind的殖利率和股利是分開的

  * 個股 PER、PBR 資料表 vs 除權除息結果表。其中 除權除息結果表 直接把除權也視為除息，只有存存差價，只為了calculate adj。
  * [個股日本益比、殖利率及股價淨值比（依代碼查詢）](https://www.twse.com.tw/zh/page/trading/exchange/BWIBBU.html)
    * https://www.twse.com.tw/exchangeReport/BWIBBU_d?response=json&date=&selectType=&_=1648937827862
    * https://www.twse.com.tw/exchangeReport/BWIBBU?response=json&date=20220301&stockNo=2330&_=1648938078221

  * 


## 綜合損益表 (CFS)

* finmind 裡以前和現在的資料column有不一樣的，不太確定為什麼？反正先都打上
* [臺灣經濟新報財務資料庫](https://www.google.com/url?sa=t&rct=j&q=&esrc=s&source=web&cd=&cad=rja&uact=8&ved=2ahUKEwix64OApvj2AhWPyosBHaYrCmgQFnoECAMQAQ&url=https%3A%2F%2Fwww.tej.com.tw%2Fwebtej%2Fplus%2Fwim4.htm&usg=AOvVaw3kZwqAe3sbN4hVOghqSJ5M)
  * 列表詳細

* id
* stock_id
* date
* AdjustmentItem 調整項目
* CostOfGoodsSold營業成本
* CumulativeEffectOfChangesInAccountingPrinciple  會計原則變動累積影響數
  * CumulativeEffectOfChanges 累積影響數

    * 應該是一樣的

* **EPS** 每股稅後盈餘(元)
  * 本益比
* EquityAttributableToOwnersOfParent 綜合損益總額歸屬於母公司業主
* ExtraordinaryItems 非常損益
  * IFRS 停用

* GrossProfit 營業毛利
* IncomeAfterTaxes 稅後純益
  * IncomeAfterTax
    * 應該一樣

* IncomeBeforeIncomeTax 稅前利潤
* IncomeBeforeTaxFromContinuingOperations 繼續營業單位稅前淨利
* IncomeFromContinuingOperations 繼續營業單位本期淨利（淨損）
* IncomeLossFromDiscontinuedOperation 停業部門損益
* NetIncome 淨利潤
* NoncontrollingInterests 綜合損益總額歸屬於非控制權益
* OTHNOE 其他收益及費損淨額
  * other_nonoperating_expense_or_loss

* OperatingExpenses 營業費用
* OperatingIncome 營業收入淨額
* OtherComprehensiveIncome 其他綜合損益
* PreTaxIncome 稅前純益
* RealizedGain 已實現銷貨（損）益
* RealizedGainFromInterAffiliateAccounts 聯屬公司間已實現利益淨額
  * realized_gain_from_inter_affiliate_accounts

* Revenue 營業收入
* TAX 所得稅(利益)
* TotalConsolidatedProfitForThePeriod 本期綜合損益總額
* TotalNonbusinessIncome 營業外收入
  * total_nonbusiness_income

* TotalNonoperatingIncomeAndExpense 營業外收入及支出
* TotalnonbusinessExpenditure 營業外支出
* UnrealizedGain 未實現損益
* UnrealizedGainFromInterAffiliateAccounts 聯屬公司間未實現利益淨額
* ~~合併前非屬共同控制股權損益~~
  * -
  * 未確認
  * income loss from Equity attributable to non-controlling interest before business combination under common control ?
  * Equity attributable to non-controlling interest before business combination under common control 合併前非屬共同控制股權
    * [ 台灣股票上市公司財務報表資料庫 :  6281 資產負債表 ](https://net-comp.tedc.org.tw/search/view2.php?db=COMP&desc=%E5%8F%B0%E7%81%A3%E8%82%A1%E7%A5%A8%E4%B8%8A%E5%B8%82%E5%85%AC%E5%8F%B8%E8%B2%A1%E5%8B%99%E5%A0%B1%E8%A1%A8%E8%B3%87%E6%96%99%E5%BA%AB&form_e=AR&name_ord=6281&book=%EF%BB%BF%E5%85%A8%E5%9C%8B%E9%9B%BB)

  * 


## ~~資產負債表~~

* AccountsPayable 應付帳款
* AccountsPayable_per
* AccountsPayableToRelatedParties 應付帳款－關係人
* AccountsPayableToRelatedParties_per
* AccountsReceivableDuefromRelatedPartiesNet 應收帳款－關係人淨額
* AccountsReceivableDuefromRelatedPartiesNet_per 應收帳款－關係人淨額
* AccountsReceivableNet 應收帳款淨額
* AccountsReceivableNet_per 應收帳款淨額
* BondsPayable 應付公司債
* BondsPayable_per
* CapitalStock 股本合計
* CapitalStock_per
* CapitalSurplus 資本公積合計
* CapitalSurplus_per 
* CapitalSurplusAdditionalPaidInCapital 資本公積－發行溢價
* CapitalSurplusAdditionalPaidInCapital_per
* CapitalSurplusChangesInEquityOfAssociatesAndJointVenturesAccountedForUsingEquityMethod 資本公積－採用權益法認列關聯企業及合資股權淨值之變動數
* CapitalSurplusChangesInEquityOfAssociatesAndJointVenturesAccountedForUsingEquityMethod_per
* CapitalSurplusDonatedAssetsReceived 資本公積－受贈資產
* CapitalSurplusDonatedAssetsReceived_per
* CapitalSurplusNetAssetsFromMerger 資本公積－合併溢額
* CapitalSurplusNetAssetsFromMerger_per
* CashAndCashEquivalents 現金及約當現金
* CashAndCashEquivalents_per
* CurrentAssets 流動資產合計
* CurrentAssets_per
* CurrentFinancialAssetsAtFairvalueThroughProfitOrLoss 透過損益按公允價值衡量之金融資產－流動
* CurrentFinancialAssetsAtFairvalueThroughProfitOrLoss_per 
* CurrentFinancialLiabilitiesAtFairValueThroughProfitOrLoss 透過損益按公允價值衡量之金融負債－流動
* CurrentFinancialLiabilitiesAtFairValueThroughProfitOrLoss_per
* CurrentLiabilities 流動負債合計
* CurrentLiabilities_per
* DeferredTaxAssets 遞延所得稅資產
* DeferredTaxAssets_per
* Equity 權益總額
* Equity_per
* EquityAttributableToOwnersOfParent 歸屬於母公司業主之權益合計
* EquityAttributableToOwnersOfParent_per
* IntangibleAssets 無形資產
* IntangibleAssets_per
* Inventories 存貨
* Inventories_per 存貨
* LegalReserve 法定盈餘公積
* LegalReserve_per
* LongtermBorrowings 長期借款
* LongtermBorrowings_per
* NoncontrollingInterests 非控制權益
* NoncontrollingInterests_per
* NoncurrentAssets 非流動資產合計
* NoncurrentAssets_per
* NoncurrentLiabilities 非流動負債合計
* NoncurrentLiabilities_per
* OrdinaryShare 普通股股本
* OrdinaryShare_per
* OtherCurrentAssets 其他流動資產
* OtherCurrentAssets_per
* OtherCurrentLiabilities 其他流動負債
* OtherCurrentLiabilities_per
* OtherEquityInterest 其他權益合計
* OtherEquityInterest_per 
* OtherNoncurrentAssets 其他非流動資產
* OtherNoncurrentAssets_per
* OtherNoncurrentLiabilities 其他非流動負債
* OtherNoncurrentLiabilities_per
* OtherPayables 其他應付款
* OtherPayables_per 
* OtherReceivablesDueFromRelatedParties 其他應收款－關係人淨額
* OtherReceivablesDueFromRelatedParties_per 
* PropertyPlantAndEquipment 不動產、廠房及設備
* PropertyPlantAndEquipment_per
* RetainedEarnings 保留盈餘合計
* RetainedEarnings_per
* ShorttermBorrowings 短期借款
* ShorttermBorrowings_per
* TotalAssets 資產總額
* TotalAssets_per
* TotalLiabilitiesEquity 負債及權益總計
* TotalLiabilitiesEquity_per

## 現金流量表（cash flow statement）

* [IFRS各業適用現金流量表項目名稱、定義及編號](https://www.dgbas.gov.tw/public/Attachment/741314336KIDMI9KP.pdf)
* [現金流量表中文項目](https://www.google.com/url?sa=t&rct=j&q=&esrc=s&source=web&cd=&cad=rja&uact=8&ved=2ahUKEwirhNC55Pb2AhViQ_UHHS4GBvQQFnoECAYQAQ&url=http%3A%2F%2Fwww.laws.taipei.gov.tw%2Flawatt%2FLaw%2FA040390050019400-20160108-3000-001.pdf&usg=AOvVaw0yLyTS31GCm4apjVPoKbVX)
  * 裡面很多項目其實是CFS的
* AccountsPayable 應付帳款增加(減少)
* AmortizationExpense 攤銷費用
* AmountDueToRelatedParties 應付帳款-關係人增加(減少)
* CashBalancesBeginningOfPeriod 期初現金及約當現金餘額
* CashBalancesEndOfPeriod 期末現金及約當現金餘額
* CashBalancesIncrease 本期現金及約當現金增加（減少）數
* CashFlowsFromOperatingActivities 營業活動之淨現金流入(流出)
* CashFlowsProvidedFromFinancingActivities 籌資活動之淨現金流入（流出）
* CashProvidedByInvestingActivities **投資活動之淨現金流入（流出）**
  * 通常認為的資本支出，負值增加表示擴大支出
* CashReceivedThroughOperations 營運產生之現金流入（流出）
* DecreaseInDepositDeposit 存出保證金減少
* DecreaseInShortTermLoans 短期借款減少
* Depreciation 折舊費用
* HedgingFinancialLiabilities 除列避險之金融負債
* IncomeBeforeIncomeTaxFromContinuingOperations 繼續營業單位稅前淨利（淨損）
* InterestExpense 利息費用
* InterestIncome 利息收入
* InventoryIncrease 存貨（增加）減少
* NetIncomeBeforeTax 本期稅前淨利（淨損）
* OtherNonCurrentLiabilitiesIncrease 其他流動資產(增加)減少
* PayTheInterest 支付之利息
* ProceedsFromLongTermDebt 舉借長期借款
* PropertyAndPlantAndEquipment 取得不動產、廠房及設備
* RealizedGain 已實現銷貨損失（利益）
* ReceivableIncrease 應收帳款（增加）減少
* RedemptionOfBonds 償還公司債
* RentalPrincipalRepayments 租賃本金償還
* TotalIncomeLossItems 收益費損項目合計
* UnrealizedGain 未實現銷貨利益（損失）
* 每季一次

## 月營收表

* stock_id
* start_d 開始時間
* 營收

## 股利 Dividends & Stock Split

目前預設是這個，但股利其實是有 股利政策表 的（[   股利分派情形-經股東會確認](https://mops.twse.com.tw/mops/web/t05st09)），但台灣的蠻亂的，交易日另外在 除權息公告。其實沒有必要要求全世界的股市都用同一張table

* 股利分派情形-經股東會確認 ，有表格，有各個名目的細項來源，但沒有交易日。
  * [決定分配股息及紅利或其他利益(94.5.5後之上市櫃/興櫃公司)](https://mops.twse.com.tw/mops/web/t108sb19_q1) 這個沒有表格，是公告，但是有交易日，且會合併一次發放兩次者
    * 如果要scrap 了話，推薦
* 以下的設計更像是把dividends 和 stock split 拼起來，因為純的dividends不需要stock_split，純stock split 不需要dividends和annual_ratio。
  * 可能可以直接拆成兩個表
* id
* stock_id
* trade_date 交易日
* interval_annual_ratio:int
  * 季:4、半年:2、year:1
* dividends
  * 現金股利
* stock_split
  * 配股率+1

# Institutional 

* **個股融資融劵表**
* 整體市場融資融劵表
  * 整體市場先不要
* 個股三大法人買賣表
* 整體市場三大法人買賣表
  * 整體市場先不要
* 外資持股表
* **股權持股分級表**
* 借券成交明細
* 個股的可以用stock 開頭，整體市場的可以用market(mrkt)開頭

## 集保戶股權分散表(股權持股分級表)

## 個股融資融劵表

## 自營商買賣超彙總表

> finmind沒有，要自己copy

## 個股三大法人買賣表



# 爬蟲

* [ BeautifulSoup vs Selenium vs Scrapy三大Python網頁爬蟲實作工具的比較 ](https://www.learncodewithmike.com/2020/11/beautifulsoup-vs-selenium-vs-scrapy-for-python-web-scraping.html)
* user agent 隨機
* decode 選utf-8
* 電腦自己dial pppoe
  * modem, router 設 pppoe passthrough (DSL-6740C選項是反的)
  * win os 設定dial
  * create .bat 重連 script 
  * python call subprocess
* [postgresql确定某张业务表最后被使用时间](https://www.cndba.cn/xty/article/3516)
* sql
  * `drop table consolid_stat;`
  * `select * from consolid_stat order by date desc;`


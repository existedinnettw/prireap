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

如果我一直糾結在用那些資料，就永遠無法開始





# exchanger

把 交易所的工作時間用crontab 記錄? 如果用crontab了話，要同時用兩個，一個for start time, another for end time

另一個辦法，hour資料直接表示區間，minute 的 \* ，表示所有時間而非單一min，但這無法處理台股開到 30分，所以不是很理想。

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
  * trading money, trade value
    * 成交金額，有時候是寫amount。volume\* close 約等於，但每一筆成交價不同所以還是會差一點
  * n_deals, transaction,  Trading_turnover
    * 成交筆數, 幾筆交易
* dividends
  * 股息
* stock_splits
  * 股票分割, 除權



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



# financial

|      |      |      |      |      |      |
| ---- | ---- | ---- | ---- | ---- | ---- |
|      |      |      |      |      |      |

基本面

* 如果要有基本面，db 要有 company 的table

使用基本面是一個很重大的議題，因為datamodel 對於基本面是很難有有效的記錄的 




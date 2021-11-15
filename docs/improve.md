

# large query slow

db query(1.5min, 用yield_per 之後) 和 return response(8min) 花非常多時間，特別是return
db部份實際用sql query是10s，資料約400MB而已，沒有理由那麼慢

return response 會那麼久我猜是花一堆時間和memory在pydantic model 上。

> 現在看起來用python 做backend也是很錯誤的，任何compile language 都好

    ## 改進
   * https://fastapi.tiangolo.com/advanced/response-directly/
   * https://github.com/tiangolo/fastapi/issues/788

改完之後只要30s，其中大部份時間花在 to json

這告訴我們動態的type check ，或是create numerous object 對python來說是非常耗時的。query中兩件事的共通點就是object，sqlalchemy 要把 raw query result 轉成orm model，而return 之後pydantic 要把orm model轉成response pydatic type。

type check 不僅沒有提升性能反而拖慢，但是引入type check後，搭配vscode的自動完成確實提升很多開發效率。目前我能做的就是繞過 create object （python 的大軟肋）

1. 直接用raw sql 而非orm model，這大大降低了使用orm的意義，不過sqlalchemy 似乎能簡化的create sql query string，且避免錯誤的query，目前看是有意義。
2. 直接 return json response (from dictionary)，完全不用object
   1. 目前用orjson（自改處理decimal） 可以少到30s
      1. 但是如果用fastapi提供的orjson，指定response class，會變4:30，所以一定要自己直接return json jesponse，可能是fastapi有做些什麼
   2. 用pandas 可能更好，有加速

使用pd.read_sql 之後，query的速度為接近1min, pd to_json 不到10s。也就是共1min。
pd read sql 也是用sqlalchemy ，所以看起來是卡在sqlalchemy

我現在用 psycopg2 直接query 看看要多久，確定是否為sqlalchemy的問題，有可能其實是python 的問題。
實測之後psycopg約在16s，比raw query慢一點但improve performance可以接受再多花心力。
要確認是不是sqlalchemy 的鍋，用connection 進行query 試試，[Working with Engines and Connections](https://docs.sqlalchemy.org/en/14/core/connections.html#module-sqlalchemy.engine) ，它是return row of dict 這種有mapping的，我估計是有用class去轉換psycopg2 的 tuple --> dict，應該是不會有多好。

用了這個 [connect_psycopg2_to_pandas.py](https://gist.github.com/jakebrinkmann/de7fd185efe9a1f459946cf72def057e), [Working with the DBAPI cursor directly](https://docs.sqlalchemy.org/en/14/core/connections.html#working-with-the-dbapi-cursor-directly)。大約50s（少10s），所以可能不是sqlalchemy 的鍋，而是tuple 轉pd dataframe所需的耗費。
確實是，有交叉比對 psycopg2加 read_sql，差不多就是50s。所以多出來的35s都用在pandas 的轉換。

再來要優化了話就是棄用pandas，自己把tuple 轉成json

[How to return dictonary or json if I use psycopg2?](https://stackoverflow.com/questions/57209769/how-to-return-dictonary-or-json-if-i-use-psycopg2), [How to overcome "datetime.datetime not JSON serializable"?](https://stackoverflow.com/questions/11875770/how-to-overcome-datetime-datetime-not-json-serializable) 
測試之後，如果沒有用dict format 而是直接變成很多array，fetch 部分一樣16s，json 部分可達18s，共約30s。使用orjson之後只要8s

如果用RealDictCursor，fetching 會慢到超過1min, 用DictCursor 是51s，且一樣是return array。所以如果要用必須自己把tuple 先轉成 dict

改完之後，query 保持在16s, 轉成dict (list comprehension)約9s, 轉成json 8s。可以看到只要牽涉到複雜一點的轉換，特別是class，就會花很多時間。現在總共30s多一點點，勉強可以接受。相比之下就發現，pandas 為了轉成df，其中多花了30s，也就是一半以上都是為了轉成df。
這其實很好笑，為了程式的架構，盡可能用class，完成之後，為了速度，全部再拆掉。這個拆掉是完全必要的，從原本10min --> 30s，快了20倍，而且不是為了數字好看，不做了話根本用不了。

parallel query  在純sql下，還是10s(4 workers)，沒提升。

# backend 架構

之所以用web server backend 是因為考慮用websocket 簡化synchronous data flow。那麼其實只需要在online 時使用 websocket 就好，一般training 時的資料完全可以從DB裡直接拿。甚至websocket 完全不傳送資料，完全只notify。
比如

* [Integrating Python with MySQL](https://towardsdatascience.com/integrating-python-with-mysql-4575248d5929)
* [Working with Data Analysis and Relational Databases in Python](https://www.opensourceforu.com/2019/08/working-with-data-analysis-and-relational-databases-in-python/)

是直接拿db裡的資料，大量使用CTE。如果覺得每次都寫sql太不structure，包成function (和 web backend 裡的crud 一模一樣)，一樣可以有很好的structure。但是節省開發api時花的時間e.g. restful api path name，還有最終的性能不需要經過http request 和 因此產生的傳送時間，不需要轉成json再轉回pd dataframe。
我在q_trade裡面也是用這個方法，pd.read_sql + sqlalchemy complie 成 sql statement，可以兼顧速度和可讀性。

如果使用spark 等方式，也會處理好資料傳輸的問題，不過我不確定有沒有辦法去stream資料，沒辦法了話，該部份獨立用backend 就好。

如果要我選最完美的解法，我覺得可能是gRPC，return 的format 自己定就好，送過來完全不用parse。如果要換到http 中執行也沒問題

* [ [DAY21]小朋友才要選擇~gRPC與http我全都要之gRPC Gateway ](https://ithelp.ithome.com.tw/articles/10243864)

不過grpc還是要下到port (111,135)（或說socket, TCP/IP），速度上肯定是會比DB server 只經過一個port 還慢的。但肯定是比http快 [gRPC vs. REST 效能測試](https://medium.com/skyler-record/grpc-vs-rest-%E6%95%88%E8%83%BD%E6%B8%AC%E8%A9%A6-859f062f6ce3)

不過說到底，backend 架構比較像用牛刀殺小雞，如果能夠殺好，當然是沒差。只是現在殺不好，因為引入的機制反而成了bottle neck，所以才回過頭考慮簡化。不然rest api backend server 能夠提供外網連接，或是身份驗證，debug UI，統一的接口（為了websocket），簡單的連接方式（client不需要知道DB的password）...，不能說是無意義的。

# json for big table

其實我覺得 json 並不是很好給table 的format，因為重複的column一直出現，也就是compact 不足。csv大概只有json一半
但是以下文章提到 json 的 scalibility，或performance更好(更好處理)。

* [ JSON and the Confusion of Formats in Big Data ](https://engineering.creditkarma.com/json-and-the-confusion-of-formats-in-big-data)
* [Difference Between JSON and CSV](https://www.educba.com/json-vs-csv/)
  * only when bandwidth important

雖然json提到的優點很多，但是仔細想想，對於大量資料，傳送資料的時間（IO）遠大於處理資料的時間。所以我認為csv 其實也是更優的選擇，如果已經找不到其它點去improve，性能又慢到受不了。

其實如果一開始架構上就用其它方案，e.g. Spark，它自帶就會有optimize的exchange format，e.g. Parquet, Avro...。

大部份來說restapi return json，但是似乎沒有任何限制非json不可（或是我找不到），沒有清楚規定真的很煩。

# setting

* [Why JSON isn’t a Good Configuration Language](https://www.lucidchart.com/techblog/2018/07/16/why-json-isnt-a-good-configuration-language/)
* 建議用 TOML



# spark












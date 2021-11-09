

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

# backend 架構

之所以用web server backend 是因為考慮用websocket 簡化synchronous data flow。那麼其實只需要在online 時使用 websocket 就好，一般training 時的資料完全可以從DB裡直接拿。甚至websocket 完全不傳送資料，完全只notify。
比如

* [Integrating Python with MySQL](https://towardsdatascience.com/integrating-python-with-mysql-4575248d5929)
* [Working with Data Analysis and Relational Databases in Python](https://www.opensourceforu.com/2019/08/working-with-data-analysis-and-relational-databases-in-python/)

是直接拿db裡的資料，大量使用CTE。如果覺得每次都寫sql太不structure，包成function (和 web backend 裡的crud 一模一樣)，一樣可以有很好的structure。但是節省開發api時花的時間e.g. restful api path name，還有最終的性能不需要經過http request 和 因此產生的傳送時間，不需要轉成json再轉回pd dataframe。

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












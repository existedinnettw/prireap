# prireap
agent that get stock data from API, and store it to local db server.

# run app
necessary process...
1. install postgresql
2. setup .env file in root directory, include DB_HOST, password...
3. create sql models by `python -m prireap.models`
4. start backend server by `python -m prireap.main`

To add data into db, execute script in "crawScript"
e.g.`python -m prireap.crawScript.20yearsDvdSplt`
During crawing, start backend server is necessary.

to periodic update newest data into sql, run script in "crawSrc" folder

# todo
我不相望造成被爬蟲網站的負擔，並且簡化爬蟲
希望可以用p2p的方式自動互傳。
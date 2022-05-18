'''
這個檔案用於選擇outer api e.g. yfinance or shoaji，並直接以subprocess 的型式執行
'''


import asyncio
from ..crawSrc.crawYf import YfCraw
from ..crawSrc.crawBase import BasicCraw
import time

'''
實際執行這個script 做日常的抓取

'''


# add_tpe_stocks()


if __name__ == '__main__':
    async def main():
        # crawler=YfCraw()
        crawler=BasicCraw()
        await crawler.async_init()
        await crawler.run()
        
        # get_khours()
    asyncio.run(main())

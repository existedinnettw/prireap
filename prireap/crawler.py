'''
這個檔案用於選擇outer api e.g. yfinance or shoaji，並直接以subprocess 的型式執行
'''


import asyncio
from .crawSrc.crawYf import YfCraw
from .crawSrc.crawBase import BasicCraw
import time













# add_tpe_stocks()


if __name__ == '__main__':
    async def main():
        # crawler=YfCraw()
        crawler=BasicCraw()
        await crawler.async_init()
        # crawler.sio.
        # add_tpe_stocks()
        # crawler.create_khour_of_cur()
        
        # crawler.khour_event.set()
        # crawler.create_kday_of_cur()


        # asyncio.run(crawler.run())
        # await asyncio.sleep(10)
        # raise
        await crawler.create_kday_of_cur()
        # time.sleep(0.5)
        # await asyncio.get_running_loop().run_forever()
        await asyncio.Event().wait()
        
        # get_khours()
    asyncio.run(main())

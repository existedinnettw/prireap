'''
這個檔案用於選擇outer api e.g. yfinance or shoaji，並直接以subprocess 的型式執行
'''


from .crawSrc.crawYf import YfCraw
from .crawSrc.crawBase import BasicCraw
import time













# add_tpe_stocks()


if __name__ == '__main__':
    # crawler=YfCraw()
    crawler=BasicCraw()
    # add_tpe_stocks()
    # crawler.create_khour_of_cur()
    
    # crawler.khour_event.set()
    # crawler.create_kday_of_cur()


    crawler.run()
    # time.sleep(0.5)
    
    # get_khours()

'''
這個檔案用於選擇outer api e.g. yfinance or shoaji，並直接以subprocess 的型式執行
'''


from .crawSrc.crawYf import YfCraw







crawler=YfCraw()






# add_tpe_stocks()


if __name__ == '__main__':
    # add_tpe_stocks()
    crawler.create_khour_of_cur()
    # get_khours()

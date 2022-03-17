import time, datetime, os, collections
from dateutil import relativedelta
import numpy as np  #数値計算用
import pandas as pd  #データ処理用
import yfinance as yf
import pandas_datareader
#import requests  #クローリング用
#import bs4  #スクレイピング用

pd.set_option('display.unicode.east_asian_width', True)  #全角文字幅を考慮して表示



#銘柄情報を取得
def get_stock_code(stock_dict, data_type='list', show=False):
    database = stock_dict['database']
    group_type = stock_dict['group_type']
    group_name = stock_dict['group_name']
    stock_list = []

    #東証上場銘柄
    if (database=='tosho_jpx'):
        file_name = 'https://www.jpx.co.jp/markets/statistics-equities/misc/tvdivq0000001vg2-att/data_j.xls'
        df_stock = pd.read_excel(file_name)
        df_stock['17業種区分'] = df_stock['17業種区分'].str.replace(' ', '')  #余計な空白を削除
        df_stock['コード'] = df_stock['コード'].astype(str).str[:4] +'.T'

    #TOPIXの構成銘柄
    if (database=='topix_jpx'):
        file_name = 'https://www.jpx.co.jp/markets/indices/topix/tvdivq00000030ne-att/TOPIX_weight_jp.xlsx'
        df_stock = pd.read_excel(file_name)
        df_stock['日付'] = df_stock['日付'].replace(r'(.*/D.*)', np.nan, regex=True)  #無効な値を置換
        df_stock = df_stock.drop(['調整係数対象銘柄'], axis=1).dropna()  #NaNを含む行を捨てる
        df_stock['日付'] = pd.to_datetime(df_stock['日付'], format='%Y%m%d')  #型変換
        df_stock['コード'] = df_stock['コード'].astype(str).str[:4] +'.T'

    #日経225の構成銘柄
    if (database=='n225_nikkei'):
        file_name = 'https://indexes.nikkei.co.jp/nkave/archives/file/nikkei_stock_average_weight_jp.csv'
        df_stock = pd.read_csv(file_name, encoding='shift-jis').dropna()
        df_stock = df_stock.rename(columns={"社名":"銘柄名"})  #列名変更
        df_stock['日付'] = pd.to_datetime(df_stock['日付'], format='%Y/%m/%d')  #型変換
        df_stock['コード'] = df_stock['コード'].astype(str).str[:4] +'.T'

    #ETFの構成銘柄
    if (database=='tosho_etf'):
        file_name = 'https://www.jpx.co.jp/equities/products/etfs/investors/tvdivq0000005cdd-att/nlsgeu000000vx9t.xlsx'
        df_stock = pd.read_excel(file_name, header=3)
        df_stock = df_stock[['コード', '略称', '連動指標名', '連動対象カテゴリー', '売買単位\n(口)']]
        df_stock = df_stock.dropna()  #NaNを含む行を捨てる
        df_stock = df_stock.rename(columns={"略称":"銘柄名", "売買単位\n(口)":"売買単位"})  #列名変更
        df_stock['コード'] = df_stock['コード'].astype(str).str[:4] +'.T'

    if (group_type!='全銘柄'):
        if (show==True):
            print(df_stock)
            counter = collections.Counter(df_stock[group_type].values.tolist())  #単語の出現回数を取得
            print(counter)

        #特定グループのデータだけ抽出
        df_stock = df_stock[df_stock[group_type].isin(group_name)]
    #stock_list = list(set(df_stock['コード'].values.tolist()))  #銘柄コード


    #貸借銘柄の情報
    file_name = 'https://www.jpx.co.jp/listing/others/margin/tvdivq0000000od2-att/list.xls'
    df_margin_stock = pd.read_excel(file_name, sheet_name='一覧', header=1)
    df_margin_stock = df_margin_stock.rename(columns={"銘柄コード":"コード"})  #列名変更
    df_margin_stock = df_margin_stock[df_margin_stock['貸借区分'].isin(['貸借銘柄'])]  #空売りできる銘柄
    df_margin_stock['コード'] = df_margin_stock['コード'].astype(str).str[:4] +'.T'
    #margin_stock_list = list(set(df_margin_stock['コード'].values.tolist()))  #銘柄コード
    #stock_list = list(set(stock_list) & set(margin_stock_list))

    df_stock = pd.merge(df_stock, df_margin_stock.drop(['銘柄名'], axis=1), on='コード', how='inner')
    stock_list = sorted(df_stock['コード'].values.tolist())  #銘柄コード

    if (show==True):
        print(stock_list)
        print()


    if(data_type=='dataframe'):
        return df_stock
    if(data_type=='list'):
        return stock_list



#株価データ取得（学習用データは5年、テストデータは0.5年くらい）
def get_stock_price(stock_list, date_min, date_max, show=False):
    if(datetime.datetime(2000, 4, 1)<date_min and date_max<datetime.datetime(2021, 1, 2)):
        df_price_all = pd.DataFrame()
        for code in stock_list:
            try:
                file_relative_path = os.path.dirname(__file__)
                csv_relative_path = r'../../../inout_data/price_data/' +code +r'.csv'
                df_price = pd.read_csv(os.path.join(file_relative_path, csv_relative_path), index_col=0)

                df_price_all['Open', code] = df_price['Open']
                df_price_all['High', code] = df_price['High']
                df_price_all['Low', code] = df_price['Low']
                df_price_all['Close', code] = df_price['Close']
                df_price_all['Adj Close', code] = df_price['Adj Close']
                df_price_all['Volume', code] = df_price['Volume']
            except Exception as e:
                #import traceback
                #print("エラー情報\n" + traceback.format_exc())
                df_price_all['Open', code] = np.nan
                df_price_all['High', code] = np.nan
                df_price_all['Low', code] = np.nan
                df_price_all['Close', code] = np.nan
                df_price_all['Adj Close', code] = np.nan
                df_price_all['Volume', code] = np.nan
        df_price_all.columns = pd.MultiIndex.from_tuples(df_price_all.columns)  #マルチカラム化
        df_price_all.index = pd.to_datetime(df_price_all.index, format='%Y-%m-%d')  #型変換
        df_price_all = df_price_all[date_min : date_max-datetime.timedelta(days=1)]

    else:
        #df_price_all = yf.download(stock_list, start=date_min, end=date_max)
        df_price_all = pandas_datareader.data.DataReader(stock_list, 'yahoo', date_min, date_max)

    if (show==True):
        print("df_price_all['Close'] =")
        print(df_price_all['Close'])
        print(df_price_all['Close'].describe())
        print()

    return df_price_all



if (__name__ == '__main__'):
    stock_dict = {'database':'tosho_jpx', 'group_type':'17業種区分', 'group_name':['自動車・輸送機']}  #

    #stock_dict = {'database':'tosho_jpx', 'group_type':'33業種区分', 'group_name':['情報・通信業']}  #
    #stock_dict = {'database':'tosho_etf', 'group_type':'連動対象カテゴリー', 'group_name':['外国株']}  #

    stock_list = get_stock_code(stock_dict, show=True)
    #print(get_stock_code(stock_dict, data_type='dataframe'))


    #date_max = datetime.date.today()
    date_ref = datetime.datetime(2019, 10, 1)  #4/1、7/1、10/1、1/1にする
    date_min = date_ref -relativedelta.relativedelta(months=5*12)  #years年前
    date_max = date_ref +relativedelta.relativedelta(months=6)  #months月後
    print(date_min)
    print(date_max)

    #株価データ取得
    df_price = get_stock_price(stock_list, date_min, date_max, show=True)

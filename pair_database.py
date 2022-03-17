import datetime
import numpy as np
import pandas as pd
#import yfinance as yf
#import pandas_datareader
#import statsmodels
#import statsmodels.api as sm
#from statsmodels.tsa.stattools import adfuller, coint

pd.set_option('display.unicode.east_asian_width', True)  #全角文字幅を考慮して表示

from database.pair_data import *
from database.pair_stat import *
from database.pair_show import *



def make_stat_database(
        stock_dict,
        date_ref,
        date_min,
        date_max,
        condition='adf判定無し',
        cutoff1=0.01,
        cutoff2=0.005,
        reinvest=False,  #統計データを取り直すかどうか
        show=False
    ):
    
    #特定グループの銘柄コード
    stock_list = get_stock_code(stock_dict, show=show)

    #株価データ取得
    df_price = get_stock_price(stock_list, date_min, date_max, show=show)


    #終値を使う場合
    df_close = df_price['Close'].dropna(how='all', axis=1)  #全てNaNの列は削除
    
    #移動平均乖離率を使う場合
    #df_sma = df_close.rolling(window=40).mean()  #移動平均
    #df_dma = 100*(df_close -df_sma)/df_sma  #移動平均乖離率（difference from moving average）

    #低位株のデータを抽出
    date_latest = date_ref -datetime.timedelta(days=365)
    #stock_list = df_close[date_latest:date_ref].describe().T.query('mean <= 5000').index.tolist()
    #stock_list = df_close[date_latest:date_ref].describe().T.query('5000 <= mean').index.tolist()
    #stock_list = df_close.columns
    #df_close = df_close[stock_list]  #
    #print(df_close.describe())

    df_train = df_close[:date_ref -datetime.timedelta(days=1)]  #境界の日付を含めた過去のデータ
    print('df_train =')
    print(df_train)
    #print(df_close[date_ref:])

    print(stock_dict)
    print()


    #統計データのファイル名
    filename1 = stock_dict['group_type'] +'_' +'-'.join(stock_dict['group_name']) +'_cutoff' +str(cutoff1)[2:]
    filename2 = '_' +date_min.strftime('%Y%m%d') +'-' +(date_ref -datetime.timedelta(days=1)).strftime('%Y%m%d')

    file_relative_path = os.path.dirname(__file__)
    csv_relative_path = r'../../inout_data/pair_stat/' +filename1 +filename2 +r'.csv'
    stat_csv_path = os.path.join(file_relative_path, csv_relative_path)
    
    #分析済みのデータがあれば読み込む
    if (os.path.isfile(stat_csv_path) and reinvest==False):
        df_pair_all = pd.read_csv(stat_csv_path, index_col=0)
    else:
        #ADF検定と共和分検定によりペアを抽出
        df_pair_all, mat_p_coint = find_coint_pairs(df_train, cutoff=cutoff1, show=True)
        #df_pair_all, mat_p_coint = find_coint_pairs(df_dma[:date_ref], cutoff=cutoff1, show=True)
        if (len(df_pair_all.index) != 0):
            df_pair_all.to_csv(stat_csv_path)  #データ出力

        #株式の各ペア間の共和分検定のp値を示すヒートマップ
        if (len(stock_list)<50):
            title = '「' +'・'.join(stock_dict['group_name']) +'」内での共和分検定'
            #show_heatmap(mat_p_coint, stock_list, title)


    #出来高
    df_volume = df_price['Volume'].dropna(how='all', axis=1)  #全てNaNの列は削除
    volume_mean = df_volume.mean()
    #print(volume_mean)

    df_pair_all['volume1'] = 0
    df_pair_all['volume2'] = 0
    for pair_index in range(len(df_pair_all.index)):
        pair_code1 = df_pair_all['code1'].iloc[pair_index]
        pair_code2 = df_pair_all['code2'].iloc[pair_index]

        df_pair_all['volume1'].iat[pair_index] = volume_mean[pair_code1]
        df_pair_all['volume2'].iat[pair_index] = volume_mean[pair_code2]

    #出来高が少ない銘柄を含むペアは削除
    df_pair_all = df_pair_all[1000<df_pair_all['volume1']]
    df_pair_all = df_pair_all[1000<df_pair_all['volume2']]


    #Bonferroni法でp値の閾値を厳しく取る
    num_pairs = len(df_pair_all)
    #cutoff2 = 30/(num_pairs*(num_pairs-1)/2)  #100ペアで0.005くらいになるよう調整
    #cutoff2 = cutoff2/(num_pairs*(num_pairs-1)/2)  #

    #候補を絞り込む
    if(condition == 'adf大'):
        df_pair_all = df_pair_all[0.05<df_pair_all['p_adf']]
    if(condition == 'adf小'):
        df_pair_all = df_pair_all[df_pair_all['p_adf']<0.05]
    df_pair_all = df_pair_all[df_pair_all['p_coint_aic']<cutoff2]
    df_pair_all = df_pair_all[df_pair_all['p_coint_bic']<cutoff2]

    if(stock_dict['database'] != 'tosho_etf'):
        df_pair_all = df_pair_all[df_pair_all['mean1']<2500]
        df_pair_all = df_pair_all[df_pair_all['mean2']<2500]
    df_pair_all = df_pair_all[0.7<df_pair_all['corr']]

    df_pair_all['p_score'] = df_pair_all["p_coint_aic"] +df_pair_all["p_coint_bic"]
    if(condition == 'adf小'):
        df_pair_all['p_score'] = df_pair_all["p_coint_aic"] +df_pair_all["p_coint_bic"] +df_pair_all["p_adf"]
    df_pair_all = df_pair_all.sort_values(['p_score'], ascending=True)  #並び替え


    return df_pair_all, df_price



if (__name__ == '__main__'):
    #計算の開始時刻を記録
    print ('Calculation start: ', time.ctime())  #計算開始時刻を表示
    compute_time = time.time()  #計算の開始時刻

    #stock_dict = {'database':'tosho_jpx', 'group_type':'33業種区分', 'group_name':['金属製品']}
    #stock_dict = {'database':'tosho_jpx', 'group_type':'33業種区分', 'group_name':['繊維製品']}
    #stock_dict = {'database':'tosho_jpx', 'group_type':'17業種区分', 'group_name':['商社・卸売']}
    #stock_dict = {'database':'tosho_jpx', 'group_type':'17業種区分', 'group_name':['自動車・輸送機']}
    #stock_dict = {'database':'tosho_jpx', 'group_type':'17業種区分', 'group_name':['鉄鋼・非鉄']}
    #stock_dict = {'database':'tosho_jpx', 'group_type':'17業種区分', 'group_name':['医薬品']}
    #stock_dict = {'database':'tosho_jpx', 'group_type':'17業種区分', 'group_name':['電力・ガス']}
    #stock_dict = {'database':'topix_jpx', 'group_type':'業種', 'group_name':['輸送用機器']}  #有望
    #stock_dict = {'database':'topix_jpx', 'group_type':'業種', 'group_name':['金属製品']}  #有望
    #stock_dict = {'database':'topix_jpx', 'group_type':'業種', 'group_name':['繊維製品']}  #
    #stock_dict = {'database':'topix_jpx', 'group_type':'ニューインデックス区分', 'group_name':['TOPIX Core30']}
    #stock_dict = {'database':'topix_jpx', 'group_type':'ニューインデックス区分', 'group_name':['TOPIX Core30', 'TOPIX Large70']}
    #stock_dict = {'database':'n225_nikkei', 'group_type':'業種', 'group_name':['自動車']}
    #stock_dict = {'database':'n225_nikkei', 'group_type':'業種', 'group_name':['機械', '自動車']}
    stock_dict = {'database':'tosho_etf', 'group_type':'連動対象カテゴリー', 'group_name':['外国株', '日本株（テーマ別）']}  #


    train_months = 5*12
    test_months = 6
    #cutoff = 0.01
    reinvest = False  #統計データを取り直すかどうか

    #date_ref = datetime.date.today()
    date_ref = datetime.datetime(2019, 4, 1)  #4/1、7/1、10/1、1/1にする

    date_min = date_ref -relativedelta.relativedelta(months=train_months) #months月前
    date_max = date_ref +relativedelta.relativedelta(months=test_months) #months月後

    df_pair_all, df_close = make_stat_database(stock_dict, date_ref, date_min, date_max, show=True)
    print(df_pair_all)


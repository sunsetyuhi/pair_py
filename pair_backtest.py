import os, datetime, traceback
from dateutil import relativedelta
import numpy as np
import pandas as pd

pd.set_option('display.unicode.east_asian_width', True)  #全角文字幅を考慮して表示
pd.set_option('display.max_rows', 250)

from backtest.pair_signal import *
from backtest.pair_order import *
from backtest.pair_balance import *
from backtest.pair_show import *



def calc_backtest(
        stock_dict,
        df_pair_all,
        df_price,
        date_ref,
        date_min,
        date_max,
        condition='adf判定無し',
        spq = 100,  #最小購入単位
        fund = 1.0*10**6,  #1ペアに使う資金
        num_pairs = 10,  #投資先の数
        cutoff2 = 0.005,
        win1 = 1,
        win2 = 120,  #60～120日くらい
        losscut=0.1,
        show = False
    ):

    num_pairs_ori = len(df_pair_all.index)
    num_pairs = min(num_pairs, len(df_pair_all.index))  #取引するペア数
    #num_pairs = len(df_pair_all.index)  #取引するペア数
    
    df_pair_all = df_pair_all[~df_pair_all['code1'].duplicated()]  #重複銘柄を削除
    df_pair_all = df_pair_all[~df_pair_all['code2'].duplicated()]  #重複銘柄を削除

    df_pair_all = df_pair_all[:num_pairs]  #上から順にペアを抽出
    #df_pair_all = df_pair_all[-num_pairs:]  #下から順にペアを抽出

    df_pair_all['profit'] = np.nan


    #抽出したペア群でトレードを実施
    df_asset_all = pd.DataFrame()
    df_close = df_price['Close']
    try:
        for pair_index in range(len(df_pair_all.index)):
            pair_code1 = df_pair_all['code1'].iloc[pair_index]
            pair_code2 = df_pair_all['code2'].iloc[pair_index]
            print('pair : ' +pair_code1 +', ' +pair_code2)
    
            #テスト用データを作成
            df_pair = pd.merge(df_close[pair_code1], df_close[pair_code2], 
                            left_index=True, right_index=True, how='inner').dropna()
    
            #テストデータ。学習用データをwin2分入れる
            df_test1 = df_pair[pair_code1][:date_ref-datetime.timedelta(days=1)].iloc[-(win2-1):]
            df_test1 = df_test1.append(df_pair[pair_code1][date_ref:])
            df_test2 = df_pair[pair_code2][:date_ref-datetime.timedelta(days=1)].iloc[-(win2-1):]
            df_test2 = df_test2.append(df_pair[pair_code2][date_ref:])
            #df_test1 = df_pair[pair_code1][date_start:date_max]
            #df_test2 = df_pair[pair_code2][date_start:date_max]
            #print(df_test1)
    
            #シグナル計算
            df_trade = calc_signal(df_test1, df_test2, win1, win2, fund=10**6, spq=spq, delay=0, losscut=losscut)
    
            #売買箇所とスプレッドの可視化
            #show_zscore(df_trade['zscore'], 'zscore', sigma=2)
    
            #
            df_trade = calc_order(df_trade, fund, spq=spq, delay=1)
            df_trade = calc_balance(df_trade, fund, int_rate=0.03, fee=0.001, delay=1)
            print(df_trade.dropna())
            
            profit_end = int(df_trade['profit'].iloc[-1])
            print('profit = ', profit_end)
            print()

            #最終損益を記録
            query_str = "code1=='" +pair_code1 +"' and code2=='" +pair_code2 +"'"
            df_subset = df_pair_all.query(query_str)
            df_pair_all.loc[df_subset.index, "profit"] = profit_end
    
    
            position_max = int(df_trade['position'].max())
            profit_abs_max = int(abs(df_trade['profit'].max()))

            #取得した銘柄情報を記録
            if(position_max<1.5*fund and profit_abs_max<0.3*fund):  #極端な取引は無視する
                df_asset = df_trade.copy()[['fund', 'position', 'asset', 'profit']]
                if (len(df_asset_all.index) != 0):  #銘柄情報まとめデータに値がある時
                    df_asset_all = df_asset_all.add(df_asset, fill_value=0)
                else:  #
                    df_asset_all = df_asset
    
            title = 'profit = ' +str(profit_end) +', pvalue = ' +str(df_pair_all['p_coint_aic'].iloc[pair_index])
            #show_buysell(df_trade.copy(), title, pair_code1, pair_code2)
            #show_trade(df_trade, '')
        
        if(show==True):
            print(df_pair_all)
            print(df_asset_all)
            print(df_asset_all.describe())
            print('profit_all = ' +str(df_asset_all['profit'].dropna().iloc[-1]))
            print()

    except Exception as e:
        print("エラー情報\n" + traceback.format_exc())
    
    #統計データのファイル名
    filename1 = stock_dict['group_type'] +'_' +'-'.join(stock_dict['group_name'])
    filename2 = '_cutoff' +str(cutoff2)[2:] +'_win' +str(win1)+'-' +str(win2) +'_' +date_min.strftime('%Y%m%d')
    filename3 = '-' +date_ref.strftime('%Y%m%d') +'-' +date_max.strftime('%Y%m%d')
    file_relative_path = os.path.dirname(__file__)
    png_relative_path = r'../../inout_data/pair_img/' +filename1 +filename2 +filename3 +r'.png'
    stat_png_path = os.path.join(file_relative_path, png_relative_path)
    
    title1 = '「' +'-'.join(stock_dict['group_name']) +'」内での売買結果 ： '
    title2 = 'cutoff=' +str(cutoff2) +'、pair=' +str(len(df_pair_all)) +'/' +str(num_pairs_ori)
    title3 = '、win=' +str(win2)
    title = title1 +title2 +title3
    #show_trade(df_asset_all, title, stat_png_path)

    return df_asset_all



if (__name__ == '__main__'):
    from pair_database import *



    #計算の開始時刻を記録
    print ('Calculation start: ', time.ctime())  #計算開始時刻を表示
    compute_time = time.time()  #計算の開始時刻


    #東証上場銘柄の17業種
    #1100以下　：　情報通信・サービスその他。小売。-。商社・卸売。建設・資材。電機・精密。素材・化学。機械。不動産。食品。
    # 120以下　：　運輸・物流。自動車・輸送機。金融（除く銀行）。銀行。鉄鋼・非鉄。医薬品。電力・ガス。エネルギー資源。
    #stock_dict = {'database':'tosho_jpx', 'group_type':'17業種区分', 'group_name':['小売']}  #
    stock_dict = {'database':'tosho_jpx', 'group_type':'17業種区分', 'group_name':['商社・卸売']}  #候補多い↑
    #stock_dict = {'database':'tosho_jpx', 'group_type':'17業種区分', 'group_name':['建設・資材']}  #
    #stock_dict = {'database':'tosho_jpx', 'group_type':'17業種区分', 'group_name':['電機・精密']}  #
    #stock_dict = {'database':'tosho_jpx', 'group_type':'17業種区分', 'group_name':['素材・化学']}  #候補
    #stock_dict = {'database':'tosho_jpx', 'group_type':'17業種区分', 'group_name':['機械']}  #
    #stock_dict = {'database':'tosho_jpx', 'group_type':'17業種区分', 'group_name':['不動産']}  #候補少ない↓
    #stock_dict = {'database':'tosho_jpx', 'group_type':'17業種区分', 'group_name':['食品']}  #
    #stock_dict = {'database':'tosho_jpx', 'group_type':'17業種区分', 'group_name':['自動車・輸送機']}  #候補
    #stock_dict = {'database':'tosho_jpx', 'group_type':'17業種区分', 'group_name':['金融（除く銀行）', '銀行']}
    #stock_dict = {'database':'tosho_jpx', 'group_type':'17業種区分', 'group_name':['鉄鋼・非鉄']}
    #stock_dict = {'database':'tosho_jpx', 'group_type':'17業種区分', 'group_name':['電力・ガス', 'エネルギー資源']}

    #東証上場銘柄の33業種
    #500以下　：　サービス業。情報・通信業。小売業。-。卸売業。電気機器。機械。化学。
    #170以下　：　建設業。不動産業。食料品。その他製品。輸送用機器。金属製品。銀行業。
    # 70以下　：　医薬品。陸運業。ガラス・土石製品。繊維製品。精密機器。鉄鋼。
    # 40以下　：　証券、商品先物取引業。倉庫・運輸関連業。非鉄金属。その他金融業。
    # 30以下　：　パルプ・紙。電気・ガス業。ゴム製品。保険業。海運業。水産・農林業。石油・石炭製品。鉱業。空運業。
    #stock_dict = {'database':'tosho_jpx', 'group_type':'33業種区分', 'group_name':['情報・通信業']}  #候補多い↑
    #stock_dict = {'database':'tosho_jpx', 'group_type':'33業種区分', 'group_name':['卸売業']}  #候補
    #stock_dict = {'database':'tosho_jpx', 'group_type':'33業種区分', 'group_name':['電気機器']}
    #stock_dict = {'database':'tosho_jpx', 'group_type':'33業種区分', 'group_name':['化学']}  #
    #stock_dict = {'database':'tosho_jpx', 'group_type':'33業種区分', 'group_name':['建設業']}
    #stock_dict = {'database':'topix_jpx', 'group_type':'業種', 'group_name':['輸送用機器']}  #
    #stock_dict = {'database':'topix_jpx', 'group_type':'ニューインデックス区分', 'group_name':['TOPIX Core30', 'TOPIX Large70', 'TOPIX Mid400']}
    
    #stock_dict = {'database':'tosho_etf', 'group_type':'None', 'group_name':['TOPIX']}

    #4/1、7/1、10/1、1/1にする
    #date_ref = datetime.date.today()
    date_ref = datetime.datetime(2008, 8, 1)  #

    reinvest = False  #統計データを取り直すかどうか
    train_months = 5*12  #学習用データの月数
    test_months = 6  #テストデータの月数
    #condition = 'adf大'
    #condition = 'adf小'
    condition = 'adf判定無し'

    date_min = date_ref -relativedelta.relativedelta(months=train_months) #months月前
    date_max = date_ref +relativedelta.relativedelta(months=test_months) #months月後

    #ペア候補を作る
    df_pair_all, df_price = make_stat_database(stock_dict, date_ref, date_min, date_max, 
            condition, reinvest=reinvest, show=True)
    #df_close = df_price['Close']
    print(df_pair_all)



    spq = 100  #最小購入単位
    win1 = 1
    win2 = 120  #120日くらい
    num_pairs = 10  #投資先の数
    fund = 1.0*10**6  #手元資金の総額
    cutoff2 = 0.005
    losscut = 0.1
    
    #バックテスト
    df_asset_all = calc_backtest(stock_dict, df_pair_all, df_price, date_ref, date_min, date_max, 
            condition, spq, fund, num_pairs, cutoff2, win1, win2, losscut, show=True)
    
    '''for cutoff2 in [0.001, 0.0005]:  #
        for win2 in [40, 60, 80]:
            df_asset_all = calc_backtest(stock_dict, df_pair_all.copy(), df_price, date_ref, 
                    date_min, date_max, spq, fund_all, num_pairs, win1=win1, win2=win2, show=True)
    #'''


    #計算時間の表示
    compute_time = time.time() -compute_time
    print ('Calculation time: {:0.5f}[sec]'.format(compute_time))


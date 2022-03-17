import datetime
import numpy as np
import pandas as pd

pd.set_option('display.unicode.east_asian_width', True)  #全角文字幅を考慮して表示

from pair_backtest import *



if (__name__ == '__main__'):
    from pair_database import *
    from backtest.pair_show import *

    #計算の開始時刻を記録
    print ('Calculation start: ', time.ctime())  #計算開始時刻を表示
    compute_time = time.time()  #計算の開始時刻


    #東証上場銘柄の17業種
    #1100(500)以下　：　情報通信・サービスその他。小売。-。商社・卸売。建設・資材。電機・精密。素材・化学。機械。不動産。食品。
    # 120( 80)以下　：　運輸・物流。自動車・輸送機。金融（除く銀行）。銀行。鉄鋼・非鉄。医薬品。電力・ガス。エネルギー資源。
    #stock_dict = {'database':'tosho_jpx', 'group_type':'17業種区分', 'group_name':['情報通信・サービスその他']}  #
    #stock_dict = {'database':'tosho_jpx', 'group_type':'17業種区分', 'group_name':['小売']}  #
    #stock_dict = {'database':'tosho_jpx', 'group_type':'17業種区分', 'group_name':['商社・卸売', '建設・資材']}  #
    #stock_dict = {'database':'tosho_jpx', 'group_type':'17業種区分', 'group_name':['商社・卸売', '素材・化学']}  #
    #stock_dict = {'database':'tosho_jpx', 'group_type':'17業種区分', 'group_name':['商社・卸売']}  #候補
    #stock_dict = {'database':'tosho_jpx', 'group_type':'17業種区分', 'group_name':['建設・資材']}  #
    #stock_dict = {'database':'tosho_jpx', 'group_type':'17業種区分', 'group_name':['電機・精密']}  #
    #stock_dict = {'database':'tosho_jpx', 'group_type':'17業種区分', 'group_name':['素材・化学']}  #
    #stock_dict = {'database':'tosho_jpx', 'group_type':'17業種区分', 'group_name':['機械', '自動車・輸送機']}  #
    #stock_dict = {'database':'tosho_jpx', 'group_type':'17業種区分', 'group_name':['機械']}  #
    #stock_dict = {'database':'tosho_jpx', 'group_type':'17業種区分', 'group_name':['不動産', '金融（除く銀行）', '銀行']}  #
    #stock_dict = {'database':'tosho_jpx', 'group_type':'17業種区分', 'group_name':['不動産']}  #
    #stock_dict = {'database':'tosho_jpx', 'group_type':'17業種区分', 'group_name':['食品']}  #
    #stock_dict = {'database':'tosho_jpx', 'group_type':'17業種区分', 'group_name':['運輸・物流']}  #
    #stock_dict = {'database':'tosho_jpx', 'group_type':'17業種区分', 'group_name':['自動車・輸送機']}  #候補
    #stock_dict = {'database':'tosho_jpx', 'group_type':'17業種区分', 'group_name':['金融（除く銀行）', '銀行']}  #候補少ない↓
    #stock_dict = {'database':'tosho_jpx', 'group_type':'17業種区分', 'group_name':['金融（除く銀行）']}  #
    #stock_dict = {'database':'tosho_jpx', 'group_type':'17業種区分', 'group_name':['銀行']}  #
    #stock_dict = {'database':'tosho_jpx', 'group_type':'17業種区分', 'group_name':['鉄鋼・非鉄']}  #
    #stock_dict = {'database':'tosho_jpx', 'group_type':'17業種区分', 'group_name':['医薬品']}  #NG
    #stock_dict = {'database':'tosho_jpx', 'group_type':'17業種区分', 'group_name':['電力・ガス', 'エネルギー資源']}  #NG

    #東証上場銘柄の33業種
    #500(230)以下　：　情報・通信業。サービス業。小売業。-。卸売業。電気機器。機械。化学。
    #170(100)以下　：　建設業。不動産業。食料品。その他製品。輸送用機器。金属製品。銀行業。
    # 70( 50)以下　：　医薬品。陸運業。ガラス・土石製品。繊維製品。精密機器。鉄鋼。証券、商品先物取引業。
    # 40以下　：　倉庫・運輸関連業。非鉄金属。その他金融業。パルプ・紙。電気・ガス業。
    # 20以下　：　ゴム製品。保険業。海運業。水産・農林業。石油・石炭製品。鉱業。空運業。
    #stock_dict = {'database':'tosho_jpx', 'group_type':'33業種区分', 'group_name':['情報・通信業', '陸運業', '電気・ガス業']}  #
    #stock_dict = {'database':'tosho_jpx', 'group_type':'33業種区分', 'group_name':['情報・通信業', 'サービス業']}  #
    #stock_dict = {'database':'tosho_jpx', 'group_type':'33業種区分', 'group_name':['情報・通信業']}  #
    #stock_dict = {'database':'tosho_jpx', 'group_type':'33業種区分', 'group_name':['サービス業']}  #
    #stock_dict = {'database':'tosho_jpx', 'group_type':'33業種区分', 'group_name':['小売業', '化学', '食料品', '医薬品']}  #
    #stock_dict = {'database':'tosho_jpx', 'group_type':'33業種区分', 'group_name':['小売業']}  #
    #stock_dict = {'database':'tosho_jpx', 'group_type':'33業種区分', 'group_name':['卸売業', '電気機器', 'その他製品']}  #
    #stock_dict = {'database':'tosho_jpx', 'group_type':'33業種区分', 'group_name':['卸売業']}  #候補
    #stock_dict = {'database':'tosho_jpx', 'group_type':'33業種区分', 'group_name':['電気機器']}  #
    #stock_dict = {'database':'tosho_jpx', 'group_type':'33業種区分', 'group_name':['機械', '輸送用機器', '鉄鋼', 'ゴム製品']}  #
    #stock_dict = {'database':'tosho_jpx', 'group_type':'33業種区分', 'group_name':['機械']}  #
    stock_dict = {'database':'tosho_jpx', 'group_type':'33業種区分', 'group_name':['化学']}  #候補
    #stock_dict = {'database':'tosho_jpx', 'group_type':'33業種区分', 'group_name':['建設業', '金属製品']}  #
    #stock_dict = {'database':'tosho_jpx', 'group_type':'33業種区分', 'group_name':['建設業']}  #
    #stock_dict = {'database':'tosho_jpx', 'group_type':'33業種区分', 'group_name':['不動産業']}  #
    #stock_dict = {'database':'tosho_jpx', 'group_type':'33業種区分', 'group_name':['食料品']}  #
    #stock_dict = {'database':'tosho_jpx', 'group_type':'33業種区分', 'group_name':['その他製品']}  #
    #stock_dict = {'database':'tosho_jpx', 'group_type':'33業種区分', 'group_name':['輸送用機器', 'ゴム製品', '金属製品', 'ガラス・土石製品']}  #
    #stock_dict = {'database':'tosho_jpx', 'group_type':'33業種区分', 'group_name':['輸送用機器', 'ゴム製品']}  #
    #stock_dict = {'database':'tosho_jpx', 'group_type':'33業種区分', 'group_name':['輸送用機器']}  #
    #stock_dict = {'database':'tosho_jpx', 'group_type':'33業種区分', 'group_name':['金属製品', 'ガラス・土石製品', '鉄鋼', '非鉄金属']}  #
    #stock_dict = {'database':'tosho_jpx', 'group_type':'33業種区分', 'group_name':['金属製品', 'ガラス・土石製品']}  #候補
    #stock_dict = {'database':'tosho_jpx', 'group_type':'33業種区分', 'group_name':['金属製品']}  #候補
    #stock_dict = {'database':'tosho_jpx', 'group_type':'33業種区分', 'group_name':['銀行業', '証券、商品先物取引業']}
    #stock_dict = {'database':'tosho_jpx', 'group_type':'33業種区分', 'group_name':['銀行業']}  #候補少ない↓
    #stock_dict = {'database':'tosho_jpx', 'group_type':'33業種区分', 'group_name':['医薬品']}  #NG
    #stock_dict = {'database':'tosho_jpx', 'group_type':'33業種区分', 'group_name':['陸運業', '倉庫・運輸関連業']}  #
    #stock_dict = {'database':'tosho_jpx', 'group_type':'33業種区分', 'group_name':['陸運業']}  #
    #stock_dict = {'database':'tosho_jpx', 'group_type':'33業種区分', 'group_name':['ガラス・土石製品']}  #
    #stock_dict = {'database':'tosho_jpx', 'group_type':'33業種区分', 'group_name':['繊維製品', 'パルプ・紙']}  #
    #stock_dict = {'database':'tosho_jpx', 'group_type':'33業種区分', 'group_name':['繊維製品']}  #
    #stock_dict = {'database':'tosho_jpx', 'group_type':'33業種区分', 'group_name':['精密機器']}  #NG
    #stock_dict = {'database':'tosho_jpx', 'group_type':'33業種区分', 'group_name':['鉄鋼']}  #NG
    #stock_dict = {'database':'tosho_jpx', 'group_type':'33業種区分', 'group_name':['倉庫・運輸関連業', '海運業', '空運業']}  #
    #stock_dict = {'database':'tosho_jpx', 'group_type':'33業種区分', 'group_name':['倉庫・運輸関連業']}  #
    #stock_dict = {'database':'tosho_jpx', 'group_type':'33業種区分', 'group_name':['非鉄金属']}  #NG

    #TOPIX採用銘柄の業種
    #250以下　：　サービス業。情報・通信業。小売業。卸売業。電気機器。化学。機械。
    #100以下　：　建設業。食料品。銀行業。不動産業。輸送用機器。その他製品。陸運業。金属製品。
    # 40以下　：　繊維製品。医薬品。ガラス・土石製品。精密機器。鉄鋼。その他金融業。
    # 25以下　：　非鉄金属。倉庫・運輸関連業。証券、商品先物取引業。電気・ガス業。
    # 15以下　：　パルプ・紙。ゴム製品。石油・石炭製品。水産・農林業。保険業。海運業。鉱業。空運業。
    #stock_dict = {'database':'topix_jpx', 'group_type':'ニューインデックス区分', 'group_name':['TOPIX Core30', 'TOPIX Large70', 'TOPIX Mid400']}
    #stock_dict = {'database':'topix_jpx', 'group_type':'ニューインデックス区分', 'group_name':['TOPIX Core30', 'TOPIX Large70']}  #NG
    #stock_dict = {'database':'topix_jpx', 'group_type':'業種', 'group_name':['卸売業']}  #使わない
    #stock_dict = {'database':'topix_jpx', 'group_type':'業種', 'group_name':['化学']}  #
    #stock_dict = {'database':'topix_jpx', 'group_type':'業種', 'group_name':['輸送用機器']}  #使わない
    #stock_dict = {'database':'topix_jpx', 'group_type':'業種', 'group_name':['金属製品', 'ガラス・土石製品', '鉄鋼', '非鉄金属']}  #
    #stock_dict = {'database':'topix_jpx', 'group_type':'業種', 'group_name':['金属製品', 'ガラス・土石製品']}  #使わない
    #stock_dict = {'database':'topix_jpx', 'group_type':'業種', 'group_name':['金属製品']}  #NG
    #stock_dict = {'database':'topix_jpx', 'group_type':'業種', 'group_name':['ガラス・土石製品']}  #

    #日経225社
    # 60以下　：　素材。技術。資本財・その他。消費。金融。運輸・公共。
    #stock_dict = {'database':'n225_nikkei', 'group_type':'全銘柄', 'group_name':['日経225']}  #候補
    #stock_dict = {'database':'n225_nikkei', 'group_type':'セクター', 'group_name':['技術']}  #NG
    #stock_dict = {'database':'n225_nikkei', 'group_type':'セクター', 'group_name':['素材']}  #NG

    #ETF
    # 50以下　：　外国株。日本株（テーマ別）。日本株（市場別）。レバレッジ型・インバース型。不動産（REIT）。
    # 20以下　：　商品(外国投資法人債券)。日本株（業種別）。外国債券。商品・商品指数。日本株（規模別）。エンハンスト型。国内債券。
    #stock_dict = {'database':'tosho_etf', 'group_type':'全銘柄', 'group_name':['全ETF']}  #
    #stock_dict = {'database':'tosho_etf', 'group_type':'連動対象カテゴリー', 'group_name':['外国株', '日本株（テーマ別）']}  #候補
    #stock_dict = {'database':'tosho_etf', 'group_type':'連動対象カテゴリー', 'group_name':['外国株']}  #NG
    
    print(stock_dict)


    reinvest = False  #統計データを取り直すかどうか
    train_months = 5*12  #学習用データの月数
    test_months = 6  #テストデータの月数
    #condition = 'adf小'
    #condition = 'adf大'
    condition = 'adf判定無し'

    spq = 100  #最小購入単位
    win1 = 1
    win2 = 120  #120日くらい
    num_pairs = 20  #投資先の数
    fund = 1.0*10**6  #1ペアに使う資金
    #cutoff2 = 0.001
    cutoff2 = 0.005
    #cutoff2 = 0.01
    losscut=0.1

    #基準日から過去に遡る
    df_asset_all_join = pd.DataFrame()
    delta_max = 10*12  #
    date_ref_start = datetime.datetime(2020, 6, 1)
    for delta in range (0, delta_max, 2):
        date_ref = date_ref_start -relativedelta.relativedelta(months=delta)

        date_min = date_ref -relativedelta.relativedelta(months=train_months)  #months月前
        date_max = date_ref +relativedelta.relativedelta(months=test_months)  #months月後

        #ペア候補を作る
        df_pair_all, df_price = make_stat_database(stock_dict, date_ref, date_min, date_max,
                condition, cutoff2=cutoff2, reinvest=reinvest, show=True)
        #df_close = df_price['Close']
        print(df_pair_all)

        #バックテスト
        df_asset_all = calc_backtest(stock_dict, df_pair_all, df_price, date_ref, date_min, date_max,
                condition, spq, fund, num_pairs, cutoff2, win1, win2, losscut, show=True)
        print(stock_dict)

        if (len(df_asset_all_join.index) != 0):  #銘柄情報まとめデータに値がある時
            try:
                date_bound = df_asset_all.index[-1] +datetime.timedelta(days=1)
                df_asset_all_join[date_bound:] += df_asset_all.iloc[-1]  #最終損益を足す
                df_asset_all_join = df_asset_all_join.add(df_asset_all, fill_value=0)
            except Exception as e:
                print("エラー情報\n" + traceback.format_exc())
        else:  #
            df_asset_all_join = df_asset_all
        print('profit_all_join = ' +str(df_asset_all_join['profit'].dropna().iloc[-1]))
        print()

    print(df_asset_all_join)
    print(stock_dict)

    date_min = date_ref_start -relativedelta.relativedelta(months=delta_max)
    date_max = date_ref_start +relativedelta.relativedelta(months=test_months)
    filename1 = stock_dict['group_type'] +'_' +'-'.join(stock_dict['group_name'])
    filename2 = '_cutoff' +str(cutoff2)[2:] +'_win' +str(win1)+'-' +str(win2)
    filename3 = '_spq' +str(spq) +'_pair' +str(num_pairs) +'_losscut' +str(losscut)[2:] +'_'
    filename4 = date_min.strftime('%Y%m%d') +'-' +date_max.strftime('%Y%m%d') +'_join_' +condition
    file_relative_path = os.path.dirname(__file__)
    png_relative_path = r'../../inout_data/pair_img/' +filename1 +filename2 +filename3 +filename4 +r'.png'
    stat_png_path = os.path.join(file_relative_path, png_relative_path)

    title1 = '「' +'-'.join(stock_dict['group_name']) +'」内での売買結果 ： '
    title2 = 'cutoff=' +str(cutoff2) +'、pair=' +str(num_pairs) +'、win=' +str(win2)
    title = title1 +title2
    show_trade(df_asset_all_join, title, stat_png_path)


    #計算時間の表示
    compute_time = time.time() -compute_time
    print ('Calculation time: {:0.5f}[sec]'.format(compute_time))

#https://developers.refinitiv.com/en/article-catalog/article/introduction-to-equity-pair-trading
import os, sys, datetime
from pprint import pprint
import numpy as np
import pandas as pd
import statsmodels
import statsmodels.api as sm
from statsmodels.tsa.stattools import adfuller, coint
from statsmodels.tsa.ar_model import AutoReg
#from statsmodels.stats.diagnostic import het_breuschpagan
#import numba  #最適化ライブラリ



#1つのセクター内の全銘柄ペアに対して共和分検定する
#@numba.jit  #JITで最適化
def find_coint_pairs(df_price, cutoff=0.01, show=False):
    stock_code = df_price.columns
    mat_p_coint = np.ones((len(df_price.columns), len(df_price.columns)))

    ##各銘柄の単位根検定
    dict_p_adf = {}
    for i in range(len(df_price.columns)):
        try:
            result_adf = adfuller(df_price[stock_code[i]].dropna())
            dict_p_adf[stock_code[i]] = result_adf[1]
        except Exception as e:
            #import traceback
            #print("エラー情報\n" + traceback.format_exc())
            pass
    #pprint(dict_p_adf)

    #ペアトレードをする銘柄コードを取り出す
    df_pair_all = pd.DataFrame()
    for i in range(len(df_price.columns)):
        for j in range(i+1, len(df_price.columns)):
            #銘柄コードは株価が大きい順にしておく
            if (df_price[stock_code[j]].iloc[-1] <= df_price[stock_code[i]].iloc[-1]):
                code1 = stock_code[i]
                code2 = stock_code[j]
            else:
                code1 = stock_code[j]
                code2 = stock_code[i]

            #変数を内部結合
            df_merge = pd.merge(df_price[code1], df_price[code2], 
                                left_index=True, right_index=True, how='inner').dropna()
            #print(df_merge)

            #元データの90%以上データがあったら検定する
            if(0.9 < len(df_merge.index)/len(df_price.index)):
                #それぞれをADF（単位根）検定
                p_adf1 = dict_p_adf[code1]
                p_adf2 = dict_p_adf[code2]
                
                df_ratio = df_merge[code1]/df_merge[code2]  
                #df_ratio = df_merge[code1] -df_merge[code2]  

                #スプレッドに対するADF（単位根）検定
                result_adf_sp = adfuller(df_ratio)

                #共和分検定
                result_coint_aic = coint(df_merge[code1], df_merge[code2], autolag="aic")
                result_coint_bic = coint(df_merge[code1], df_merge[code2], autolag="bic")
                mat_p_coint[i, j] = result_coint_aic[1]  #p値

                #相関係数
                corr = df_merge.corr()[code1][code2]
                #DoD1 = df_merge[code1].pct_change()
                #DoD2 = df_merge[code2].pct_change()
                #corr = DoD1.corr(DoD2)
                
                #自己回帰モデル。AR(1)
                result_ar = AutoReg(df_ratio.values, lags=[1], old_names=False).fit()
                coef_ar = result_ar.params[1]  #独立変数の係数が小さいほど平均回帰が早い。1以下なら定常過程。
                #predictions = result_ar.predict(start=0, end=len(df_ratio.index), dynamic=False)
                #resid = df_ratio.values -predictions.dropna().values
                #plt.plot(resid)
                #plt.show()
                
                #p値が閾値未満で有意に共和分関係にあるペアを保存
                #ADF検定、共和分検定、相関係数、AR(1)モデルの係数
                if (result_coint_aic[1]<cutoff and result_coint_bic[1]<cutoff and corr<(1-cutoff) and coef_ar<1):
                    txt1 = code1 +", " +code2 +" -> " +"corr=" +'{:.2f}'.format(corr)
                    txt2 = ", adf1=" +'{:.2f}'.format(p_adf1) +", adf2=" +'{:.2f}'.format(p_adf2)
                    txt3 = ", adf=" +'{:.4f}'.format(result_adf_sp[1]) +", coint_aic=" +'{:.4f}'.format(result_coint_aic[1])
                    txt4 = ", coint_bic=" +'{:.4f}'.format(result_coint_bic[1])
                    print(txt1 +txt2 +txt3 +txt4)

                    df_pair = pd.DataFrame()
                    df_pair["code1"] = [code1]
                    df_pair["code2"] = [code2]

                    df_pair["mean1"] = [df_merge[code1].iloc[-240:].mean()]  #直近の株価
                    df_pair["mean2"] = [df_merge[code2].iloc[-240:].mean()]  #直近の株価
                    df_pair["std1"] = [df_merge[code1].iloc[-240:].std()]  #
                    df_pair["std2"] = [df_merge[code2].iloc[-240:].std()]  #

                    df_pair["corr"] = [corr]
                    df_pair["coef_ar"] = [coef_ar]

                    #df_pair["p_adf1"] = [result_adf1[1]]  #p値
                    #df_pair["p_adf2"] = [result_adf2[1]]  #p値
                    df_pair["p_adf1"] = [p_adf1]  #p値
                    df_pair["p_adf2"] = [p_adf2]  #p値

                    df_pair["p_adf"] = [result_adf_sp[1]]  #p値
                    #df_pair["cri_adf"] = [result_adf_sp[0]]
                    #df_pair["t1_adf"] = [result_adf_sp[4]['1%']]
                    #df_pair["t1-cri_adf"] = [result_adf_sp[4]['1%'] -result_adf[0]]

                    df_pair["p_coint_aic"] = [result_coint_aic[1]]  #p値
                    #df_pair["cri_coint_aic"] = [result_coint_aic[0]]
                    #df_pair["t1_coint_aic"] = [result_coint_aic[2][0]]  #1%
                    #df_pair["t1-cri_coint_aic"] = [result_coint_aic[2][0] -result_coint_aic[0]]

                    df_pair["p_coint_bic"] = [result_coint_bic[1]]  #p値
                    
                    if (len(df_pair_all.index) != 0):  #まとめデータに値がある時
                        df_pair_all = df_pair_all.append(df_pair, ignore_index=True)
                    else:  #
                        df_pair_all = df_pair

    return df_pair_all, mat_p_coint



if (__name__ == "__main__"):
    sys.path.append('..')
    from pair_data import *
    from pair_show import *


    #stock_dict = {'database':'tosho_jpx', 'group_type':'17業種区分', 'group_name':['素材・化学']}  #候補
    #stock_dict = {'database':'tosho_jpx', 'group_type':'17業種区分', 'group_name':['鉄鋼・非鉄']}
    stock_dict = {'database':'tosho_jpx', 'group_type':'33業種区分', 'group_name':['繊維製品']}
    #stock_dict = {'database':'topix_jpx', 'group_type':'ニューインデックス区分', 'group_name':['TOPIX Core30']}

    stock_list = get_stock_code(stock_dict, show=True)



    #date_max = datetime.date.today()
    date_ref = datetime.datetime(2019, 6, 1)  #4/1、7/1、10/1、1/1にする
    #date_min = date_ref -datetime.timedelta(days=len_train)  #days日前
    #date_max = date_ref +datetime.timedelta(days=len_test)  #days日後
    date_min = date_ref -relativedelta.relativedelta(months=5*12) #学習用データの期間を引く
    date_max = date_ref +relativedelta.relativedelta(months=6) #テストデータの期間を足す

    #株価データ取得
    df_price = get_stock_price(stock_list, date_min, date_max, show=True)

    #終値を使う場合
    df_close = df_price['Close']
    
    #学習データ
    df_train_close = df_close[date_min:date_ref-datetime.timedelta(days=1)]  #境界の日付を含めた過去のデータ
    print('df_train_close =')
    print(df_train_close)
    print(df_close[date_ref:date_max])
    print()



    cutoff = 0.01

    #ペア探索
    df_pair_all, mat_p_coint = find_coint_pairs(df_train_close, cutoff=cutoff, show=True)
    df_pair_all = df_pair_all.sort_values(['corr'], ascending=False)  #並び替え
    print(df_pair_all)

    #株式の各ペア間の共和分検定のp値を示すヒートマップ
    if (len(stock_list)<50):
        title = '「' +'・'.join(stock_dict['group_name']) +'」内での共和分検定'
        show_heatmap(mat_p_coint, stock_list, title)


import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns



def show_zscore(data, title, sigma=2):
    data.plot(figsize=(12,6))
    plt.suptitle(title)

    plt.axhline(data.mean())
    plt.axhline(0, color='black')
    plt.axhline(sigma, color='red')
    plt.axhline(-sigma, color='green')
    plt.show()



def show_buysell(df_trade, title, pair_code1, pair_code2):
    long_signal = 0*df_trade['price1'].copy()
    short_signal = 0*df_trade['price1'].copy()
    settle_signal = 0*df_trade['price1'].copy()

    #lonshoが出た時、price1を買い、price2を売る
    long_signal[df_trade['jadge']=='lonsho'] = df_trade['price1'][df_trade['jadge']=='lonsho']
    short_signal[df_trade['jadge']=='lonsho'] = df_trade['price2'][df_trade['jadge']=='lonsho']

    #sholonが出た時、price1を売り、price2を買う
    short_signal[df_trade['jadge']=='sholon'] = df_trade['price1'][df_trade['jadge']=='sholon']
    long_signal[df_trade['jadge']=='sholon'] = df_trade['price2'][df_trade['jadge']=='sholon']

    settle_signal[df_trade['jadge']=='settle'] = \
            ( df_trade['price1'][df_trade['jadge']=='settle'] +df_trade['price2'][df_trade['jadge']=='settle'] )/2

    #0以外の値を残す
    long_signal = long_signal[long_signal!=0]
    short_signal = short_signal[short_signal!=0]
    settle_signal = settle_signal[settle_signal!=0]

    if(len(settle_signal)!=0):
        plt.figure(figsize=(12,6))
        plt.suptitle(title)
        df_trade['price1'].plot(color='b', label=pair_code1)
        df_trade['price2'].plot(color='c', label=pair_code2)

        long_signal.plot(color='g', linestyle='None', marker='^', label='Buy Signal')
        short_signal.plot(color='r', linestyle='None', marker='^', label='Sell Signal')
        settle_signal.plot(color='k', linestyle='None', marker='^', label='Settle Signal')

        plt.legend(loc='best')  #
        plt.show()



def show_trade(df_trade, title, stat_png_path):
    fig = plt.figure(figsize=(12,8))
    plt.rcParams["font.family"] = "IPAexGothic" #全体のフォントを設定
    plt.suptitle(title)

    ###グラフ上段
    ax = fig.add_subplot(2, 1, 1)
    plt.plot(df_trade.index, df_trade["profit"], lw=1, label="profit")  #
    plt.xlabel('Date')
    plt.ylabel('Money')
    plt.grid(which='major',color='gray',linestyle='-')  #主目盛
    plt.axhline(0, color='#000000')  #y=0の線
    plt.legend(loc='best')  #凡例(グラフラベル)を表示
    
    ###グラフ下段
    ax = fig.add_subplot(2, 1, 2)
    #plt.plot(df_trade.index, df_trade["asset"], lw=1, label="asset")  #
    #plt.plot(df_trade.index, df_trade["fund"], lw=1, label="fund")  #
    plt.plot(df_trade.index, df_trade["position"], lw=1, label="position")  #
    plt.xlabel('Date')
    plt.ylabel('Money')
    plt.grid(which='major',color='gray',linestyle='-')  #主目盛
    plt.axhline(0, color='#000000')  #y=0の線
    plt.legend(loc='best')  #凡例(グラフラベル)を表示

    plt.savefig(stat_png_path)
    #plt.show()



if (__name__ == "__main__"):
    pass

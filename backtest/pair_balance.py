import numpy as np
import pandas as pd



#収支を計算
def calc_balance(df_trade, fund0, int_rate=0.03, fee=0.001, delay=1):
    #トレード前の初期状態
    asset = fund0
    profit = 0
    df_trade["asset"] = fund0
    df_trade["profit"] = 0
    #print(df_trade)

    #トレードをシミュレーション
    for date in range(len(df_trade.index)):
        #エントリー時の処理（delay日前にシグナル、）
        if ((df_trade["jadge"].iloc[date-delay]=="lonsho" or df_trade["jadge"].iloc[date-delay]=="sholon") and
                df_trade["position"].iloc[date]!=0):
            pos1 = df_trade["price1"].iloc[date]*df_trade["hold1"].iloc[date-delay]
            pos2 = df_trade["price2"].iloc[date]*df_trade["hold2"].iloc[date-delay]
            profit = -(pos1 +pos2)
            asset += profit -fee*fund0  #損益と売買手数料とスリッページを追加。

        #ポジション解消（2日目以降）
        if (1<=date and df_trade["jadge"].iloc[date-delay]=="settle" and 
                df_trade["position"].iloc[date-1]!=0):
            pos1 = df_trade["price1"].iloc[date]*df_trade["hold1"].iloc[date-delay-1]
            pos2 = df_trade["price2"].iloc[date]*df_trade["hold2"].iloc[date-delay-1]
            profit = +(pos1 +pos2)
            asset += profit -fee*fund0  #損益と売買手数料とスリッページを追加。

        #金利と貸株料を引く。3%
        if (df_trade["position"].iloc[date]!=0):
            asset -= int(int_rate/365 *df_trade["position"].iloc[date])

        df_trade["asset"].iloc[date] = asset
        df_trade["profit"].iloc[date] = asset -fund0
    #print(300)

    return df_trade



if (__name__ == "__main__"):
    pass

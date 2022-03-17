import numpy as np
import pandas as pd



#注文量を計算
def calc_order(df_trade, fund0, spq=100, delay=1, test=True):
    #トレード前の初期状態
    fund = fund0
    position = 0.0
    hold1 = 0.0
    hold2 = 0.0
    df_trade["fund"] = fund0  #資金
    df_trade["position"] = 0
    #df_trade["hold1"] = 0
    #df_trade["hold2"] = 0

    #トレードをシミュレーション
    for date in range(delay, len(df_trade.index)):
        pos1_min = df_trade["price1"].iloc[date-delay]
        pos2_min = df_trade["price2"].iloc[date-delay]*df_trade["ratio"].iloc[date-delay]
        pos_basic = int(pos1_min +pos2_min)*spq  #最小ポジション
        fp_ratio = fund/pos_basic  #ポジションと資金の比率
        
        #σ < z-scoreでロング・ショート（ある時期まで売買）
        #if (df_trade["jadge"].iloc[date-delay]=="lonsho" and date<=len(df_trade)/3):
        if (df_trade["jadge"].iloc[date-delay]=="lonsho" and pos_basic<fund and date<=40):  #約2か月
            hold1 += spq*round(1 *fp_ratio)  #買い
            hold2 += -spq*round(df_trade["ratio"].iloc[date-delay] *fp_ratio)  #売り
            fund -= df_trade["price1"].iloc[date]*abs(hold1) +df_trade["price2"].iloc[date]*abs(hold2)
            position += df_trade["price1"].iloc[date]*abs(hold1) +df_trade["price2"].iloc[date]*abs(hold2)

        #z-score < -σでショート・ロング（ある時期まで売買）
        #elif (df_trade["jadge"].iloc[date-delay]=="sholon" and date<=len(df_trade)/3):
        elif (df_trade["jadge"].iloc[date-delay]=="sholon" and pos_basic<fund and date<=40):  #約2か月
            hold1 += -spq*round(1 *fp_ratio)  #売り
            hold2 += spq*round(df_trade["ratio"].iloc[date-delay] *fp_ratio)  #買い
            fund -= df_trade["price1"].iloc[date]*abs(hold1) +df_trade["price2"].iloc[date]*abs(hold2)
            position += df_trade["price1"].iloc[date]*abs(hold1) +df_trade["price2"].iloc[date]*abs(hold2)
        
        #ポジション解消（最後は強制決済）
        elif (df_trade["jadge"].iloc[date-delay]=="settle"):
        #elif (df_trade["jadge"].iloc[date-delay]=="settle" or (test==True and position!=0 and date==len(df_trade)-1)):
            df_trade["jadge"].iloc[date-delay]="settle"

            #profit = -(df_trade["price1"].iloc[date]*hold1 +df_trade["price2"].iloc[date]*hold2)
            fund += position  #ポジション分が資金に戻る
            #fund += position +profit  #ポジション分と損益が資金に戻る
            position = 0  #ポジション全解消
            hold1 = 0
            hold2 = 0

        df_trade["fund"].iloc[date] = fund
        df_trade["position"].iloc[date] = position
        #df_trade["hold1"].iloc[date] = hold1
        #df_trade["hold2"].iloc[date] = hold2

    return df_trade



if (__name__ == "__main__"):
    pass

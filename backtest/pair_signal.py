import numpy as np
import pandas as pd
import warnings



#
def calc_signal(price1, price2, win1, win2, fund=1.0*10**6, spq=100, 
        delay=0, sigma=2, pos_limit=60, losscut=0.1, test=True):
    df_trade = pd.DataFrame()
    df_trade["price1"] = price1.copy()
    df_trade["price2"] = price2.copy()
    
    #移動平均と移動標準偏差を計算し、価格の比からzscoreを出す
    df_trade["ratio"] = price1/price2  #価格の比率
    ma1 = df_trade["ratio"].rolling(window=win1, center=False).mean()
    ma2 = df_trade["ratio"].rolling(window=win2, center=False).mean()
    std2 = df_trade["ratio"].rolling(window=win2, center=False).std()
    df_trade["zscore"] = (ma1 -ma2)/std2  #'''

    #移動平均乖離率で判断する場合（zスコアの引き算）
    '''ma1 = df_trade["price1"].rolling(window=win2, center=False).mean()
    ma2 = df_trade["price2"].rolling(window=win2, center=False).mean()
    df_trade["zscore"] = 100*( (df_trade["price1"] -ma1)/ma1 -(df_trade["price2"] -ma2)/ma2)
    #'''

    df_trade = df_trade.dropna()

    #トレード前の初期状態
    df_trade["jadge"] = "wait"
    df_trade["hold1"] = 0
    df_trade["hold2"] = 0
    hold1 = 0
    hold2 = 0
    position = False
    sale_price_profit = 0
    trading_halt = False


    #シグナルを計算
    #pos_limit = 1.0*win2
    pos_count = 0
    for date in range(len(df_trade.index)):
        #現在の損益
        pos1 = df_trade["price1"].iloc[date-delay]*hold1
        pos2 = df_trade["price2"].iloc[date-delay]*hold2
        current_profit = pos1 +pos2
        #if (position == True):
        #    print(df_trade["price1"].iloc[date-delay], df_trade["price2"].iloc[date-delay])
        #    print(df_trade.index[date], 'current_profit=', current_profit, 'sale_price_profit=', sale_price_profit)

        pos1_min = df_trade["price1"].iloc[date-delay]
        pos2_min = df_trade["price2"].iloc[date-delay]*df_trade["ratio"].iloc[date-delay]
        pos_basic = int(pos1_min +pos2_min)*spq  #最小ポジション
        fp_ratio = fund/pos_basic  #ポジションと資金の比率

        
        #ポジションがあれば、ポジション解消判定をする
        if (position==True):
            pos_count += 1  #ポジションを連続で持っている日数を数える

            if(current_profit -sale_price_profit < -losscut*fund):  #一定額損したら
            #if(2*sigma < abs(df_trade["zscore"].iloc[date-delay])):  #売買ラインの2倍を越えたら解消
                df_trade["jadge"].iat[date] = "settle"
                position = False
                pos_count = 0
                sale_price_profit = 0
                hold1 = 0
                hold2 = 0

                trading_halt=True  #取引対象から外す

            #「符号が変わった」ならば、ポジション解消する
            #elif(df_trade["zscore"].iloc[date-delay-1]*df_trade["zscore"].iloc[date-delay] < 0):
            #elif(df_trade["zscore"].iloc[date-delay-1]*df_trade["zscore"].iloc[date-delay] < 0 or 
            #        abs(df_trade["zscore"].iloc[date-delay]) < 0.5*sigma):  #売買ラインの半分以下になったら解消
            elif(df_trade["zscore"].iloc[date-delay-1]*df_trade["zscore"].iloc[date-delay] < 0 or 
                    pos_limit<=pos_count):  #一定の日数が過ぎたら解消
                df_trade["jadge"].iat[date] = "settle"
                position = False
                pos_count = 0
                sale_price_profit = 0
                hold1 = 0
                hold2 = 0
            
            #「テスト時の取引最終日」ならば、ポジション解消
            elif(test==True and date==len(df_trade)-2):
                df_trade["jadge"].iat[date] = "settle"
                position = False
                pos_count = 0
                sale_price_profit = 0
                hold1 = 0
                hold2 = 0
            
            #保持し続ける
            else:
                df_trade["jadge"].iat[date] = "hold"
        
        
        #「売買対象外でない」かつ「一定期間以内」ならば、エントリー判定をする
        #elif (trading_halt==False and date<=40):
        elif (trading_halt==False):
            #z-score < -σ
            #if(df_trade["zscore"].iloc[date-delay] < -sigma):  #複数回買う
            if (position==False and df_trade["zscore"].iloc[date-delay] < -sigma):  #1回しか買わない
            #if ((position==False and df_trade["zscore"].iloc[date-delay]<-sigma) or
            #       df_trade["zscore"].iloc[date-delay]<-3):  #3σ越えたら複数買う
                df_trade["jadge"].iat[date] = "lonsho"
                hold1 += spq*round(1 *fp_ratio)  #買い
                hold2 += -spq*round(df_trade["ratio"].iloc[date] *fp_ratio)  #売り

                position = True
                pos1 = df_trade["price1"].iloc[date]*hold1
                pos2 = df_trade["price2"].iloc[date]*hold2
                sale_price_profit = (pos1 +pos2)
                #print(df_trade.index[date], 'sale_price_profit=', sale_price_profit)
        
            #σ < z-score
            #elif(sigma < df_trade["zscore"].iloc[date-delay]):  #複数回買う
            elif(position==False and sigma < df_trade["zscore"].iloc[date-delay]):  #1回しか買わない
            #elif((position==False and sigma<df_trade["zscore"].iloc[date-delay]) or
            #       3<df_trade["zscore"].iloc[date-delay]):  #3σ越えたら複数買う
                df_trade["jadge"].iat[date] = "sholon"
                hold1 += -spq*round(1 *fp_ratio)  #売り
                hold2 += spq*round(df_trade["ratio"].iloc[date] *fp_ratio)  #買い
            
                position = True
                pos1 = df_trade["price1"].iloc[date]*hold1
                pos2 = df_trade["price2"].iloc[date]*hold2
                sale_price_profit = (pos1 +pos2)
                #print(df_trade.index[date], 'sale_price_profit=', sale_price_profit)
        
        df_trade["hold1"].iloc[date] = hold1
        df_trade["hold2"].iloc[date] = hold2


    return df_trade



#
def calc_signal1(price1, price2, win1, win2, delay=0, sigma=2, test=True):
    df_trade = pd.DataFrame()
    df_trade["price1"] = price1.copy()
    df_trade["price2"] = price2.copy()
    
    #移動平均と移動標準偏差を計算し、価格の比からzscoreを出す
    df_trade["ratio"] = price1/price2  #価格の比率
    ma1 = df_trade["ratio"].rolling(window=win1, center=False).mean()
    ma2 = df_trade["ratio"].rolling(window=win2, center=False).mean()
    std2 = df_trade["ratio"].rolling(window=win2, center=False).std()
    df_trade["zscore"] = (ma1 -ma2)/std2  #'''

    #移動平均乖離率で判断する場合（zスコアの引き算）
    '''ma1 = df_trade["price1"].rolling(window=win2, center=False).mean()
    ma2 = df_trade["price2"].rolling(window=win2, center=False).mean()
    df_trade["zscore"] = 100*( (df_trade["price1"] -ma1)/ma1 -(df_trade["price2"] -ma2)/ma2)
    #'''

    #トレード前の初期状態
    df_trade["jadge"] = "wait"
    hold1 = 0
    hold2 = 0
    position = False
    sale_price_profit = 0
    trading_halt = False


    #シグナルを計算
    sigma = 2.0
    pos_limit = 1.0*win2
    pos_count = 0

    spq = 100
    fund = 1.0*10**6
    for date in range(1, len(df_trade.index)):
        #現在の損益
        pos1 = df_trade["price1"].iloc[date-delay]*hold1
        pos2 = df_trade["price2"].iloc[date-delay]*hold2
        current_profit = pos1 +pos2
        #if (position == True):
        #    print(df_trade.index[date], 'current_profit=', current_profit, 'sale_price_profit=', sale_price_profit)

        pos1_min = df_trade["price1"].iloc[date-delay]
        pos2_min = df_trade["price2"].iloc[date-delay]*df_trade["ratio"].iloc[date]
        pos_basic = int(pos1_min +pos2_min)*spq  #最小ポジション
        fp_ratio = fund/pos_basic  #ポジションと資金の比率

        #大損したら取引対象から外す
        if(current_profit -sale_price_profit < -0.05*fund):
            trading_halt=True

        #符号が変わった時、ポジションを解消
        if (position==True):
            pos_count += 1  #ポジションを連続で持っている日数を数える


        #if(df_trade["zscore"].iloc[date-delay-1]*df_trade["zscore"].iloc[date-delay]<0):
        if(df_trade["zscore"].iloc[date-delay-1]*df_trade["zscore"].iloc[date-delay]<0 or 
            date==len(df_trade)-1 or current_profit -sale_price_profit < -0.05*fund ):  #一定額損したら
        #if(df_trade["zscore"].iloc[date-delay-1]*df_trade["zscore"].iloc[date-delay]<0 or 
        #    pos_limit<=pos_count):  #一定の日数が過ぎたら解消
        #if( df_trade["zscore"].iloc[date-delay-1]*df_trade["zscore"].iloc[date-delay]<0 or 
        #    abs(df_trade["zscore"].iloc[date-delay]) < 0.5*sigma ):  #売買ラインの半分以下になったら解消
        #if( df_trade["zscore"].iloc[date-delay-1]*df_trade["zscore"].iloc[date-delay]<0 or 
        #    2*sigma < abs(df_trade["zscore"].iloc[date-delay]) ):  #売買ラインの2倍を越えたら解消
            df_trade["jadge"].iat[date] = "settle"
            position = False
        
            pos_count = 0

            sale_price_profit = 0
            hold1 = 0
            hold2 = 0
        
        
        #z-score < -σ
        #if (trading_halt==False and df_trade["zscore"].iloc[date-delay] < -sigma):  #複数回買う
        if (position==False and trading_halt==False and df_trade["zscore"].iloc[date-delay] < -sigma):  #1回しか買わない
        #if ((position==False and df_trade["zscore"].iloc[date-delay] < -sigma) or
        #       df_trade["zscore"].iloc[date-delay]<-3):  #3σ越えたら複数買う
            df_trade["jadge"].iat[date] = "lonsho"
            position = True
        
            hold1 += spq*round(1 *fp_ratio)  #買い
            hold2 += -spq*round(df_trade["ratio"].iloc[date] *fp_ratio)  #売り
            pos1 = df_trade["price1"].iloc[date]*hold1
            pos2 = df_trade["price2"].iloc[date]*hold2
            sale_price_profit = (pos1 +pos2)
            #print(df_trade.index[date], 'sale_price_profit=', sale_price_profit)

        #σ < z-score
        #elif (trading_halt==False and sigma < df_trade["zscore"].iloc[date-delay]):  #複数回買う
        elif (position==False and trading_halt==False and sigma < df_trade["zscore"].iloc[date-delay]):  #1回しか買わない
        #elif (position==False and ((position==False and sigma < df_trade["zscore"].iloc[date-delay]) or
        #       3<df_trade["zscore"].iloc[date-delay])):  #3σ越えたら複数買う
            df_trade["jadge"].iat[date] = "sholon"
            position = True
            
            hold1 += -spq*round(1 *fp_ratio)  #売り
            hold2 += spq*round(df_trade["ratio"].iloc[date] *fp_ratio)  #買い
            pos1 = df_trade["price1"].iloc[date]*hold1
            pos2 = df_trade["price2"].iloc[date]*hold2
            sale_price_profit = (pos1 +pos2)
            #print(df_trade.index[date], 'sale_price_profit=', sale_price_profit)

    return df_trade.dropna()



if (__name__ == "__main__"):
    from pair_show import *

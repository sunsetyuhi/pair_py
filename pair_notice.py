import datetime
import numpy as np
import pandas as pd
from email.mime.text import MIMEText
import smtplib

pd.set_option('display.unicode.east_asian_width', True)  #全角文字幅を考慮して表示

from pair_database import *
from pair_backtest import *



def make_orders(
        stock_dict,
        df_pair_all,
        df_price,
        date_ref,
        date_min,
        date_max,
        condition='adf判定無し',
        spq = 100,  #最小購入単位
        fund = 1.0*10**6,  #1ペアに使う資金
        num_pairs = 50,
        cutoff2 = 0.005,
        win1 = 1,
        win2 = 120,  #80～120日くらい
        losscut = 0.1,
        show = False
    ):
    
    num_pairs = min(num_pairs, len(df_pair_all.index))  #取引するペア数

    df_pair_all = df_pair_all[~df_pair_all['code1'].duplicated()]  #重複銘柄を削除
    df_pair_all = df_pair_all[~df_pair_all['code2'].duplicated()]  #重複銘柄を削除

    df_pair_all = df_pair_all[:num_pairs]  #上から順にペアを抽出
    df_pair_all['profit'] = np.nan


    #抽出したペア群でトレードを実施
    df_trade_all = pd.DataFrame()  #最終日時点の取引情報
    df_close = df_price['Close']
    for pair_index in range(len(df_pair_all.index)):
        try:
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

            #シグナル計算
            df_trade = calc_signal(df_test1, df_test2, win1, win2, fund=10**6, 
                    spq=spq, delay=0, losscut=losscut, test=False)
            df_trade = calc_order(df_trade, fund, spq=spq, delay=1)
            df_trade = calc_balance(df_trade, fund, int_rate=0.03, fee=0.001, delay=1)
            print(df_trade.dropna())

            position_max = int(df_trade['position'].max())
            profit_abs_max = int(abs(df_trade['profit'].max()))
            
            
            #取引情報
            df_trade_end = pd.DataFrame(df_trade.iloc[-1]).T.reset_index()
            df_trade_end = df_trade_end.rename(columns={"index":"date"})  #列名変更
            df_trade_end.insert(1, "code1", pair_code1)
            df_trade_end.insert(2, "code2", pair_code2)
            #銘柄名も入れる
            print(df_trade_end)
            print()
    
    
            #取得した銘柄情報を記録
            if(position_max<1.5*fund and profit_abs_max<0.3*fund):  #極端な取引は無視する
                if (len(df_trade_all.index) != 0):  #まとめデータに値がある時
                    df_trade_all = df_trade_all.append(df_trade_end, ignore_index=True)
                else:  #
                    df_trade_all = df_trade_end
    
        except Exception as e:
            print("エラー情報\n" + traceback.format_exc())
    
    if(show==True):
        print(df_pair_all)
        print(df_trade_all)
        print()

    return df_trade_all



#メッセージ作成
def send_mail(from_addr, from_pass, to_addr, stock_dict, df_trade_all, date_ref, date_max):
    pd.set_option('colheader_justify', 'center')  # <th>内の文字列を真ん中に寄せる

    html_head = f'''
    <head>
        <meta charset="utf-8"/>
        <title>Signal</title>
    '''
    html_style = '''
        <style type="text/css" media="screen">
            .mystyle {
                font-size: 11pt;
                font-family: Arial;
                border-collapse: collapse;
                border: 1px solid silver;
            }

            .mystyle td, th {
                padding: 5px;
            }
        </style>
        <script type="text/javascript">
            $('td:contains("hold")').parent("tr").css("background-color", "#FF0000");
        </script>
    </head>
    <body>
    '''
    html_text1 = '基準' +str(date_ref.strftime('%Y-%m-%d')) +'、profit_all=' +str(int(df_trade_all['profit'].sum()))
    html_table1 = df_trade_all[~(df_trade_all['jadge']=='wait')].to_html(index=False, classes="mystyle")
    html_body1 = '<br>'
    html_table2 = df_trade_all[df_trade_all['jadge']=='wait'].to_html(index=False, classes="mystyle")
    html_end = """</body>"""
    
    body_txt = html_head +html_style +html_text1 +html_table1 +html_body1 +html_table2 +html_end
    #print(body_txt)


    #メール文を作成
    #msg = MIMEText(body_txt)
    msg = MIMEText(body_txt, "html")
    sub_txt1 = '[ペアトレード] ' +str(date_max.strftime('%Y-%m-%d')) +'：基準' +str(date_ref.strftime('%Y-%m-%d'))
    sub_txt2 = '-'.join(stock_dict['group_name']) +"の売買シグナル：利益" +str(int(df_trade_all['profit'].sum())) +'円'
    msg["Subject"] = sub_txt1 +sub_txt2
    msg["From"] = from_addr
    msg["To"] = ','.join(to_addr)  #複数アドレスはカンマ区切りにする
    print('Maked massage.')

    #メール送信
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login(from_addr, from_pass)
    server.send_message(msg)
    print('Sent e-mail.')



if (__name__ == '__main__'):
    #計算の開始時刻を記録
    print ('Calculation start: ', time.ctime())  #計算開始時刻を表示
    compute_time = time.time()  #計算の開始時刻


    #東証上場銘柄の17業種
    #stock_dict = {'database':'tosho_jpx', 'group_type':'17業種区分', 'group_name':['素材・化学']}  #
    #stock_dict = {'database':'tosho_jpx', 'group_type':'17業種区分', 'group_name':['自動車・輸送機']}  #候補

    #東証上場銘柄の33業種
    #stock_dict = {'database':'tosho_jpx', 'group_type':'33業種区分', 'group_name':['卸売業']}  #
    stock_dict = {'database':'tosho_jpx', 'group_type':'33業種区分', 'group_name':['金属製品', 'ガラス・土石製品']}  #候補
    
    print(stock_dict)


    reinvest = False  #統計データを取り直すかどうか
    train_months = 5*12  #学習用データの月数
    #test_months = 1  #テストデータの月数
    condition='adf判定無し'
    
    spq = 1  #最小購入単位
    win1 = 1
    win2 = 120  #120日くらい
    fund = 1.0*10**6  #1ペアに使う資金
    cutoff2 = 0.005
    losscut = 0.15

    #date_ref = datetime.datetime(2021, 2, 1)  #
    #date_ref = datetime.datetime(2021, 4, 1)  #
    date_ref = datetime.datetime(2021, 6, 1)  #
    print('date_ref = ' +str(date_ref.strftime('%Y-%m-%d')))
    
    date_min = date_ref -relativedelta.relativedelta(months=train_months)  #months月前
    date_max = datetime.datetime.today()  #シグナルを出したい日
    #date_max = date_ref +relativedelta.relativedelta(days=2)  #シグナルを出したい日


    #ペア候補を作る
    df_pair_all, df_price = make_stat_database(stock_dict, date_ref, date_min, date_max,
            condition, reinvest=reinvest, show=True)
    #df_close = df_price['Close']
    print(df_pair_all)


    #シグナルを取得
    df_trade_all = make_orders(stock_dict, df_pair_all, df_price, date_ref, date_min, date_max,
            condition, spq, fund, win1=win1, win2=win2, losscut=losscut, show=True)
    print(stock_dict)


    #メール送信
    from_addr = 'address'
    from_pass = 'pass'

    to_addr = ['address1']
    #to_addr = ['address2']
    #to_addr = ['address1', 'address2']

    send_mail(from_addr, from_pass, to_addr, stock_dict, df_trade_all, date_ref, date_max)

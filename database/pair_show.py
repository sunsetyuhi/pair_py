import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns



def show_heatmap(pvalues, stock_list, title):
    fig, ax = plt.subplots(figsize=(12,8))
    plt.rcParams["font.family"] = "IPAexGothic" #全体のフォントを設定
    plt.suptitle(title)
    sns.heatmap(pvalues, xticklabels=stock_list, yticklabels=stock_list, annot=True, cmap='Blues', mask=(1<=pvalues))
    plt.show()



if (__name__ == "__main__"):
    pass

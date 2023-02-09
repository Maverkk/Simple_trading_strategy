#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 25 14:11:37 2023

@author: gaobikai
"""


import numpy as np
import talib as ta 
import pandas as pd
import matplotlib.pyplot as plt

import tushare as ts
import datetime as dt


# stock = ts.get_h_data('600030', '2016-06-01', '2017-06-30')

# stock.sort_index(inplace=True)
# print( stock.head() )




path = '/Users/gaobikai/Desktop/金融/py4fi-master/jupyter36/source/fxcm_eur_usd_eod_data.csv'


# data = data[sym]
# print(data.info())





# stra_index = 
#                0   for cci;  1 for bollinger band
#                2   for SMA + cci

def strategy(stra_index):
    
    if stra_index == 0 :


########################## Strategy CCI ###################################
# ###Calculate CCI
        data = pd.read_csv(path, parse_dates = True, index_col=(0)).dropna()

        data['cci'] = ta.CCI(data['HighBid'], data['LowBid'], data['CloseBid'], timeperiod=300)

        data = data.dropna()
        # print(data.head())
        
        
        
        
        
        # plt.subplot(2, 1, 1)
        # plt.title('CCI Index')
        # plt.gca().axes.get_xaxis().set_visible(False)  #Use the same horizontal axis （两个子图共用一个横坐标）
        # data['CloseBid'].plot( figsize = (10, 8) )
        # plt.legend()
        
        # plt.subplot(2, 1, 2)
        # data['cci'].plot(figsize = (10, 8) )
        # plt.legend()
        # plt.show
        
        
        
        #CCI lag
        data['CCI_lag1'] = data['cci'].shift(1)
        data['CCI_lag2'] = data['cci'].shift(2)
        
        
        data.dropna()
        
        # Strategy signal
        # When  cci_lag2 smaller than -100 and cci_lag1 larger than -100, we buy !
        data['signal'] = np.where( np.logical_and(data['CCI_lag2']<-100 , data['CCI_lag1']>-100), 1, np.nan )
        
        #When cci_lag2 larger than 100 and cci_lag1 smaller than 100, we sell !
        data['signal'] = np.where( np.logical_and(data['CCI_lag2']>100 , data['CCI_lag1']<100), -1, data['signal'])
        
        data['signal'] = data['signal'].fillna(method = 'ffill')
        data['signal'] = data['signal'].fillna(0)
        
        def plot_cci():
            plt.subplot(2, 1, 1)
            plt.title('Price')
            plt.gca().axes.get_xaxis().set_visible(False)  #Use the same horizontal axis （两个子图共用一个横坐标）
            data['CloseBid'].plot( figsize = (10, 8) )
            # plt.legend()
            
            # plt.subplot(2, 1, 2)
            data['signal'].plot(secondary_y=True,marker = 'o' ,linestyle = '', figsize = (10, 8) )
            plt.legend()
            plt.show
            
            
            plt.subplot(2, 1, 2)
            data['cci'].plot( figsize =( 10, 8)  )
        
        
        
        # percentage return
        data['pct_change'] = data['CloseBid'].pct_change()
        
        data['stra_return'] = data['pct_change'] * data['signal'].shift(1)
        
        data['return'] = (data['pct_change'] + 1).cumprod()
        
        data['stra_cum_return'] = (1 + data['stra_return']).cumprod()
        
        
        # plot the return vs stra_return(cci)
        def plot_return_cci():
            data[['return','stra_cum_return']].plot( figsize = (10, 8))
        
        plot_return_cci()
        
    if stra_index == 1:

########################################################
############# strategy bollinger bands ##############

        # print(data.head())

        data = pd.read_csv(path, parse_dates = True, index_col=(0)).dropna()
        
        data['upper'], data['middle'], data['lower'] = ta.BBANDS(data['CloseBid'], timeperiod=300, nbdevup=2, nbdevdn=2, matype=0)
        
        
        def plot_bollinger():
            
            plt.figure(dpi=500)
            plt.plot(figsize  = (10, 8))
            plt.plot( data['CloseBid'] )
            plt.plot(data['upper'], linestyle = '--', label = "upper")
            plt.plot(data['middle'], linestyle = '--' , label = "middle")
            plt.plot(data['lower'], linestyle = '--' , label = "lower")
            plt.legend()
        
        
        # plot_bollinger()
        
        
        ###lag 1 #######
        data['lag1_close'] = data['CloseBid'].shift(1)
        data['lag1_lower'] = data['lower'].shift(1)
        data['lag1_upper'] = data['upper'].shift(1)
        
        ####lag 2 ########
        data['lag2_close'] = data['CloseBid'].shift(2)
        data['lag2_lower'] = data['lower'].shift(2)
        data['lag2_upper'] = data['upper'].shift(2)
        
        
        
        ####signal for bollinger band ##################
        
        #When lag2 < lower band and lag1 > lower band , we long!
        data['signal'] = np.where(np.logical_and( data['lag2_close']<data['lag2_lower'], data['lag1_close'] > data['lag1_lower']), 1, np.nan )
        
        #When lag2 > upper band and lag1 < upper band, we short!
        data['signal'] = np.where(np.logical_and( data['lag2_close']>data['lag2_upper'], data['lag1_close'] < data['lag1_upper']), -1,data['signal'] )
        data['signal'] = data['signal'].fillna(method = 'ffill')
        data['signal'] = data['signal'].fillna(0)
        
        
        
        def plot_signal():
            
            data[['signal','CloseBid']].plot(secondary_y='signal', figsize=(10, 8) )
        
        
        # plot_signal()
        
        
        
        
        #####Calculate the return
        # # percentage return
        data['pct_change'] = data['CloseBid'].pct_change()
        data['stra_return'] = data['pct_change'] * data['signal'].shift(1)
        
        
        data['return'] = (data['pct_change'] + 1).cumprod()
        data['stra_cum_return'] = (1 + data['stra_return']).cumprod()
        
        def plot_return_bollinger():
            data[['return','stra_cum_return','signal']].plot(secondary_y='signal', figsize = (10, 8))
        
        
        plot_return_bollinger() 
        
    if stra_index == 3:
        
        data = pd.read_csv(path, parse_dates = True, index_col=(0)).dropna()

        data['cci'] = ta.CCI(data['HighBid'], data['LowBid'], data['CloseBid'], timeperiod=300)
        data['sma_80'] = ta.SMA(data['CloseBid'], 80)
        data['sma_200'] = ta.SMA(data['CloseBid'], 200)
        
        data = data.dropna()
        
        # data[['CloseBid', 'sma_80','sma_200']].plot(figsize=(10, 8))
        
        # lag1, lag2
        data['lag1_close'] = data['CloseBid'].shift(1);
        data['lag2_close'] = data['CloseBid'].shift(2);
        
        data['lag1_cci'] = data['cci'].shift(1);
        data['lag2_cci'] = data['cci'].shift(2);
        
        data['lag1_sma80'] = data['sma_80'].shift(1)
        data['lag1_sma200'] = data['sma_200'].shift(1)
        
        data['lag2_sma80'] = data['sma_80'].shift(2)
        data['lag2_sma200'] = data['sma_200'].shift(2)
        
        
        
        ##  Signal for mix index     
        #   SMA80 > SMA200 and cci < -100    long  !
        #   SMA80 < SMA200 and cci > 100     short !
        data['signal'] = np.where(np.logical_and( data['lag2_sma80'] < data['lag2_sma200'] \
                                                 , data['lag1_sma80'] > data['lag1_sma200']\
                                                 , data['cci']<-100   ), 1, np.nan )
            
        data['signal'] = np.where(np.logical_and( data['lag2_sma80'] > data['lag2_sma200'] \
                                                 , data['lag1_sma80'] < data['lag1_sma200']\
                                                 , data['cci']>100   ), -1, data['signal'] )
        data['signal'] = data['signal'].fillna(method = 'ffill')
        data['signal'] = data['signal'].fillna(0)
    
        # data[['CloseBid', 'sma_80','sma_200','signal']].plot(secondary_y = 'signal', figsize=(10, 8))
        
        data['pct_change'] = data['CloseBid'].pct_change()
        data['stra_return'] = data['pct_change'] * data['signal'].shift(1)
        
        
        data['return'] = (data['pct_change'] + 1).cumprod()
        data['stra_cum_return'] = (1 + data['stra_return']).cumprod()
 
        def plot_stramix_return():
            data[['return','stra_cum_return','signal']].plot(secondary_y='signal', figsize = (10, 8))
            
        plot_stramix_return()







stra_index = 3
strategy(stra_index)























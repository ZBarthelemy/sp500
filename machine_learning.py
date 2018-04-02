#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr  2 12:39:40 2018

@author: whitestallion
"""

from collections import Counter
import datetime as dt
import numpy as np
import pandas as pd
import pickle

def df_withDateRange(df, date_from, date_to): 
    df['Date'] = pd.to_datetime(df['Date'])
    df = df[(df['Date']>date_from) & (df['Date']<date_to)]
    df['Date'] = df['Date'].dt.strftime('%Y-%m-%d')
    
    return df

def process_data_for_labels(ticker):
    hm_days = 6
    df = pd.read_csv('/Users/whitestallion/Desktop/sp500/sp500_joined_closes.csv') 
    df = df_withDateRange(df, dt.datetime(2009,1,1), dt.datetime(2018,3,31))
    
    tickers = df.columns.values.tolist()
    tickers.remove('Date')
    df.fillna(0, inplace=True)
    
    for i in range(1, hm_days + 1):
        df['{}_{}d'.format(ticker, i)] = (df[ticker].shift(-i) - df[ticker]) / df[ticker]
    
    return tickers, df

def buy_sell_hold(*args):
    cols = [c for c in args]
    requirement = 0.02
    for col in cols:
        if col > requirement:
            return 1
        if col < -requirement:
            return - 1
    return 0
   
def extract_featuresets(ticker):
    tickers, df = process_data_for_labels(ticker)
    
    #alas not enough, yahoo free data fed null strings
    #check the aggregator later and single stock CSV later, perhaps running out of memory making
    #the big matrix
    df.loc[df['BKNG'] == "null", 'BKNG'] = 0
    df.loc[df['UA'] == "null", 'UA'] = 0
    df.loc[df['WELL'] == "null", 'WELL'] = 0
    df.loc[df['BHF'] == "null", 'BHF'] = 0
    df[['BKNG','UA', 'WELL', 'BHF']] = df[['BKNG','UA', 'WELL', 'BHF']].astype(np.float64)
    df.fillna(0, inplace=True)
    
    df['{}_target'.format(ticker)] = list(map(buy_sell_hold,
                                               df['{}_1d'.format(ticker)],
                                               df['{}_2d'.format(ticker)],
                                               df['{}_3d'.format(ticker)],
                                               df['{}_4d'.format(ticker)],
                                               df['{}_5d'.format(ticker)],
                                               df['{}_6d'.format(ticker)]))
    
    vals = df['{}_target'.format(ticker)].values.tolist()
    str_vals = [str(i) for i in vals]
    print('Data spread:',Counter(str_vals))
    
    df.fillna(0, inplace=True)
    
    
    df = df.replace([np.inf, -np.inf], np.nan)
    df.dropna(inplace=True)
    df_vals = df[[ticker for ticker in tickers]]
    print('Data types: ', Counter(df_vals.dtypes))
    #for y in df.columns:
    #    if df[y].dtype == "object" and y != 'Date':
    #        print(y)

    df_vals = df_vals.pct_change()
    df_vals = df_vals.replace([np.inf, -np.inf], 0)
    df_vals.fillna(0, inplace=True)
    #Feature (daily price change), labels
    X, y = df_vals.values, df['{}_target'.format(ticker)].values

    return X, y, df
    
X, y , df = extract_featuresets('XOM')
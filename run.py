#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Apr  1 09:46:23 2018

@author: whitestallion
"""
import os, sys
import bs4 as bs
import pickle
import requests
import datetime as dt
import pandas as pd
import pandas_datareader.data as web
import webbrowser
import time


#build dico index ticker value: name, industry, edgar link 
#serialize locally
def build_sp500_constituents_wikipedia():
    response = requests.get('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
    soup = bs.BeautifulSoup(response.text, 'lxml')
    table = soup.find('table', {'class': 'wikitable sortable'})
    sp500_members = {}
    
    for row in table.findAll('tr')[1:]:
        #get all col for ever row
        td = row.findAll('td')
        ticker = td[0].text
        name = td[1].text
        edgar = td[2].find('a').get('href')
        industry = td[4].text
        sp500_members.update({ticker: name+","+industry+","+edgar})
    
    with open('/Users/whitestallion/Desktop/sp500/data.pickle', 'wb') as f:
        pickle.dump(sp500_members, f)
    
    return sp500_members
    
def get_data_yahoo(reloadConstituents = False):
    if reloadConstituents:
        build_sp500_constituents_wikipedia()
    stocks = pickle.load(open("/Users/whitestallion/Desktop/sp500/data.pickle", "rb" ))
    
    if not os.path.exists("/Users/whitestallion/Desktop/sp500/yahoo_prices"):
        os.makedirs("/Users/whitestallion/Desktop/sp500/yahoo_prices")

    start = dt.datetime(2000,1,1)
    end = dt.datetime(2018,4,1)
    startUnix = int(start.timestamp())
    endUnix = int(end.timestamp())
    print (str(startUnix) + ' , ' + str(endUnix))
    
    os.chdir("/Users/whitestallion/Desktop/sp500/")
    for ticker in stocks.keys():
        print('looking at: ' + ticker)
        if not os.path.exists("/Users/whitestallion/Desktop/sp500/yahoo_prices/{}.csv".format(ticker)):
            if "." in ticker:
                ticker = ticker.replace(".","-")
            webbrowser.open('https://query1.finance.yahoo.com/v7/finance/download/' + ticker + '?period1=' + str(startUnix) + '&period2=' + str(endUnix) + '&interval=1d&events=history&crumb=wBwwzj3M11v')
            time.sleep(1.5)
            #handle referentials between wikipedia and yahoo, since constituents pickle will be based on wikepedia it should conform for now
            if "-" in ticker:
                ticker2 = ticker.replace("-",".")
                os.rename("/Users/whitestallion/Downloads/" + ticker + '.csv', "/Users/whitestallion/Desktop/sp500/yahoo_prices/" + ticker2 + '.csv')
            else:
                os.rename("/Users/whitestallion/Downloads/" + ticker + '.csv', "/Users/whitestallion/Desktop/sp500/yahoo_prices/" + ticker + '.csv')
        else:
            print('Already have {}'.format(ticker))

get_data_yahoo()
            
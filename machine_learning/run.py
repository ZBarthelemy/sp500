import datetime as dt
import os
import pickle
import time
import webbrowser
import bs4 as bs
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import requests
from matplotlib import style

style.use('ggplot')


def build_sp500_constituents_wikipedia():
    response = requests.get('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
    soup = bs.BeautifulSoup(response.text, 'lxml')
    table = soup.find('table', {'class': 'wikitable sortable'})
    sp500_members = {}

    for row in table.findAll('tr')[1:]:
        # get all col for ever row
        td = row.findAll('td')
        ticker = td[0].text
        name = td[1].text
        edgar = td[2].find('a').get('href')
        industry = td[4].text
        sp500_members.update({ticker: name + "," + industry + "," + edgar})

    with open('/Users/whitestallion/Desktop/sp500/data.pickle', 'wb') as f:
        pickle.dump(sp500_members, f)

    return sp500_members


def get_data_yahoo(reloadConstituents=False, synchronizeUpToDate=False):
    if reloadConstituents:
        build_sp500_constituents_wikipedia()
    stocks = pickle.load(open("/Users/whitestallion/Desktop/sp500/data.pickle", "rb"))

    if not os.path.exists("/Users/whitestallion/Desktop/sp500/yahoo_prices"):
        os.makedirs("/Users/whitestallion/Desktop/sp500/yahoo_prices")

    start = dt.datetime(2000, 1, 1)
    end = dt.datetime(2018, 4, 1)
    start_unix = int(start.timestamp())
    end_unix = int(end.timestamp())
    print(str(start_unix) + ' , ' + str(end_unix))

    os.chdir("/Users/whitestallion/Desktop/sp500/")
    for ticker in stocks.keys():
        print('looking at: ' + ticker)
        if not os.path.exists("/Users/whitestallion/Desktop/sp500/yahoo_prices/{}.csv".format(ticker)):
            if "." in ticker:
                ticker = ticker.replace(".", "-")
            webbrowser.open('https://query1.finance.yahoo.com/v7/finance/download/' + ticker + '?period1=' + str(
                start_unix) + '&period2=' + str(end_unix) + '&interval=1d&events=history&crumb=wBwwzj3M11v')
            time.sleep(1.5)
            # handle referentials between wikipedia and yahoo, since constituents pickle will be based on wikepedia it should conform for now
            if "-" in ticker:
                ticker2 = ticker.replace("-", ".")
                os.rename("/Users/whitestallion/Downloads/" + ticker + '.csv',
                          "/Users/whitestallion/Desktop/sp500/yahoo_prices/" + ticker2 + '.csv')
            else:
                os.rename("/Users/whitestallion/Downloads/" + ticker + '.csv',
                          "/Users/whitestallion/Desktop/sp500/yahoo_prices/" + ticker + '.csv')
        else:
            print('Already have {}'.format(ticker))


def compile_data():
    stocks = pickle.load(open("/Users/whitestallion/Desktop/sp500/data.pickle", "rb"))

    df = pd.DataFrame()

    for count, ticker in enumerate(stocks):
        df_i = pd.read_csv("/Users/whitestallion/Desktop/sp500/yahoo_prices/{}.csv".format(ticker))
        df_i.set_index('Date', inplace=True)
        df_i.rename(columns={'Adj Close': ticker}, inplace=True)
        df_i.drop(['Open', 'High', 'Low', 'Close', 'Volume'], 1, inplace=True)

        if df.empty:
            df = df_i
        else:
            df = df.join(df_i, how='outer')
        if count % 25 == 0:
            print(count=', ' + ticker)
    print(df.head())
    df.to_csv('/Users/whitestallion/Desktop/sp500/sp500_joined_closes.csv')


def correlation_table(passDateRange=False, date_from=dt.datetime(2018, 2, 1), date_to=dt.datetime(2018, 3, 31)):
    df = pd.read_csv('/Users/whitestallion/Desktop/sp500/sp500_joined_closes.csv')

    # get last months prices
    if passDateRange:
        df['Date'] = pd.to_datetime(df['Date'])
        df = df[(df['Date'] > date_from) & (df['Date'] < date_to)]

    df_corr = df.corr()
    data = df_corr.values
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)

    heatmap = ax.pcolor(data, cmap=plt.cm.RdYlGn)
    fig.colorbar(heatmap)
    ax.set_xticks(np.arange(data.shape[0]) + 0.5, minor=False)
    ax.set_yticks(np.arange(data.shape[1]) + 0.5, minor=False)
    ax.invert_yaxis()
    ax.xaxis.tick_top()

    column_labels = df_corr.columns
    row_labels = df_corr.index

    ax.set_xticklabels(column_labels)
    ax.set_yticklabels(row_labels)

    plt.xticks(rotation=90)
    heatmap.set_clim(-1, 1)
    plt.tight_layout()
    plt.show()


correlation_table()

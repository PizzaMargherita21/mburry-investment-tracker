import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from pandas_datareader import data as pdr
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import yfinance as yf
yf.pdr_override()
from bs4 import BeautifulSoup
# to collect a sample wep page
import requests
import csv
import time

#Page title 
st.set_page_config(
    page_title="M.Burry Investment Tracker")

st.title("M.Burry Investment Tracker")

#Option single ticker or ticker list loaded via CSV
def getTicker():
    options = ['Single Ticker Check', 'Multi Ticker Check via CSV upload']
    getTickerOptions = st.radio('Select Ticker Check option', options, key="0")
    if getTickerOptions == 'Single Ticker Check':
        tickerList = []
        #Check via single ticker
        x = st.text_input('Enter Ticker')
        if x:
            tickerList.append(x)
        else:
            st.info("Please enter a ticker")

    elif getTickerOptions == 'Multi Ticker Check via CSV upload':
        tickerList = []
        try:
            #read csv
            uploaded_file = st.file_uploader('Choose a file')
            colnames=['Ticker','Name','Asset Class','Weight (%)','Price','Shares','Market Value','Notional Value','Sector','SEDOL','ISIN','Location','Currency','Market Currency','FX Rate'] 
            tickerlist=pd.read_csv(uploaded_file, sep=',',skiprows=10,skipfooter=2, names=colnames, header=None)
            tickerList = tickerlist[['Ticker','Name']]
            tickerList = tickerList['Ticker']

        except:
            st.warning('Please upload a csv file')

    return tickerList

#Menu
st.sidebar.header("Menu")
menu = ["Burry Investments", "Burry Style Analysis","About"]
choice = st.sidebar.selectbox("Select Page",menu)

countryList = ['Japan', 'Korea']
selectCountry = st.sidebar.radio('Select Country', countryList, key="1")

#External links
st.sidebar.header('External Links')
topixETF = '[iShares Core TOPIX ETF](https://www.blackrock.com/jp/individual-en/en/products/279438/ishares-core-topix-etf)'
st.sidebar.write(topixETF)
msciJapanValueETF = '[iShares MSCI Japan Value ETF](https://www.ishares.com/us/products/307263/ishares-msci-japan-value-etf/)'
st.sidebar.write(msciJapanValueETF)


if choice == "Burry Investments":
    
    st.header("Burry Investments :eyes:")
    
    #Get Ticker
    tickerList = getTicker()

    def main(ticker):
        listOwnership = pd.DataFrame(columns=['Company Ticker', 'Link'])
        st.text('\n')
        latest_iteration = st.empty()
        bar = st.progress(0)
        for idx,ticker in enumerate(ticker):
            
            latest_iteration.write('Progress Bar: {} Ticker left from {}'.format((len(tickerList) - (idx+1)), (len(tickerList))))
            bar.progress((100//len(tickerList))*(idx+1))
            time.sleep(1)
            
            try:
                #st.write(idx, ticker)

                # Get url:
                if selectCountry == 'Japan':
                    urlOwnership = 'https://www.wsj.com/market-data/quotes/JP/'+ticker+'/company-people'
                    
                elif selectCountry == 'Korea':
                    urlOwnership = 'https://www.wsj.com/market-data/quotes/KR/XKRX/'+ticker+'/company-people'

                # Get text-based page content of web-files 
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36'} 
                textOwnership  = requests.get(urlOwnership, headers=headers).text

                # Get a parse tree from parsed HTML (makes the web page more readable)
                textSoupOwnership = BeautifulSoup(textOwnership,"lxml") #read in
                containerOwnership = textSoupOwnership.find_all("div", {"class": "mod-column"})[1]
                containerOwnershipList = containerOwnership.find('table', class_ = 'cr_dataTable cr_ownership_mod')
                #st.write(containerOwnershipList.prettify())

                # Loop through Top Institutional Ownership list
                for i in containerOwnershipList.find_all('span', class_ = 'data_label'): 
                    if i.text == 'Scion Asset Management LLC':
                        #name = tickerList['Name'][tickerList['Ticker'] == ticker].values[0]
                        #listOwnership[ticker] = name
                        listOwnership  = listOwnership.append({'Company Ticker': ticker, 'Link': urlOwnership}, ignore_index=True)
                        st.text('\n')
                        st.write('## :fire: It seems that Burry is betting on these stock(s) :fire:')
              

            except:
                pass
        
        st.text('\n')
        st.write('### List of Burry Ownership')
        st.write(listOwnership)

    if len(tickerList)>=1:
        main(tickerList)
        
    
     
    
if choice == "Burry Style Analysis":  
    
    st.header("Burry Style Analysis :mag:")
    
    #Get Ticker
    x = st.text_input('Enter Ticker')
    if x:
        ticker = x
        
        #Select date
        st.subheader("Time Period")

        col1, col2 = st.beta_columns(2) 
        with col1:
            startDate = st.date_input('Start Date', datetime(2019, 1, 1))
        with col2:
            endDate = st.date_input('End Date')

        if selectCountry == 'Japan':
            data = pdr.get_data_yahoo(ticker+'.T', startDate,endDate)['Adj Close']
            currency = 'JPY'
                    
        elif selectCountry == 'Korea':
            data = pdr.get_data_yahoo(ticker+'.KQ', startDate,endDate)['Adj Close']
            currency = 'KRW'
            
        if not data.empty:
            
            priceChart = px.line(data, x=data.index, y='Adj Close')
            priceChart.update_layout(
                title="Daily (Closing) Price Chart",
                yaxis_title= "Price {}".format(currency),
                legend_title="Ticker")

            st.write(priceChart)
            
        else:
            st.write('## No price data available yet!')
    
    else:
        st.info("Please enter a ticker")
    
    st.write("# :bulb: Collecing Ideas, More Soooooon :bulb:")
    
    
elif choice == "About":
    st.info("Built with Streamlit by [Lifelonglearner](https://www.lifelonglearner.de/)")

    
    
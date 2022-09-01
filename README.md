# Crypto Tracker App

## Introduction

**This application was developped for Study exam**

This application permit :
- to save a cryptocurrency wallet for any existing crypto currency
- to get the last value of the wallet at any time
- to get the potential profit of the wallet at any time
- to keep the graph history of these values
- Transactions have to be added one by one and can be removed or updated one by one

All crypto currencies transactions are recorded in euros (this can be changed by updating the "convert_id" of the currency in the functions, in this application the convert id is not a parameter, it could be in a future revision of the app, in this case all the currencies symbol euros have also to be updated in the html files)

This application use a **PostgreSQL** database and the API **https://coinmarketcap.com/api/**

## Environment 

Check files : 
- requirements.txt
- runtime.txt

## Front 

All the html files are in the folder *template*
The html mother file is *base.html*

In the file static are the *javascript.js* and *style.css* and the *pictures* folder

## Back

- *appcrypto.py* is the app start file, the link between all files
- *m_API_cmc_PG.py* contain all the functions linked to the CoinMarketCap API
- *m_db_PG.py* contain all the functions linked to the database

## Test 

*TestFunction.py* contain some functional tests.
The parameters of this test are the following :
lines 9 to 12 (PostgreSQL parameters):
hostname = 'localhost'
user = 'user_test'
password = 'admin'
dbname = 'TestCryptoTracker'
**These parameters have to be updated if necessary to make test on your own machine**
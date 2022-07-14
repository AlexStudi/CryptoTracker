"""Get datas from the data base"""
import psycopg2
from requests import Session
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import json
  

def post_transaction(dbname, user, password, hostname, crypto_id, crypto_qty, crypto_purchase_price):
    """
    Save a transaction in the data base at the UTC datetime
    
    Args:
        - dbname : PG database name
        - user : PG user
        - password : PG password
        - hostname : PG hostname
        - crypto_id (int) : official id of the crypto
        - crypto_qty (float) : 
        - crypto_purchase_price (float) : the purchase price is the total price

    Return : None
    """
    #Save the transaction in the table wallet
    conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=hostname)

    datas = (crypto_id, crypto_qty, crypto_purchase_price) #, crypto_purchase_date)
    with conn:
        with conn.cursor() as curs:
            curs.execute("INSERT INTO wallet (id_crypto, purchase_qty, purchase_price) VALUES(%s,%s,%s)",datas)
            curs.execute("COMMIT;")
    
    datas =  [crypto_id]
    with conn:
        with conn.cursor() as curs:
            curs.execute("INSERT INTO actual_datas (id_crypto) VALUES(%s) ON CONFLICT DO NOTHING;", datas)
            curs.execute("COMMIT;")

    conn.close()

def delete_transaction(dbname, user, password, hostname, id): 
    """
    Delete a transaction from the table wallet

    Args:
        - dbname : PG database name
        - user : PG user
        - password : PG password
        - hostname : PG hostname
        - id : id of the transaction that need to be deleted

    Return : None    
    """
    datas = [id]
    conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=hostname)
    with conn:
        with conn.cursor() as curs:
            curs.execute("DELETE FROM wallet WHERE id_transaction = %s",datas)
            curs.execute("COMMIT;")
    conn.close()
    return id

def update_transaction(dbname, user, password, hostname, id, qte, total_price): 
    """
    Update in the database for a transaction id the crypto quantity and/or the total price
    
    Args:
        - dbname : PG database name
        - user : PG user
        - password : PG password
        - hostname : PG hostname
        - id : id of the transaction that need to be updated
        - qte : new qty of crypto monnaie 
        - total_price : new total price

    Return : None
    """
    datas = [qte, total_price, id]
    conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=hostname)
    with conn:
        with conn.cursor() as curs:
            curs.execute("""
                UPDATE wallet
                SET 
                    purchase_qty = %s,
                    purchase_price = %s 
                WHERE id_transaction = %s;
                """, datas)
            curs.execute("COMMIT;")
    conn.close()
    
def get_datas_delete_transaction(dbname, user, password, hostname, id): # : TODO revoir format purchase_qty
    """
    Return the informations about the transaction that need to be delete in the database

    Args:
        - dbname : PG database name
        - user : PG user
        - password : PG password
        - hostname : PG hostname
        - id : id of the transaction that need to be deleted

    Return dictionary:
        - crypto_logo
        - crypto_transaction_id
        - crypto_transaction_date
        - crypto_qty 
        - crypto_symbol 
        - crypto_name 
        - crypto_purchase_price
        - crypto_plus_value
    """
    
    datas = [id]
    conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=hostname)
    with conn:
        with conn.cursor() as curs:
            curs.execute("""
                SELECT
                    actual_datas.logo,
                    wallet.id_transaction,
                    CAST(wallet.purchase_date AS DATE),
                    wallet.purchase_qty, 
                    actual_datas.symbol,
                    actual_datas.name,
                    wallet.purchase_price, 
                    ROUND(wallet.purchase_qty*(actual_datas.actual_value - wallet.purchase_price)) AS plus_value_euros
                FROM wallet 
                LEFT JOIN actual_datas
                ON wallet.id_crypto = actual_datas.id_crypto
                WHERE wallet.id_transaction = %s;
                """, datas)
            transaction = curs.fetchall()
    conn.close() 
    tuple_title = (
        'crypto_logo',
        'crypto_transaction_id',
        'crypto_transaction_date',
        'crypto_qty', 
        'crypto_symbol', 
        'crypto_name', 
        'crypto_purchase_price',
        'crypto_plus_value'
        )
    transaction_delete = []      
    for i in transaction:
        if len(i) == len(tuple_title): 
            transaction_delete.append(dict(zip(tuple_title,i)))
    
    return transaction_delete
  
def get_crypto_synthesis(dbname, user, password, hostname): 
    """
    This function make 2 actions :
    - Step 1 : Get the last wallet value & profits 
        - Calculation of these values by crypto id
        - The calculation is based on tables wallet and actual_datas
    - Step 2 & 3 : Save these values in the history table
        - Only the latest calculation of the day is kept in the history (one value per day)

    Args:
        - dbname : PG database name
        - user : PG user
        - password : PG password
        - hostname : PG hostname

    Return:
        - crypto_logo
        - crypto_actual_value
        - crypto_qty
        - crypto_symbol
        - crypto_name
        - crypto_total_value
        - crypto_total_profit
        - percent_change_24h
        - percent_change_7d
        - tendancy_24h
        - tendancy_7d
    """
    
    # Step 1 : Value and profit calculation
    conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=hostname)
    with conn:
        with conn.cursor() as curs:
            curs.execute("""
                SELECT
                    actual_datas.id_crypto,
                    actual_datas.logo,
                    actual_datas.actual_value,
                    ROUND(SUM(wallet.purchase_qty),3), 
                    actual_datas.symbol,
                    actual_datas.name,
                    SUM(wallet.purchase_qty)*(actual_datas.actual_value) AS wallet_value,
                    SUM(wallet.purchase_qty)*(actual_datas.actual_value) - SUM(wallet.purchase_price) AS wallet_profit,
                    actual_datas.percent_change_24h,
                    actual_datas.percent_change_7d,
                    actual_datas.tendancy_24h,
                    actual_datas.tendancy_7d
                FROM wallet 
                LEFT JOIN actual_datas
                ON wallet.id_crypto = actual_datas.id_crypto
                GROUP BY actual_datas.id_crypto
                ORDER BY actual_datas.id_crypto;
                """)
            wallet_value = curs.fetchall()
    conn.close()
        
    #with numpy
    wallet = np.array(wallet_value, [
        ("crypto_id","int_"),
        ("crypto_logo","U250"),
        ("crypto_actual_value","float32"),
        ("crypto_qty","float32"),
        ("crypto_symbol","U10"),
        ("crypto_name","U30"),
        ("crypto_total_value","int_"),
        ("crypto_total_profit","int_"),
        ("percent_change_24h","float32"),
        ("percent_change_7d","float32"),
        ("tendancy_24h","U250"),
        ("tendancy_7d","U250")
        ]).view(np.recarray)

    #if the wallet is empty, there is nothing to update in the history
    if len(wallet)==0: 
        wallet = None
        return wallet
    else:   
        #Step 2 : Add the actual date in the history if it doesn't exist
        conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=hostname)
        with conn:
            with conn.cursor() as curs:
                curs.execute("""
                    INSERT INTO history (date) VALUES(current_date) ON CONFLICT DO NOTHING
                    """)
                curs.execute("COMMIT;")
        conn.close()
        #Step 3 : Update the history
        datas = [int(wallet.crypto_total_value.sum()), int(wallet.crypto_total_profit.sum())]#, now]
        conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=hostname)
        with conn:
            with conn.cursor() as curs:
                curs.execute("""
                    UPDATE history
                    SET 
                        wallet_value = %s,
                        profit_loss = %s
                    WHERE date = current_date
                """,datas)
                curs.execute("COMMIT;")
        conn.close()

        return wallet

def history_graph(path, path2, dbname, user, password, hostname): 
    """
    Save 2 graphs : 
        - history of the wallet value 
        - history of the wallet loss and profit

    Args:
        - path : path of the wallet value history
        - path2 : path of the wallet value profits
        - dbname : PG database name
        - user : PG user
        - password : PG password
        - hostname : PG hostname

    Return : None
    """
    # ============================= DATA EXTRACT FROM DB =============================
    conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=hostname)
    with conn:
        with conn.cursor() as curs:
            curs.execute("""
                SELECT * 
                FROM history
                """)
            history = curs.fetchall()
    conn.close()
    history = np.array(history, [
        ("date",'<M8[D]'),
        ("wallet_value","int_"),
        ("profit_loss","int_")
        ]).view(np.recarray)

    # ============================= GRAPH Numpy & matplotlib =============================

    # Graph theme
    plt.style.use('dark_background')

    # Graph setup
    fig, ax = plt.subplots(1, 1, figsize=(5, 3), constrained_layout=True)

    # Calculation of the minimum value in the history (in order to use fill_between)
    min_history = history.wallet_value.min()

    # Curve setup
    ax.fill_between('date', 'wallet_value',min_history, data=history, color='#1fc36c')

    # Major ticks every half year, minor ticks every month,
    ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=(1, 7)))
    ax.xaxis.set_minor_locator(mdates.MonthLocator())
    ax.grid(False)
    # ax.set_ylabel(r'valeur €') #Title y axis
    # format:
    ax.set_title('', loc='left', y=0.85, x=0.02,
                fontsize='medium')
    # x axis format.
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d-%b-%y'))
    # Rotates and right-aligns the x labels so they don't crowd each other.
    for label in ax.get_xticklabels(which='major'):
        label.set(rotation=0, horizontalalignment='center')
    # Path of the history graph
    plt.savefig(path, transparent=True) 

    # Graph 2
    fig, profit = plt.subplots(1, 1, figsize=(5, 3), constrained_layout=True)
    # Calculation of the minimum value in the history (in order to use fill_between)
    if history.profit_loss.min() < 0:
        min_history =0# history.profit_loss.min()
    else:
        min_history = history.profit_loss.min()

    # Curve setup
    profit.fill_between('date', 'profit_loss',min_history, data=history, color='#3498db')

    # Major ticks every half year, minor ticks every month,
    profit.xaxis.set_major_locator(mdates.MonthLocator(bymonth=(1, 7)))
    profit.xaxis.set_minor_locator(mdates.MonthLocator())
    profit.grid(False)
    # ax.set_ylabel(r'valeur €') #Title y axis
    # format:
    profit.set_title('', loc='left', y=0.85, x=0.02,
                fontsize='medium')
    # x axis format.
    profit.xaxis.set_major_formatter(mdates.DateFormatter('%d-%b-%y'))
    # Rotates and right-aligns the x labels so they don't crowd each other.
    for label in profit.get_xticklabels(which='major'):
        label.set(rotation=0, horizontalalignment='center')
    # Path of the history graph
    plt.savefig(path2, transparent=True) 

def get_transactions_list(dbname, user, password, hostname):
    """
    Return all the transactions details saved in the database in the table wallet

    Args:
        - dbname : PG database name
        - user : PG user
        - password : PG password
        - hostname : PG hostname

    Return for each transaction :
        - crypto_logo
        - crypto_transaction_id
        - crypto_transaction_date
        - crypto_qty
        - crypto_symbol
        - crypto_name
        - crypto_purchase_price
        - crypto_plus_value
    """
    conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=hostname)
    with conn:
        with conn.cursor() as curs:
            curs.execute("""
            SELECT
                actual_datas.logo,
                wallet.id_transaction,
                CAST(wallet.purchase_date AS DATE),
                ROUND(wallet.purchase_qty,3), 
                actual_datas.symbol,
                actual_datas.name,
                wallet.purchase_price, 
                ROUND((wallet.purchase_qty*actual_datas.actual_value) - wallet.purchase_price) AS plus_value_euros
            FROM wallet
            LEFT JOIN actual_datas
            ON wallet.id_crypto = actual_datas.id_crypto
            ORDER BY wallet.id_transaction DESC;
            """)
            wallet_value = curs.fetchall()
    conn.close() 
    tuple_title = (
        'crypto_logo',
        'crypto_transaction_id',
        'crypto_transaction_date',
        'crypto_qty', 
        'crypto_symbol', 
        'crypto_name', 
        'crypto_purchase_price',
        'crypto_plus_value'
        )
    wallet = []      
    for i in wallet_value:
        if len(i) == len(tuple_title): 
            wallet.append(dict(zip(tuple_title,i)))
    
    return wallet

"""Get datas from the data base"""
#from requests import Session
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from mysql.connector import errorcode
from datetime import datetime
import datetime as dt

def post_transaction(dbconnect, crypto_id, crypto_qty, crypto_purchase_price):#, crypto_purchase_date=(datetime.now()).strftime("%Y-%m-%d")):
    """Save a transaction in the data base
    
    Args:
        crypto_id (int) : official id of the crypto
        crypto_qty (float) : _
        crypto_purchase_price (float) : the purchase price is the total price
        crypto_purchase_date (date) : (by default) the actual date

    Exemples:
        To post the following transaction : Buy 2 bitcoin(id=1) for 10000€ on the 1st february 2022. Execute the following
        
        post_transaction("1", "2", "10000", "2022-02-01")
    """
    #Save the transaction in the table wallet
    datas = (crypto_id, crypto_qty, crypto_purchase_price) #, crypto_purchase_date)
    cursor = dbconnect.cursor()
    cursor.execute("""INSERT INTO wallet (id_crypto, purchase_qty, purchase_price, purchase_date) VALUES(%s,%s,%s,UTC_TIMESTAMP())""",datas)
    dbconnect.commit()
    cursor.close()
    #Save the id in actual datas if never used
    cursor = dbconnect.cursor()
    datas =  [crypto_id]
    cursor.execute("""INSERT IGNORE INTO actual_datas (id_crypto) VALUES(%s);""", datas) #BUG added here removed from get last cmc
    dbconnect.commit()
    cursor.close()
    
    
def get_transactions_list(dbconnect):
    """Get the détail of the transaction saved in the database
    
    Args:
        dbconnect :paramètres de connexion à la DB :
        dbconnect = mysql.connector.connect(host="",user="######",password="######", database="######")

    Return for each transaction :
                'crypto_logo',
                'crypto_transaction_id',
                'crypto_transaction_date',
                'crypto_qty', 
                'crypto_symbol', 
                'crypto_name', 
                'crypto_purchase_price',
                'crypto_plus_value'

    """
    cursor = dbconnect.cursor()
    cursor.execute("""
        SELECT
            actual_datas.logo,
            wallet.id_transaction,
            CAST(wallet.purchase_date AS DATE) ,
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
    wallet_value = cursor.fetchall()
    cursor.close() #BUG added 22/07/09
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

def update_transaction(dbconnect, id, qte, total_price):
    """Update for a transaction the crypto quantity bought and/or the total price
    
    Args:
        dbconnect : paramètres de connexion à la DB :
            dbconnect = mysql.connector.connect(host="",user="######",password="######", database="######")
        id : id of the transaction that need to be updated
        qte : new qty of crypto monnaie 
        total_price : new total price

    Return for each transaction :
                'crypto_logo',
                'crypto_transaction_id',
                'crypto_transaction_date',
                'crypto_qty', 
                'crypto_symbol', 
                'crypto_name', 
                'crypto_purchase_price',
                'crypto_plus_value'

    """
    datas = [qte, total_price, id]  
    cursor = dbconnect.cursor()
    cursor.execute("""
    UPDATE wallet
    SET 
        purchase_qty = %s,
        purchase_price = %s 
    WHERE id_transaction = %s;
    """, datas)
    dbconnect.commit()
    cursor.close()
    
def get_datas_delete_transaction(dbconnect, id):
    """Get the informations about the transaction that need to be delete
    in order to make a confirmation form.

    Args:
    dbconnect :paramètres de connexion à la DB :
        dbconnect = mysql.connector.connect(host="",user="######",password="######", database="######")
    id : id of the transaction that need to be deleted

    Return a dictionary:
        'crypto_logo',
        'crypto_transaction_id',
        'crypto_transaction_date',
        'crypto_qty', 
        'crypto_symbol', 
        'crypto_name', 
        'crypto_purchase_price',
        'crypto_plus_value'
    """
    cursor = dbconnect.cursor()
    datas = [id]
    cursor.execute("""
    SELECT
        actual_datas.logo,
        wallet.id_transaction,
        CAST(wallet.purchase_date AS DATE),
        FORMAT(wallet.purchase_qty,3), 
        actual_datas.symbol,
        actual_datas.name,
        wallet.purchase_price, 
        ROUND(wallet.purchase_qty*(actual_datas.actual_value - wallet.purchase_price)) AS plus_value_euros
    FROM wallet 
    LEFT JOIN actual_datas
    ON wallet.id_crypto = actual_datas.id_crypto
    WHERE wallet.id_transaction = %s;
    """, datas)
    transaction = cursor.fetchall()
    cursor.close() #BUG added 22/07/09
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

def delete_transaction(dbconnect, id):
    """Delete forever a transaction from the table wallet

    Args:
    dbconnect :paramètres de connexion à la DB :
        dbconnect = mysql.connector.connect(host="",user="######",password="######", database="######")
    id : id of the transaction that need to be deleted

    Return :
        none    
    """
    datas = [id]
    cursor = dbconnect.cursor()
    cursor.execute("""
        DELETE FROM wallet WHERE id_transaction = %s;
    """,datas)
    dbconnect.commit()
    cursor.close()
    return id

def history_graph(path, path2, dbconnect):
   """
   Graph visualisation value history
   
   parameters :
         path : path of the png graph
         cursor : cursor parameters to access to the database"""

   cursor = dbconnect.cursor()
   

   # ============================= DATA EXTRACT FROM DB =============================
   cursor.execute("""
   SELECT * 
   FROM history
   """)
   history = cursor.fetchall()
   cursor.close()
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
   
   
def get_crypto_synthesis(dbconnect):
    """
    Get the last wallet total value & total profits 
    Save these values in the history table

    Step 1 : Calculate value & profits from the database
    If there is datas in the data bases 
    Step 2 : Add the atual date(=key) in the history if doesn't exist
    Step 3 : Update the profit and loss

    Comment : the history table can be be updated many times per day each time there is :
        an additive transaction
        a transaction update
        a transaction delete
        an update of the table actual_datas with new crypto rates

    Parameters :
        dbconnect : database connexion parameters 
    
    Example : 
        dbconnect = mysql.connector.connect(host="",user="######",password="######", database="######")

    Return following arguments :
        ("crypto_logo","U250"),
        ("crypto_actual_value","int_"),
        ("crypto_qty","float32"),
        ("crypto_symbol","U10"),
        ("crypto_name","U30"),
        ("crypto_total_value","int_"),
        ("crypto_total_profit","int_"),
        ("percent_change_24h","float32"),
        ("percent_change_7d","float32"),
        ("tendancy_24h","U250"),
        ("tendancy_7d","U250")
    """
    
    # Step 1 : Value and profit calculation
    #TODO supprimer la source crypto_map car BUG 


    cursor = dbconnect.cursor()
    cursor.execute("""
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
      GROUP BY wallet.id_crypto
      ORDER BY wallet.id_crypto;
      """)
    wallet_value = cursor.fetchall()
    cursor.close()
        
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
        wallet = []
    else:   
        #now = (dt.datetime.now()).strftime("%Y-%m-%d")
        #datas = [now]

        #Step 2 : Add the actual date in the history if it doesn't exist
        cursor = dbconnect.cursor()
        cursor.execute("""
            INSERT IGNORE INTO history (date) VALUES(UTC_DATE())
        """)
        dbconnect.commit()
        cursor.close()
        #cursor.close()#BUG
        

        #Step 3 : Update the history
        
        datas = [int(wallet.crypto_total_value.sum()), int(wallet.crypto_total_profit.sum())]#, now]
        cursor = dbconnect.cursor()#BUG
        cursor.execute("""
            UPDATE history
            SET 
                wallet_value = %s,
                profit_loss = %s
            WHERE date = UTC_DATE()
        """,datas)
        dbconnect.commit()
        cursor.close()
    #BUG remove 2022 07 09
    return wallet

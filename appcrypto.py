from __future__ import print_function
import os
from flask import Flask, redirect, render_template, request
import mysql.connector
from mysql.connector import errorcode
from m_API_cmc import get_last_cmc
from m_API_cmc import get_crypto_list

from m_db import post_transaction
from m_db import get_transactions_list
from m_db import update_transaction
from m_db import get_datas_delete_transaction
from m_db import delete_transaction
from m_db import history_graph
from m_db import get_crypto_synthesis

app = Flask(__name__, template_folder='templates')

def error_message(e):
   loading_error_message = """<img src="../static/pictures/broken.PNG" alt="Broken" height="30"><h1>Something is broken.</h1>"""
   error_text = "<p>The error:<br>" + str(e) + "</p>"
   return loading_error_message + error_text

# ===================================== connexion mysql
host = os.environ.get('DB_HOST')
user = os.environ.get('DB_USER')
password = os.environ.get('DB_PASSWORD')
database = os.environ.get('DATABASE')

#
dbconnect = None
cursor = None
try:
   dbconnect = mysql.connector.connect(
      host=host,
      user=user,
      password=password, 
      database=database
      )
   cursor = dbconnect.cursor()
except Exception as error:
   print(error)
finally:
   if cursor is not None:
      cursor.close()
   if dbconnect is not None:
      dbconnect.close()
#

# ===================================== connexion API cmc

headers = {
    'Accepts': 'application/json',
    'X-CMC_PRO_API_KEY': os.environ.get('API_KEY_TWO'),
    }

# ===================================== Create database

# Tables creation in the database named "DB_NAME"
# Source : https://dev.mysql.com/doc/connector-python/en/connector-python-example-ddl.html 

TABLES = {}

TABLES['wallet'] = (
    "CREATE TABLE `wallet` ("
    "  `id_transaction` INT PRIMARY KEY NOT NULL AUTO_INCREMENT,"
    "  `id_crypto` INT,"
    "  `purchase_qty` DECIMAL(30, 15),"
    "  `purchase_price` DECIMAL(20, 2),"
    "  `purchase_date` DATETIME"
    ") ENGINE=InnoDB")

TABLES['crypto_map'] = (
    "CREATE TABLE `crypto_map` ("
    "   `id_crypto` INT PRIMARY KEY,"
    "   `name` VARCHAR(250),"
    "   `symbol` VARCHAR(50),"
    "   `rank_crypto` INT,"
    "   `last_update` DATETIME"
    ") ENGINE=InnoDB")

TABLES['actual_datas'] = (
    "CREATE TABLE `actual_datas` ("
    "   `id_crypto` INT PRIMARY KEY NOT NULL,"
    "   `actual_value` DECIMAL(20, 2),"
    "   `logo` VARCHAR(250),"
    "   `update_date` DATE,"
    "   `update_date_time` DATETIME,"
    "   `percent_change_24h` DECIMAL(20, 2),"
    "   `percent_change_7d` DECIMAL(20, 2),"
    "   `tendancy_7d` VARCHAR(50),"
    "   `tendancy_24h` VARCHAR(50),"
    "   `symbol` VARCHAR(50),"
    "   `name` VARCHAR(250)"
    ") ENGINE=InnoDB")

TABLES['history'] = (
    "CREATE TABLE `history` ("
    "   `date` DATE PRIMARY KEY,"
    "   `wallet_value` DECIMAL(20, 2),"
    "   `profit_loss` DECIMAL(20, 2)"
    ") ENGINE=InnoDB")

# The preceding code shows how we are storing the CREATE statements in a Python dictionary called TABLES. 
# We also define the database in a global variable called DB_NAME, which enables you to easily use a different schema.
DB_NAME = database
# A single MySQL server can manage multiple databases. Typically, you specify the database to switch to when connecting to the MySQL server. 
# This example does not connect to the database upon connection, so that it can make sure the database exists, and create it if not:

def create_database(cursor):
    try:
        cursor.execute(
            "CREATE DATABASE {} DEFAULT CHARACTER SET 'utf8'".format(DB_NAME))
    except mysql.connector.Error as err:
        print("Failed creating database: {}".format(err))
        exit(1)

cursor = dbconnect.cursor()
try:
    cursor.execute("USE {}".format(DB_NAME))
except mysql.connector.Error as err:
    print("Database {} does not exists.".format(DB_NAME))
    if err.errno == errorcode.ER_BAD_DB_ERROR:
        create_database(cursor)
        print("Database {} created successfully.".format(DB_NAME))
        dbconnect.database = DB_NAME
    else:
        print(err)
        exit(1)
cursor.close()
# After we successfully create or change to the target database, we create the tables by iterating over the items of the TABLES dictionary:
cursor = dbconnect.cursor()
for table_name in TABLES:
    table_description = TABLES[table_name]
    try:
        print("Creating table {}: ".format(table_name), end='')
        cursor.execute(table_description)
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
            print("already exists.")
        else:
            print(err.msg)
    else:
        print("OK")
cursor.close()
# ===================================== Create database == END

# Parameters
refresh_in_minutes = 15 #refresh time for function get_last_cmc()
lengh_crypto_list = 200

# ===================================== crypto_tracker 
@app.route("/")
def cryptotracker():
   try:
      # Get the last update about crypto 
      cursor = dbconnect.cursor()
      cursor.close()
      get_last_cmc(dbconnect,headers,refresh_in_minutes)    #TODO update the time to 15  
      # Get the detail by crypto
      wallet_detailled = get_crypto_synthesis(dbconnect)
      return render_template('crypto_tracker.html',wallet_detailled=wallet_detailled)
   except Exception as e:
      error_message(e)

# ===================================== crypto_add > /cryptoadd
@app.route("/cryptoadd")
def cryptoadd():
   try:
      # get de last list of crypto
      crypto_currency_list = get_crypto_list(headers, lengh_crypto_list) #TODO update quantity if more currency needed
      return render_template('crypto_add.html', crypto_currency = crypto_currency_list)
   except Exception as e:
      error_message(e)

# ===================================== crypto_add - button validate 
@app.route("/cryptoadd", methods=['POST'])
def get_data_new_crypto_entry():
   # Get datas from form
   crypto_id = (request.form['crypto_id'])[1:(request.form['crypto_id'].find(","))]
   crypto_qty = request.form['crypto_qty']
   crypto_purshase_price = request.form['crypto_purshase_price']
   # Save the transaction
   post_transaction(dbconnect, crypto_id, crypto_qty, crypto_purshase_price)
   # Update actual value
   get_last_cmc(dbconnect,headers,refresh_in_minutes) #TODO update the time to 15  
   get_crypto_synthesis(dbconnect)
   #return redirect('/cryptoAdd2')
   return render_template('crypto_add_confirm.html')

# ===================================== crypto_add_confirm 
#@app.route("/cryptoAdd2")
#def crypto_add_new_entry():
#   try:
#      # Message to confirm the transaction is recorded in the database
#      return render_template('crypto_Add_confirm.html')
#   except Exception as e:
#      error_message(e)

# ===================================== crypto_history 
@app.route("/crypto_history")
def crypto_history():
   try:
      values = get_crypto_synthesis(dbconnect)
      history_graph("./static/pictures/History.png","./static/pictures/History2.png",dbconnect)
      return render_template('crypto_history.html', values=values)
   except Exception as e:
      error_message(e)

# ===================================== crypto_edit
@app.route("/wallet_edit")
def wallet_edit():
   try:
      wallet = get_transactions_list(dbconnect)
      return render_template('crypto_edit.html', wallet = wallet)     
   except Exception as e:
      error_message(e)

# ===================================== crypto_edit - button delete
@app.route('/delete_transaction2/<id>', methods=['DELETE', 'GET'])
def wallet_delete_line2(id):
   try:    
      delete_transaction(dbconnect,id)
      return redirect('/wallet_edit', code=302)
   except Exception as e:
      error_message(e)     

# ===================================== crypto_delete_confirmation
@app.route('/delete_transaction/<id>', methods=['POST', 'GET'])
def wallet_delete_line(id):
   try:
      transaction_delete = get_datas_delete_transaction(dbconnect,id)
      return render_template('crypto_delete_confirmation.html', transaction_delete = transaction_delete)       
   except Exception as e:
      error_message(e)

# ===================================== crypto_edit - button update
@app.route("/update_transaction/<id>", methods=['POST'])
def transaction_update(id):
   try:
      qte = request.form['crypto_qty']
      total_price = request.form['crypto_purchase_price']
      update_transaction(dbconnect, id, qte, total_price)
      return redirect('/wallet_edit', code=302)
   except Exception as e:
      error_message(e)

if __name__ == "__main__":
   app.run( debug = True)

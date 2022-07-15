from __future__ import print_function
import os
from flask import Flask, redirect, render_template, request
import psycopg2
from datetime import date

from m_API_cmc_PG import get_last_cmc
from m_API_cmc_PG import get_crypto_list

from m_db_PG import post_transaction
from m_db_PG import get_transactions_list
from m_db_PG import update_transaction
from m_db_PG import get_datas_delete_transaction
from m_db_PG import delete_transaction
from m_db_PG import history_graph
from m_db_PG import get_crypto_synthesis

app = Flask(__name__, template_folder='templates')

def error_message(e):
   loading_error_message = """<img src="../static/pictures/broken.PNG" alt="Broken" height="30"><h1>Something is broken.</h1>"""
   error_text = "<p>The error:<br>" + str(e) + "</p>"
   return loading_error_message + error_text

# ===================================== connexion mysql
hostname = os.environ.get('PG_HOST')
user = os.environ.get('PG_USER')
password = os.environ.get('PG_PASSWORD')
dbname = os.environ.get('PG_DATABASE')

# ===================================== connexion API cmc
headers = {
    'Accepts': 'application/json',
    'X-CMC_PRO_API_KEY': os.environ.get('API_KEY_TWO'),
    }

# ===================================== Create database
conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=hostname)
with conn:
    with conn.cursor() as curs:
        curs.execute("CREATE TABLE IF NOT EXISTS test (id serial PRIMARY KEY, num integer, data varchar);")
with conn:
    with conn.cursor() as curs:
        curs.execute("CREATE TABLE IF NOT EXISTS wallet (id_transaction serial PRIMARY KEY, id_crypto integer, purchase_qty decimal(30,15), purchase_price decimal(20,2), purchase_date timestamp without time zone default (now() at time zone 'utc'));")
with conn:
    with conn.cursor() as curs:
        curs.execute("CREATE TABLE IF NOT EXISTS actual_datas (id_crypto integer PRIMARY KEY, actual_value decimal(20, 2), logo varchar(250), update_date DATE, update_date_time timestamp, percent_change_24h decimal(20, 2), percent_change_7d decimal(20, 2), tendancy_7d varchar(50), tendancy_24h varchar(50), symbol varchar(50), name varchar(250));")
with conn:
    with conn.cursor() as curs:
        curs.execute("CREATE TABLE IF NOT EXISTS history (date date PRIMARY KEY, wallet_value decimal(20,2), profit_loss decimal(20,2));")
conn.close()

# Parameters
refresh_in_minutes = 15 #refresh time for function get_last_cmc()
lengh_crypto_list = 200

# ===================================== crypto_tracker 
@app.route("/", methods=['GET', 'POST'])
def cryptotracker():
   try:
      # Get the last update about crypto 
      get_last_cmc(dbname, user, password, hostname,headers,refresh_in_minutes)     
      # Get the detail by crypto
      wallet_detailled = get_crypto_synthesis(dbname, user, password, hostname)
      return render_template('crypto_tracker.html',wallet_detailled=wallet_detailled)
   except Exception as e:
      error_message(e)

# ===================================== crypto_add > /cryptoadd
@app.route("/cryptoadd")
def cryptoadd():
   try:
      # get de last list of crypto
      crypto_currency_list = get_crypto_list(headers, lengh_crypto_list)
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
   post_transaction(dbname, user, password, hostname, crypto_id, crypto_qty, crypto_purshase_price)
   # Update actual value
   get_last_cmc(dbname, user, password, hostname,headers,refresh_in_minutes)  
   get_crypto_synthesis(dbname, user, password, hostname)
   return render_template('crypto_add_confirm.html')

# ===================================== crypto_history 
@app.route("/crypto_history")
def crypto_history():
   try:
      values = get_crypto_synthesis(dbname, user, password, hostname)
      history_graph("./static/pictures/History.png","./static/pictures/History2.png",dbname, user, password, hostname)
      return render_template('crypto_history.html', values=values, day=date.today())
   except Exception as e:
      error_message(e)

# ===================================== crypto_edit
@app.route("/wallet_edit")
def wallet_edit():
   try:
      wallet = get_transactions_list(dbname, user, password, hostname)
      return render_template('crypto_edit.html', wallet = wallet)     
   except Exception as e:
      error_message(e)

# ===================================== crypto_edit - button delete
@app.route('/delete_transaction2/<id>', methods=['DELETE', 'GET'])
def wallet_delete_line2(id):
   try:    
      delete_transaction(dbname, user, password, hostname,id)
      return redirect('/wallet_edit', code=302)
   except Exception as e:
      error_message(e)     

# ===================================== crypto_delete_confirmation
@app.route('/delete_transaction/<id>', methods=['POST', 'GET'])
def wallet_delete_line(id):
   try:
      transaction_delete = get_datas_delete_transaction(dbname, user, password, hostname,id)
      return render_template('crypto_delete_confirmation.html', transaction_delete = transaction_delete)       
   except Exception as e:
      error_message(e)

# ===================================== crypto_edit - button update
@app.route("/update_transaction/<id>", methods=['POST'])
def transaction_update(id):
   try:
      qte = request.form['crypto_qty']
      total_price = request.form['crypto_purchase_price']
      update_transaction(dbname, user, password, hostname, id, qte, total_price)
      return redirect('/wallet_edit', code=302)
   except Exception as e:
      error_message(e)

if __name__ == "__main__":
   app.run()

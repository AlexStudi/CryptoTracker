from flask import Flask, redirect, render_template, request
from m_API_cmc import *
from m_db import *
from boto.s3.connection import S3Connection
s3 = S3Connection(os.environ['S3_KEY'], os.environ['S3_SECRET'])

crypto_app = Flask(__name__)

def error_message(e):
   loading_error_message = """<img src="../static/pictures/broken.PNG" alt="Broken" height="30"><h1>Something is broken.</h1>"""
   error_text = "<p>The error:<br>" + str(e) + "</p>"
   return loading_error_message + error_text

# ===================================== connexion mysql
host = os.environ.get('DB_host')
user = os.environ.get('DB_user')
password = os.environ.get('DB_password')
database = os.environ.get('DB_database')
dbconnect = mysql.connector.connect(host=host,user=user,password=password, database=database)

cursor = dbconnect.cursor()

# ===================================== connexion API cmc
api_key = os.environ.get('X-CMC_PRO_API_KEY') 
headers = {
    'Accepts': 'application/json',
    'X-CMC_PRO_API_KEY': api_key,
    }

# ===================================== crypto_tracker 
@crypto_app.route("/")
def list_of_crypto():
   try:
      # Get the last update about crypto 
      get_last_cmc(dbconnect,headers,60)      
      # Get the detail by crypto
      wallet_detailled = Get_crypto_synthesis(dbconnect)
      # Get the total wallet value
      return render_template('crypto_tracker.html',wallet_detailled=wallet_detailled)
   except Exception as e:
      error_message(e)

# ===================================== crypto_add > /cryptoadd
# get de last list of crypto
crypto_currency_list = get_crypto_list(headers, dbconnect)

@crypto_app.route("/cryptoadd")
def cryptoadd():
   try:
      return render_template('crypto_add.html', crypto_currency = crypto_currency_list)
   except Exception as e:
      error_message(e)

# ===================================== crypto_add - button validate 
@crypto_app.route("/cryptoadd", methods=['POST'])
def get_data_new_crypto_entry():
   # Get datas from form
   crypto_id = (request.form['crypto_id'])[1:(request.form['crypto_id'].find(","))]
   crypto_qty = request.form['crypto_qty']
   crypto_purshase_price = request.form['crypto_purshase_price']
   # Save the transaction in the table wallet
   post_transaction(dbconnect, crypto_id, crypto_qty, crypto_purshase_price)
   #Update actual value
   get_last_cmc(dbconnect,headers,180)
   # Update actual value and history
   Get_crypto_synthesis(dbconnect)
   return redirect('/cryptoAdd2', code=302)

# ===================================== crypto_add_confirm 
@crypto_app.route("/cryptoAdd2")
def crypto_add_new_entry():
   try:
      return render_template('crypto_Add_confirm.html')
   except Exception as e:
      error_message(e)

# ===================================== crypto_history 
@crypto_app.route("/crypto_history")
def crypto_history():
   try:
      values = Get_crypto_synthesis(dbconnect)
      Get_crypto_synthesis(dbconnect)
      history_graph("./static/pictures/History.png","./static/pictures/History2.png",dbconnect)
      return render_template('crypto_history.html', values=values)
   except Exception as e:
      error_message(e)

# ===================================== crypto_edit
@crypto_app.route("/wallet_edit")
def wallet_edit():
   try:
      wallet = get_transactions_list(dbconnect)
      return render_template('crypto_edit.html', wallet = wallet)     
   except Exception as e:
      error_message(e)

# ===================================== crypto_edit - button delete
@crypto_app.route('/delete_transaction2/<id>', methods=['DELETE', 'GET'])
def wallet_delete_line2(id):
   try:    
      delete_transaction(dbconnect,id)
      return redirect('/wallet_edit', code=302)
   except Exception as e:
      error_message(e)     

# ===================================== crypto_delete_confirmation
@crypto_app.route('/delete_transaction/<id>', methods=['POST', 'GET'])
def wallet_delete_line(id):
   try:
      transaction_delete = get_datas_delete_transaction(dbconnect,id)
      return render_template('crypto_delete_confirmation.html', transaction_delete = transaction_delete)       
   except Exception as e:
      error_message(e)

# ===================================== crypto_edit - button update
@crypto_app.route("/update_transaction/<id>", methods=['POST'])
def transaction_update(id):
   try:
      qte = request.form['crypto_qty']
      total_price = request.form['crypto_purchase_price']
      update_transaction(dbconnect, id, qte, total_price)
      return redirect('/wallet_edit', code=302)
   except Exception as e:
      error_message(e)

if __name__ == "__main__":
   crypto_app.run(debug = True)
from __future__ import print_function

from m_db import *
from m_API_cmc import *
import mysql.connector
from mysql.connector import errorcode
from datetime import date, datetime, timedelta
from pprint import pprint

DB_NAME = 'crypto_test2'

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

cnx = mysql.connector.connect(host="localhost",user="root",password="admin", database=str(DB_NAME))
cursor = cnx.cursor()

print("---- TEST START ----")

# Empty the table wallet in the case this table already exist and have some input inside
cursor.execute("""DROP TABLE IF EXISTS wallet;""")
cursor.execute("""DROP TABLE IF EXISTS actual_datas;""")
cursor.execute("""DROP TABLE IF EXISTS history;""")
cursor.execute("""DROP TABLE IF EXISTS crypto_map;""")
print("Tables wallet, actual_datas, history, crypto_map deleted")

# A single MySQL server can manage multiple databases. Typically, you specify the database to switch to when connecting to the MySQL server. 
# This example does not connect to the database upon connection, so that it can make sure the database exists, and create it if not:

def create_database(cursor):
    try:
        cursor.execute(
            "CREATE DATABASE {} DEFAULT CHARACTER SET 'utf8'".format(DB_NAME))
    except mysql.connector.Error as err:
        print("Failed creating database: {}".format(err))
        exit(1)

try:
    cursor.execute("USE {}".format(DB_NAME))
except mysql.connector.Error as err:
    print("Database {} does not exists.".format(DB_NAME))
    if err.errno == errorcode.ER_BAD_DB_ERROR:
        create_database(cursor)
        print("Database {} created successfully.".format(DB_NAME))
        cnx.database = DB_NAME
    else:
        print(err)
        exit(1)

# We first try to change to a particular database using the database property of the connection object cnx. 
# If there is an error, we examine the error number to check if the database does not exist. If so, we call the create_database function to create it for us.

# On any other error, the application exits and displays the error message.

# After we successfully create or change to the target database, we create the tables by iterating over the items of the TABLES dictionary:

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



#cursor.close()
#cnx.close()
# =================================== END OF DB CREATION ===================================

# Add datas in the data base :
# Source : https://dev.mysql.com/doc/connector-python/en/connector-python-example-cursor-transaction.html




# ==== SETUP DATAS IN wallet TABLE ====
add_crypto = ("INSERT INTO wallet "
               "(id_crypto, purchase_qty, purchase_price, purchase_date) "
               "VALUES (%s, %s, %s, %s)")

data_crypto = (1, 10, 500000, date(2022, 6, 1))
# Insert datas into the table
cursor.execute(add_crypto, data_crypto)
transaction_id = cursor.lastrowid
print("transaction number ",transaction_id," recorded in database : OK")

data_crypto = (1027, 20, 20000, date(2022, 6, 3))
# Insert datas into the table
cursor.execute(add_crypto, data_crypto)
transaction_id = cursor.lastrowid
print("transaction number ",transaction_id," recorded in database : OK")

# Make sure data is committed to the database
cnx.commit()

# ==== SETUP DATAS IN actual_datas TABLE ====
add_actual_datas = ("INSERT INTO actual_datas "
               "(id_crypto, actual_value, logo, update_date, percent_change_24h, percent_change_7d, tendancy_24h, tendancy_7d, symbol, name) "
               "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")

data_actual = (1, 40000, "link logo BTC", datetime.now(), 5, -10, "link logo up", "link logo down", "BTC", "Bitcoin")
# Insert datas into the table
cursor.execute(add_actual_datas, data_actual)
transaction_id = cursor.lastrowid
print("datas for crypto id 1 recorded in database : OK")

data_actual = (1027, 3000, "link logo ETH", datetime.now(), 3, 7, "link logo up", "link logo up", "ETH", "Etherum")
# Insert datas into the table
cursor.execute(add_actual_datas, data_actual)
transaction_id = cursor.lastrowid
print("datas for crypto id 1027 recorded in database : OK")

# Make sure data is committed to the database
cnx.commit()

print("----> END OF DATA BASE SETUP <----")
# =================================== END OF DB FAKE DATAS ===================================

def title_test(function):
    print("============ test fonction : ",function," ============")

def fc_test(test_id, test, test_desc_if_true, test_desc_if_false):
    if test:
        print("> OK < test_id: ",test_id," : ",test_desc_if_true)
    else:
        print("> NOK < test_id: ",test_id," : ",test_desc_if_false)

# Test 1 : 
# In our DB we bought 10BTC for 500000, now a 1BTC = 40000
# It should make 
#   a actual wallet_value = 10x40000 = 400000
#   a actual wallet_profit = 500000 - 10x40000 = 100000




# Check if the function calculate well the total value and the total profit



title_test("Get_crypto_synthesis()")

wallet = Get_crypto_synthesis(cnx)

test_id = 1.1
test = wallet[0][5] == 400000
test_desc_if_true = "In our DB we bought 10BTC for 500000, now a 1BTC = 40000, the actual wallet_value = 10x40000 = 400000 euros"
test_desc_if_false = f"The total wallet value should be 400000, and it is {wallet[0][5]}"
fc_test(test_id, test, test_desc_if_true, test_desc_if_false)

test_id = 1.2
test = wallet[0][6] == -100000
test_desc_if_true = "In our DB we bought 10BTC for 500000, now a 1BTC = 40000, the actual wallet_profit = 10x40000 - 500000 = -100000 euros"
test_desc_if_false = f"The total wallet profit should be -100000, and it  {wallet[0][6]}"
fc_test(test_id, test, test_desc_if_true, test_desc_if_false)

test_id = 1.3
test = wallet[1][5] == 60000
test_desc_if_true = "In our DB we bought 20ETH for 20000, now a 1ETH = 3000, the actual wallet_value = 20x3000 = 60000 euros"
test_desc_if_false = f"The total wallet value should be 60000, and it is  {wallet[1][5]}"
fc_test(test_id, test, test_desc_if_true, test_desc_if_false)

test_id = 1.4
test = wallet[1][6] == 40000
test_desc_if_true = "In our DB we bought 20ETH for 20000, now a 1ETH = 3000, the actual wallet_profit = 20x3000 - 20000 = 40000 euros"
test_desc_if_false = f"The total wallet profit should be 40000, and it is  {wallet[1][6]}"
fc_test(test_id, test, test_desc_if_true, test_desc_if_false)

# Check if the function record well the history in the DB

test_id = 2.1
cursor.execute("""SELECT * FROM history""")
history = cursor.fetchall() 
test = str(history[0][0]) == datetime.now().strftime("%Y-%m-%d")
test_desc_if_true = "history day well saved"
test_desc_if_false = "history day wrong saved"
fc_test(test_id, test, test_desc_if_true, test_desc_if_false)

# actual value = 400000 + 60000 = 460000
test_id = 2.2
test = history[0][1] == 460000
test_desc_if_true = "history total actual value well saved"
test_desc_if_false = "history total actual value not well saved"
fc_test(test_id, test, test_desc_if_true, test_desc_if_false)

# actual profit -100000 + 40000 = -60000
test_id = 2.3
test = history[0][2] == -60000
test_desc_if_true = "history total actual profit well saved"
test_desc_if_false = "history total actual profit not well saved"
fc_test(test_id, test, test_desc_if_true, test_desc_if_false)

title_test("post_transaction()")
# In this test we save a new entry in the DB : 2BTC for 35000€
crypto_id = 1
crypto_qty = 2
crypto_purchase_price = 35000
#crypto_purchase_date = "2022-06-12"
post_transaction(cnx, crypto_id, crypto_qty, crypto_purchase_price)
cursor.execute("""SELECT * FROM wallet WHERE id_transaction = @@identity""")
last_transaction = cursor.fetchall()

test_id = 3.1
test = last_transaction[0][1] == 1 and last_transaction[0][2] == 2 and last_transaction[0][3] == 35000 #TODO tester la date : and str(last_transaction[0][4]) == datetime.now().strftime("%Y-%m-%d")
test_desc_if_true = "last transaction well saved"
test_desc_if_false = "last transaction not well saved"
fc_test(test_id, test, test_desc_if_true, test_desc_if_false)

title_test("update_transaction()")
# In this test we update the last transaction 
# instead of 2BTC at 35000€ we'll set up 3 BTC at 45000€
id_last_transaction = last_transaction[0][0]
update_transaction(cnx, id_last_transaction, "3.5", "45000")
cursor.execute("""SELECT * FROM wallet WHERE id_transaction = @@identity""")
last_transaction = cursor.fetchall()

test_id = 4.1
test = last_transaction[0][1] == 1 and last_transaction[0][2] == 3.5 and last_transaction[0][3] == 45000 #TODO tester la date : and str(last_transaction[0][4]) == datetime.now().strftime("%Y-%m-%d")
test_desc_if_true = "last transaction well updateded"
test_desc_if_false = "last transaction not well updated"
fc_test(test_id, test, test_desc_if_true, test_desc_if_false)

title_test("get_datas_delete_transaction()")
# In this test we check if we get the datas from a transaction we want to delete

test_id = 5.1
test = get_datas_delete_transaction(cnx,"1")[0]['crypto_logo']=='link logo BTC'
test_desc_if_true = "get good data"
test_desc_if_false = "get wrong data"
fc_test(test_id, test, test_desc_if_true, test_desc_if_false)
test_id = 5.2
test = get_datas_delete_transaction(cnx,"1")[0]['crypto_transaction_id']==1
fc_test(test_id, test, test_desc_if_true, test_desc_if_false)
test_id = 5.3
test = get_datas_delete_transaction(cnx,"1")[0]['crypto_transaction_date']=='2022-06-01' #TODO check wrong check data type
fc_test(test_id, test, test_desc_if_true, test_desc_if_false)
test_id = 5.4
test = get_datas_delete_transaction(cnx,"1")[0]['crypto_qty']=='10.000'
fc_test(test_id, test, test_desc_if_true, test_desc_if_false)
test_id = 5.5
test = get_datas_delete_transaction(cnx,"1")[0]['crypto_symbol']==None
fc_test(test_id, test, test_desc_if_true, test_desc_if_false)
test_id = 5.6
test = get_datas_delete_transaction(cnx,"1")[0]['crypto_name']==None
fc_test(test_id, test, test_desc_if_true, test_desc_if_false)
test_id = 5.7
test = get_datas_delete_transaction(cnx,"1")[0]['crypto_purchase_price']==500000.00
fc_test(test_id, test, test_desc_if_true, test_desc_if_false)
test_id = 5.8
test = get_datas_delete_transaction(cnx,"1")[0]['crypto_plus_value']==-4600000
fc_test(test_id, test, test_desc_if_true, test_desc_if_false)

title_test("delete_transaction()")
#In this test we check if we well delete the last transaction of the wallet
cursor.execute("""SELECT * FROM wallet WHERE id_transaction = @@identity""")
last_transaction_id = cursor.fetchall()[0][0]
delete_id = delete_transaction(cnx,last_transaction_id)
test_id = 6.1
test = delete_id == last_transaction_id
test_desc_if_true = "delete id in wallet"
test_desc_if_false = "delete id in wallet"
fc_test(test_id, test, test_desc_if_true, test_desc_if_false)

test_id = 6.2
datas = [delete_id]
cursor.execute("""SELECT * FROM wallet WHERE id_transaction = %s""",datas) #here we request the wallet line which as just been deleted it should return an empty list
result = cursor.fetchall()
test = result == []
test_desc_if_true = f"transaction {delete_id} delete id in wallet"
test_desc_if_false = f"transaction {delete_id} not deleted in the wallet"
fc_test(test_id, test, test_desc_if_true, test_desc_if_false)

print("---- TEST END ----")
cursor.close()
cnx.close()
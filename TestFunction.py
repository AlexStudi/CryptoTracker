import psycopg2
from datetime import date, datetime
from m_db_PG import get_crypto_synthesis
from m_db_PG import post_transaction
from m_db_PG import update_transaction
from m_db_PG import get_datas_delete_transaction
from m_db_PG import delete_transaction

hostname = 'localhost'
user = 'user_test'
password = 'admin'
dbname = 'TestCryptoTracker'

# ===================================== Create tables in the database
conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=hostname)
with conn:
    with conn.cursor() as curs:
        curs.execute("DROP TABLE IF EXISTS wallet;")
with conn:
    with conn.cursor() as curs:
        curs.execute("DROP TABLE IF EXISTS actual_datas;")
with conn:
    with conn.cursor() as curs:
        curs.execute("DROP TABLE IF EXISTS history;")
with conn:
    with conn.cursor() as curs:
        curs.execute("CREATE TABLE IF NOT EXISTS wallet (id_transaction serial PRIMARY KEY, id_crypto integer, purchase_qty decimal(30,15), purchase_price decimal(20,2), purchase_date timestamp without time zone default (now() at time zone 'utc'));")
with conn:
    with conn.cursor() as curs:
        curs.execute("CREATE TABLE IF NOT EXISTS actual_datas (id_crypto integer PRIMARY KEY, actual_value decimal(20, 2), logo varchar(250), update_date DATE, update_date_time timestamp without time zone default (now() at time zone 'utc'), percent_change_24h decimal(20, 2), percent_change_7d decimal(20, 2), tendancy_7d varchar(50), tendancy_24h varchar(50), symbol varchar(50), name varchar(250));")
with conn:
    with conn.cursor() as curs:
        curs.execute("CREATE TABLE IF NOT EXISTS history (date date PRIMARY KEY, wallet_value decimal(20,2), profit_loss decimal(20,2));")
conn.close()

# ===================================== Insert datas in table wallet

add_crypto = ("INSERT INTO wallet (id_crypto, purchase_qty, purchase_price) VALUES (%s, %s, %s);")
data_crypto1 = (1, 10, 500000)
data_crypto2 = (1027, 20, 20000)
data_crypto3 = (1027, 1, 2000)

conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=hostname)
with conn:
    with conn.cursor() as curs:
        curs.execute(add_crypto, data_crypto1)
        curs.execute(add_crypto, data_crypto2)
        curs.execute(add_crypto, data_crypto3)
conn.close()

# ===================================== Insert datas in table actual_datas

add_actual_datas = ("INSERT INTO actual_datas (id_crypto, actual_value, logo, update_date, percent_change_24h, percent_change_7d, tendancy_24h, tendancy_7d, symbol, name) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);")
data_actual1 = (1, 40000, "link logo BTC", datetime.now(), 5, -10, "link logo up", "link logo down", "BTC", "Bitcoin")
data_actual2 = (1027, 3000, "link logo ETH", datetime.now(), 3, 7, "link logo up", "link logo up", "ETH", "Etherum")

conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=hostname)
with conn:
    with conn.cursor() as curs:
        curs.execute(add_actual_datas, data_actual1)
        curs.execute(add_actual_datas, data_actual2)
conn.close()

# ===================================== Functions for tests

def fc_test(test_id, title_test, test, test_desc_if_true, test_desc_if_false):
    print("============ test fonction : ",title_test," ============")
    if test:
        print("> OK < test_id: ",test_id," : ",test_desc_if_true)
    else:
        print("> NOK < test_id: ",test_id," : ",test_desc_if_false)

# ===================================== Tests get_crypto_synthesis()

wallet = get_crypto_synthesis(dbname, user, password, hostname)

fc_test(
    1.1, 
    "get_crypto_synthesis()", 
    wallet[0][6] == 400000, 
    "In our DB we bought 10BTC for 500000, now a 1BTC = 40000, the actual wallet_value = 10x40000 = 400000 euros", 
    f"The total wallet value should be 400000, and it is {wallet[0][6]}")

fc_test(
    1.2, 
    "get_crypto_synthesis()", 
    wallet[1][6] == 63000, 
    "In our DB we bought 21ETH for 22000, now a 1ETH = 3000, the actual wallet_value = 21x3000 = 63000 euros", 
    f"The total wallet value should be 400000, and it is {wallet[1][6]}")

fc_test(
    1.3, 
    "get_crypto_synthesis()", 
    wallet[0][7] == -100000, 
    "In our DB we bought 10BTC for 500000, now a 1BTC = 40000, the actual wallet_profit = 10x40000 - 500000 = -100000 euros", 
    f"The total wallet profit should be -100000, and it  {wallet[0][7]}")

fc_test(
    1.4, 
    "get_crypto_synthesis()", 
    wallet[1][7] == 41000, 
    "In our DB we bought 21BTC for 22000, now a 1ETH = 3000, the actual wallet_profit = 21x3000 - 22000 = 41000 euros", 
    f"The total wallet profit should be 41000, and it  {wallet[1][7]}")

# ===================================== Tests get_crypto_synthesis() : history table

conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=hostname)
with conn:
    with conn.cursor() as curs:
        curs.execute("SELECT * FROM history")
        history = curs.fetchall() 
conn.close()

fc_test(
    2.1,
    "get_crypto_synthesis() history table",
    str(history[0][0]) == datetime.now().strftime("%Y-%m-%d"),
    "history day well saved",
    "history day wrong saved"
)

fc_test(
    2.2,
    "get_crypto_synthesis() history table",
    history[0][1] == 463000,
    "history total actual value well saved",
    "history total actual value not well saved"
)

fc_test(
    2.3,
    "get_crypto_synthesis() history table",
    history[0][2] == -59000,
    "history total actual profit well saved",
    "history total actual profit not well saved"
)

# ===================================== Tests post_transaction()

crypto_id = 1
crypto_qty = 2
crypto_purchase_price = 35000

post_transaction(dbname, user, password, hostname, crypto_id, crypto_qty, crypto_purchase_price)

conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=hostname)
with conn:
    with conn.cursor() as curs:
        curs.execute("SELECT * FROM wallet")
        transactions = curs.fetchall() 
conn.close()

last_transaction = transactions[-1]

fc_test(
    3.1,
    "post_transaction()",
    last_transaction[1] == 1 and last_transaction[2] == 2 and last_transaction[3] == 35000,
    "last transaction well saved",
    "last transaction not well saved"
)

# ===================================== Tests update_transaction()

id = last_transaction[0]
qte = 3.5
total_price = 45000

update_transaction(dbname, user, password, hostname, id, qte, total_price)

conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=hostname)
with conn:
    with conn.cursor() as curs:
        curs.execute("SELECT * FROM wallet")
        transactions = curs.fetchall() 
conn.close()

last_transaction = transactions[-1]

fc_test(
    4.1,
    "post_transaction()",
    last_transaction[1] == 1 and last_transaction[2] == 3.5 and last_transaction[3] == 45000,
    "last transaction well saved",
    "last transaction not well saved"
)

# ===================================== Tests get_datas_delete_transaction()

id = 1

fc_test(
    5.1,
    "get_datas_delete_transaction()",
    get_datas_delete_transaction(dbname, user, password, hostname, id)[0]['crypto_logo']=='link logo BTC',
    "get good data",
    "get wrong data"
)

fc_test(
    5.2,
    "get_datas_delete_transaction()",
    get_datas_delete_transaction(dbname, user, password, hostname, id)[0]['crypto_transaction_id']==1,
    "get good data",
    "get wrong data"
)

fc_test(
    5.3,
    "get_datas_delete_transaction()",
    get_datas_delete_transaction(dbname, user, password, hostname, id)[0]['crypto_qty']==10,
    "get good data",
    "get wrong data"
)

fc_test(
    5.4,
    "get_datas_delete_transaction()",
    get_datas_delete_transaction(dbname, user, password, hostname, id)[0]['crypto_symbol']=='BTC',
    "get good data",
    "get wrong data"
)

fc_test(
    5.5,
    "get_datas_delete_transaction()",
    get_datas_delete_transaction(dbname, user, password, hostname, id)[0]['crypto_name']=='Bitcoin',
    "get good data",
    "get wrong data"
)

fc_test(
    5.6,
    "get_datas_delete_transaction()",
    get_datas_delete_transaction(dbname, user, password, hostname, id)[0]['crypto_purchase_price']==500000.00,
    "get good data",
    "get wrong data"
)

fc_test(
    5.7,
    "get_datas_delete_transaction()",
    get_datas_delete_transaction(dbname, user, password, hostname, id)[0]['crypto_plus_value']==-4600000,
    "get good data",
    "get wrong data"
)

# ===================================== Tests delete_transaction()

id = 1
delete_transaction(dbname, user, password, hostname, id)

conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=hostname)
with conn:
    with conn.cursor() as curs:
        curs.execute("SELECT * FROM wallet WHERE id_transaction='1'")
        transaction = curs.fetchall() 
conn.close()
fc_test(
    6.1,
    "get_datas_delete_transaction()",
    transaction == [],
    "Transaction deleted",
    "Transaction not deleted"
)



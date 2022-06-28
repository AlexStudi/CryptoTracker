"""Get datas from the API Coin Market Cap"""
# Web site : https://coinmarketcap.com/api/

import json
from symtable import Symbol
import mysql.connector
from requests import Session
import json
from datetime import datetime, timedelta
import numpy as np
from zoneinfo import ZoneInfo

def get_crypto_list(headers, dbconnect, limit=100, refresh=180):
    """
    TODO : Terminer la notice de cette fonction : Arg, etc...
    Get list of the crypto from the API CoinMarketCap
    Ce code permet de :
    récupérer la liste des 100 crypto les mieux côtées sur l'API CoinMarket 
    et de les envoyer vers la table crypto_map de la DB crypto
    Paramètres :
    > headers : paramètres de connexion à l'API :
        headers = {
            'Accepts': 'application/json',
            'X-CMC_PRO_API_KEY': 'insert_the_api_key_here',
            }
    > dbconnect : paramètres de connexion à la DB :
        dbconnect = mysql.connector.connect(host="",user="######",password="######", database="######")
    """
    
    #db connexion
    cursor = dbconnect.cursor()
    
    #API parameters
    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/map'
    parameters = {
        'limit':str(limit),
        'aux':"", #when empty remove : "platform,first_historical_data,last_historical_data,is_active" 
        'sort':"cmc_rank" #sort by rank (id by default)
    }
        
    # Check the last update of the table crypto_map in DB
    cursor.execute("""SELECT last_update FROM crypto_map LIMIT 1;""") 
    last_update = cursor.fetchall()

    def minutes_since_last_update(last_update):
        dico={}
        dico["time"] = last_update
        minutes_since_last_update = (datetime.today() - dico["time"]).total_seconds()/60
        return minutes_since_last_update

    # Check if the table crypto_map need to be updated
    if last_update == []:
        update = True
        print("Update of the crypto_map needed") #TODO delete after dev
    elif minutes_since_last_update(last_update[0][0]) < refresh:
        update = False
        print("Update of the crypto_map not needed") #TODO delete after dev
    else:
        update = True
        print("Update of the crypto_map needed") #TODO delete after dev

    if update == True: # if an update is needed, truncate the table crypto_map and save the last list from the API
        session = Session()
        session.headers.update(headers)
        response = session.get(url, params=parameters)
        crypto_list_source = json.loads(response.text)["data"] 
        
        cursor.execute("""
            TRUNCATE TABLE crypto_map
            """)
        dbconnect.commit()

        crypto_list =[]
        for i in range(len(crypto_list_source)):
            # Insert the datas into crypto_map table
            id_crypto = crypto_list_source[i]["id"]
            name = crypto_list_source[i]["name"]
            symbol = crypto_list_source[i]["symbol"]
            rank_crypto = crypto_list_source[i]["rank"]
            datas = (id_crypto,name,symbol,rank_crypto, datetime.now())
            cursor.execute("""
                INSERT INTO crypto_map (id_crypto, name, symbol, rank_crypto, last_update) VALUES(%s,%s,%s,%s,%s)""",datas)
            dbconnect.commit()
            crypto_list.append([id_crypto, symbol, name])
    else: # if an update is not needed, take the list from the database
        cursor.execute("""
            SELECT id_crypto, symbol, name FROM crypto_map ORDER by name""")
        crypto_list = cursor.fetchall()

    return crypto_list

def get_last_cmc(dbconnect, headers, refresh=60):
    """
    Update of the table actual_datas

    Step 1 : get the list of the used crypto id
    Step 2 : empty the table actual_datas
    Step 3 : for each crypto id :   get the value of the crypto through the API cmc (1 jeton / crypto)
                                    save the actual value + date.now in the actual_datas table
    Step 4 : for each crypto id :   get the logo link (1 jeton / crypto)
                                    save the actual value + date.now in the actual datas table
    
    Comment :   this table need to be updated once a day minimum, and each time there is a new crypto id in the wallet table
                Each time this fonction is runing it consume (2 x qty of crypto_id in the table wallet)

    Return : none

    Parameters :
        dbconnect : database connexion parameters 
        headers : API connexion parameters 
    """

    cursor = dbconnect.cursor()

    # Step 1 : List of crypto currency used in the wallet
    cursor.execute("""
        SELECT DISTINCT id_crypto 
        FROM wallet;
    """)
    crypto_purchased = cursor.fetchall()
    crypto_purchased = [i for k in crypto_purchased for i in k] #Convert into list

    # Step 2 : Add crypto id if not exist in the table actual_datas
    for id in crypto_purchased:
        id=[id]
        cursor.execute("""
            INSERT IGNORE INTO actual_datas (id_crypto) VALUES(%s);
            """, id)
        dbconnect.commit()

    # Step 3 : get the last update datetime for each crypto_id in the actual_datas table
    cursor.execute("""
        SELECT 
            id_crypto,
            update_date_time
        FROM actual_datas
    """)
    update_datetime = cursor.fetchall()

    # Dictionnaire : id:dateupdate
    dico={}
    for i in update_datetime:
        A = i[0]
        B = i[1]
        dico[A] = B

    # Update table actual_datas

    for id in crypto_purchased:
        
        if dico[id] is None:
            # if there is no update date, consider the last refresh is older than refresh time (in order to update the datas on the next lines)
            minutes_since_last_update = refresh + 1
        else:
            minutes_since_last_update = (datetime.today() - dico[id]).total_seconds()/60

        if (minutes_since_last_update > refresh) or (dico[id] is None):

            # Step 3 : Get the id_crypto value & save it in the database
            session = Session()
            session.headers.update(headers)
            url = 'https://pro-api.coinmarketcap.com/v2/cryptocurrency/quotes/latest'
            convert_id = '2790' #2790 code pour convertir en euros
            parameters = {
                'id':id,
                'convert_id':convert_id
            }
            response = session.get(url, params=parameters)
            actual_value = (json.loads(response.text)['data'][str(id)]) # get dictionnary for id
            last_updated = actual_value['last_updated'] #TODO Supprimer cette ligne si pas conversion en heure FR 
            percent_change_24h = actual_value['quote'][str(convert_id)]['percent_change_24h']
            percent_change_7d = actual_value['quote'][str(convert_id)]['percent_change_7d']
            price = actual_value['quote'][str(convert_id)]['price']
            symbol = actual_value['symbol']
            name = actual_value['name']
            if percent_change_24h > 0:
                tendancy_24h = "./static/pictures/graph_up.PNG"
            else:
                tendancy_24h = "./static/pictures/graph_down.PNG"
            if percent_change_7d > 0:
                tendancy_7d = "./static/pictures/graph_up.PNG"
            else:
                tendancy_7d = "./static/pictures/graph_down.PNG"
            
            # Save into actual_datas table
            date = datetime.now()
            datas = (price,date,date,percent_change_24h,percent_change_7d,tendancy_24h,tendancy_7d,symbol,name,id) #Try date replaced by last_updated
            cursor.execute("""
                UPDATE actual_datas
                SET 
                    actual_value = %s, 
                    update_date = %s,
                    update_date_time = %s,
                    percent_change_24h = %s,
                    percent_change_7d = %s,
                    tendancy_24h = %s,
                    tendancy_7d = %s,
                    symbol = %s,
                    name = %s
                WHERE id_crypto = %s
                """, datas)
            dbconnect.commit()

            # Step 4 : Get the crypto logo & save it in the database
            url_2 = 'https://pro-api.coinmarketcap.com/v2/cryptocurrency/info'
            parameters_2 = {
                'id':id
            }
            session_2 = Session()
            session_2.headers.update(headers)
            response_2 = session.get(url_2, params=parameters_2)
            logo_link = json.loads(response_2.text)['data'][str(id)]['logo'] #recupération du logo
            datas = (logo_link,id)
            # Save logo into actual_datas table
            cursor.execute("""
                UPDATE actual_datas
                SET logo =  %s
                WHERE id_crypto = %s;
                """,datas)
            dbconnect.commit()
            print("id_",id," updated")
        else:
            print("id_",id," update not needed")

"""Get datas from the API Coin Market Cap"""
# Web site : https://coinmarketcap.com/api/

import json
from requests import Session
import json
from operator import itemgetter


def get_last_cmc(dbconnect, headers, refresh=60):
    refresh = [refresh]
    # The list of crypto 
    cursor = dbconnect.cursor()
    cursor.execute("""
        SELECT DISTINCT
            actual_datas.id_crypto
        FROM actual_datas
        JOIN wallet
        ON wallet.id_crypto = actual_datas.id_crypto
        WHERE TIMESTAMPDIFF(MINUTE, actual_datas.update_date_time, UTC_TIMESTAMP()) > %s OR update_date_time IS NULL
    """, refresh)
    get_update_datetime_by_id = cursor.fetchall()
    #cursor.close()#BUG
    print("test 1 get_last_cmc")#TODO delete
    for i in get_update_datetime_by_id:
        print("test 2 get_last_cmc, update of the id", i)#TODO delete
        session = Session()
        session.headers.update(headers)
        url = 'https://pro-api.coinmarketcap.com/v2/cryptocurrency/quotes/latest'
        convert_id = '2790' #2790 code pour convertir en euros
        parameters = {
            'id':i[0],
            'convert_id':convert_id
        }
        response = session.get(url, params=parameters)
        actual_value = (json.loads(response.text)['data'][str(i[0])]) # get dictionnary for id
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
        #date = datetime.now()
        datas = (price,percent_change_24h,percent_change_7d,tendancy_24h,tendancy_7d,symbol,name,i[0]) #Try date replaced by last_updated
        #cursor = dbconnect.cursor() #BUG
        cursor.execute("""
            UPDATE actual_datas
            SET 
                actual_value = %s, 
                update_date = UTC_DATE(),
                update_date_time = UTC_TIMESTAMP(),
                percent_change_24h = %s,
                percent_change_7d = %s,
                tendancy_24h = %s,
                tendancy_7d = %s,
                symbol = %s,
                name = %s
            WHERE id_crypto = %s
            """, datas)
        dbconnect.commit()
        #cursor.close()#BUG

        # Step 4 : Get the crypto logo & save it in the database
        url_logo = 'https://pro-api.coinmarketcap.com/v2/cryptocurrency/info'
        parameters_logo = {
            'id':i[0]
        }
        response_logo = session.get(url_logo, params=parameters_logo)
        logo_link = json.loads(response_logo.text)['data'][str(i[0])]['logo'] #recupération du logo
        datas = (logo_link,i[0])
        # Save logo into actual_datas table
        #cursor = dbconnect.cursor() #BUG
        cursor.execute("""
            UPDATE actual_datas
            SET logo =  %s
            WHERE id_crypto = %s;
            """,datas)
        dbconnect.commit()
        print("id_",i[0]," updated")
    cursor.close()#BUG

def get_crypto_list(headers, limit=100):
    
    #API parameters
    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/map'
    parameters = {
        
        'aux':"", #when empty remove : "platform,first_historical_data,last_historical_data,is_active" 
        'sort':"cmc_rank", #sort by rank (id by default)
        'limit':str(limit)
    }
    session = Session()
    session.headers.update(headers)
    response = session.get(url, params=parameters)
    crypto_list_source = json.loads(response.text)['data'] 
    crypto_list = []
    for i in range(len(crypto_list_source)):
        id_crypto = crypto_list_source[i]["id"]
        name = crypto_list_source[i]["name"]
        symbol = crypto_list_source[i]["symbol"]
        crypto_list.append([id_crypto, symbol, name])
    crypto_list = sorted(crypto_list, key=itemgetter(2))
    return crypto_list

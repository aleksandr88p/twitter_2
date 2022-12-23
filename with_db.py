import json
from config import *
from mysql.connector import connect
import mysql.connector
import datetime





def make_connection(host, user, password, database, ssl_ca):
    return mysql.connector.connect(host=host, user=user, password=password, database=database, ssl_ca=ssl_ca)


conn = make_connection(host=HOST, user=USER, password=PASSWORD, database=DATABSE, ssl_ca=SSL_CA)
cur = conn.cursor()

"""
+----------------+------+------+-----+---------+----------------+
| Field          | Type | Null | Key | Default | Extra          |
+----------------+------+------+-----+---------+----------------+
| id             | int  | NO   | PRI | NULL    | auto_increment |
| tweeter_handle | text | YES  |     | NULL    |                |
| author_name    | text | YES  |     | NULL    |                |
| replyCount     | text | YES  |     | NULL    |                |
| retweetCount   | text | YES  |     | NULL    |                |
| likeCount      | text | YES  |     | NULL    |                |
| quoteCount     | text | YES  |     | NULL    |                |
| tweet_date     | text | YES  |     | NULL    |                |
| scrape_date    | text | YES  |     | NULL    |                |
| content        | text | YES  |     | NULL    |                |
| image_url      | text | YES  |     | NULL    |                |
| video_url      | text | YES  |     | NULL    |                |
| links          | text | YES  |     | NULL    |                |
| tweet_id       | text | YES  |     | NULL    |                |
| tweet_url      | text | YES  |     | NULL    |                |
| tweet_json     | text | YES  |     | NULL    |                |
+----------------+------+------+-----+---------+----------------+

"""


def create_table():
    try:
        dbs = cur.execute("""CREATE TABLE scraped_twitter 
        (id int not null AUTO_INCREMENT primary key,
        tweeter_handle text, author_name text,
        replyCount text, retweetCount text, likeCount text, quoteCount text,
        tweet_date text, scrape_date text, content text, 
        image_url text, video_url text, links text,
        tweet_id text, tweet_url text, tweet_json text)""")
        print('db ok;')
    except Exception as e:
        print(f'db noP{e}')
        conn.rollback()



def write_from_json_to_db(info_dict):
    date_now = datetime.date.today()
    # print(date_now)
    tweeter_handle = info_dict.get('tweeter_handle', None)
    author_name = info_dict.get('author_name', None)
    replyCount = info_dict.get('replyCount', None)
    retweetCount = info_dict.get('retweetCount', None)
    likeCount = info_dict.get('likeCount', None)
    quoteCount = info_dict.get('quoteCount', None)
    tweet_date = info_dict.get('date', None)
    scrape_date = str(date_now)
    content = info_dict.get('renderedContent', None)
    try:
        images_raw = [i['url'] for i in info_dict['media'] if 'format' in i]
        if images_raw:
            image_url = json.dumps(images_raw)
        else:
            image_url = None
    except Exception as e:
        print(e)
        image_url = None

    try:
        videos_raw = [i['url'] for i in info_dict['media'] if 'content_type' in i]
        if videos_raw:
            video_url = json.dumps(videos_raw)
        else:
            video_url = None
    except Exception as e:
        print(e)
        video_url = None

    try:
        links_raw = info_dict.get('links', None)
        if links_raw:
            links = json.dumps(links_raw)
        else:
            links = None
    except Exception as e:
        print(e)
        links = None
    tweet_id = info_dict.get('id', None)
    tweet_url = info_dict.get('url', None)
    tweet_json = json.dumps(info_dict)
    val = [tweeter_handle, author_name, replyCount, retweetCount, likeCount, quoteCount, tweet_date, scrape_date,
           content, image_url, video_url, links, tweet_id, tweet_url, tweet_json]

    _sql = """INSERT INTO scraped_twitter (
    tweeter_handle,
    author_name,   
    replyCount,    
    retweetCount,  
    likeCount,     
    quoteCount,    
    tweet_date,    
    scrape_date,   
    content,       
    image_url,     
    video_url,     
    links,         
    tweet_id,      
    tweet_url,     
    tweet_json) VALUES
    (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
    conn = make_connection(host=HOST, user=USER, password=PASSWORD, database=DATABSE, ssl_ca=SSL_CA)
    cur = conn.cursor()
    cur.execute(_sql, val)
    conn.commit()



def read_from_db(name):
    '''
    function for looking some tweets with tweeter_handle
    :param name: tweeter_handle
    :return: dict with users tweets
    '''
    conn = make_connection(host=HOST, user=USER, password=PASSWORD, database=DATABSE, ssl_ca=SSL_CA)
    cur = conn.cursor()
    cur.execute(f'SELECT * from scraped_twitter where tweeter_handle="{name}"')
    res = cur.fetchall()
    res_dict = {}
    for i, item in enumerate(res):
        res_dict[i] = {'tweeter_handle': item[1],
                       'author_name': item[2],
                       'replyCount': item[3],
                       'retweetCount': item[4],
                       'likeCount': item[5],
                       'quoteCount': item[6],
                       'tweet_date': item[7],
                       'scrape_date': item[8],
                       'content': item[9],
                       'image_url': item[10],
                       'video_url': item[11],
                       'links': item[12],
                       'tweet_id': item[13],
                       'tweet_url': item[14],
                       'tweet_json': item[15],
                       }
    return res_dict


def find_info_by_handler(tweeter_handle):
    conn = make_connection(host=HOST, user=USER, password=PASSWORD, database=DATABSE, ssl_ca=SSL_CA)
    cur = conn.cursor()
    try:
        sql = f"SELECT * FROM scraped_twitter WHERE tweeter_handle = '{tweeter_handle}'"
        cur.execute(sql)
        res = cur.fetchall()
        res_to_show = []
        res_to_show.append(res[0])
        id_to_show = []
        id_to_show.append(res[0][13])
        for i in res:
            tweet_id = i[13]
            if tweet_id not in id_to_show:
                id_to_show.append(tweet_id)
                res_to_show.append(i)
        return res_to_show
    except:
        return ['no data yet']





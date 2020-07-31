import os
import psycopg2

DATABASE_URL = os.environ['DATABASE_URL']
# conn = psycopg2.connect(DATABASE_URL, sslmode='require')
# cur = conn.cursor()
# cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = \'public\' ORDER BY 1")
# table_name = cur.fetchone()

default_url = "51.178.75.71:40714"

def get(source):
    id = source.from_user.id

    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cur = conn.cursor()
    cur.execute("SELECT url FROM users WHERE user_id = {};".format(id))
    if cur.rowcount == 0:
        return default_url
    else:
        return cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()

def set(source, customUrl: str):
    id = source.from_user.id

    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cur = conn.cursor()
    cur.execute("SELECT url FROM users WHERE user_id = {};".format(id))
    if cur.rowcount == 0:
        cur.execute("INSERT INTO users (user_id, url) VALUES ({}, '{}');".format(id, customUrl))
    else:
        if cur.fetchone() != customUrl:
            cur.execute("UPDATE users SET url = '{}' WHERE user_id = {};".format(customUrl, id))
    conn.commit()
    cur.close()
    conn.close()
from os import getenv
import psycopg2

DATABASE_URL = getenv('DATABASE_URL')

default_url = "51.178.75.71:40714"

def data(user_id, url=None):
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cur = conn.cursor()

    cur.execute("SELECT url FROM users WHERE user_id = {};".format(user_id))

    # set
    if url:
        if cur.rowcount == 0:
            cur.execute("INSERT INTO users (user_id, url) VALUES ({}, '{}');".format(user_id, url))
        else:
            if cur.fetchone() != url:
                cur.execute("UPDATE users SET url = '{}' WHERE user_id = {};".format(url, user_id))
    # get
    else:
        if  cur.rowcount == 0:
            cur.execute("INSERT INTO users (user_id, url) VALUES ({}, '{}');".format(user_id, default_url))
            r = default_url
        else:
            r = cur.fetchone()[0]

    conn.commit()
    cur.close()
    conn.close()

    if not url: return r
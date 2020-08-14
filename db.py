from os import getenv
import psycopg2

DATABASE_URL = getenv('DATABASE_URL')


def data(user_id, url=None):
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cur = conn.cursor()

    cur.execute("SELECT url FROM users WHERE user_id = {};".format(user_id))

    # set
    if url:
        if url == 'default':
            cur.execute("UPDATE users SET url = DEFAULT WHERE user_id = %s;",(user_id,))
        else:
            cur.execute("UPDATE users SET url = %s WHERE user_id = %s;",(url, user_id))
    # get
    else:
        if cur.rowcount == 0:
            cur.execute("INSERT INTO users (user_id) VALUES ({});".format(user_id))
            cur.execute("SELECT url FROM users WHERE user_id = {};".format(user_id))
            r = cur.fetchone()[0]
        else:
            r = cur.fetchone()[0]

    conn.commit()
    cur.close()
    conn.close()

    if not url: return r
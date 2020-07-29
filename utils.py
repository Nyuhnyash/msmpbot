from validators import url
def validUrl(st):
    if url("http://" +st) and (int(len(st)) < 35):
        return True
    else:
        return False

def ending(n):
# Source: https://gist.github.com/CubexX/182bd5918d3455d986b354eadaea02ce
    endings = ['', 'а', 'ов']
    
    if n % 10 == 1 and n % 100 != 11:
        p = 0
    elif 2 <= n % 10 <= 4 and (n % 100 < 10 or n % 100 >= 20):
        p = 1
    else:
        p = 2

    return endings[p]

def name_and_id(source):
    user = source.from_user
    return "{0} ({1})".format(user.username, user.id)

# memcached
import os
import bmemcached
import json
from main import mode

mc = bmemcached.Client(os.environ.get('MEMCACHEDCLOUD_SERVERS').split(','), os.environ.get('MEMCACHEDCLOUD_USERNAME'), os.environ.get('MEMCACHEDCLOUD_PASSWORD'))

def UrlById(source):
    if mode=="prod":
        return mc.get(str(source.from_user.id))
def SetCustomUrl(source,customUrl):
    if mode=="prod":
        mc.set(str(source.from_user.id), customUrl)

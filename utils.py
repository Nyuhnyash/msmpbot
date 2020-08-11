from validators import url
def validUrl(address):
    if url('http://' + address) and (int(len(address)) < 35):
        return True
    else:
        return False


from mcstatus import MinecraftServer as mcS
from requests import get
api = 'https://api.mcsrvstat.us/2/'

class MinecraftServer(mcS):
    def __init__(self, host, port=25565):
        mcS.__init__(self, host, port)
        self._enable_query = None

    @staticmethod
    def lookup(address):
        server = mcS.lookup(address)
        return MinecraftServer(server.host, server.port)
        
    @property
    def enable_query(self):
        if self._enable_query:
            return self._enable_query
        else:
            return get('{}{}:{}'.format(api, self.host, self.port)).json()['debug']['query']


def name_and_id(effective_user):
    return "{0} ({1})".format(effective_user.username, effective_user.id)


update_objects_attrs = { 'inline_query', 'message', 'callback_query'} 

def update_object_type(update):
    for object_attr in update_objects_attrs:
        update_object = update.__dict__.get(object_attr, None)
        if update_object:
            return update_object
            
    raise NotATelegramUpdateInstanseError

class NotATelegramUpdateInstanseError(BaseException): ...


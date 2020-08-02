def validUrl(st):
    from validators import url
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


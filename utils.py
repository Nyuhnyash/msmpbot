def validUrl(st):
    from validators import url
    if url("http://" +st) and (int(len(st)) < 35):
        return True
    else:
        return False

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


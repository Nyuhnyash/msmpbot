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
def by(source):
    user = source.from_user
    return "by {0} ({1})".format(user.username, user.id)

from validators import url

def validUrl(url):
    if url(url) & int(len(url)) > 35:
        return False
    else:
        return True

def plural(n):
# Source: https://gist.github.com/CubexX/182bd5918d3455d986b354eadaea02ce
    endings = ['', 'а', 'ов']
    
    if n % 10 == 1 and n % 100 != 11:
        p = 0
    elif 2 <= n % 10 <= 4 and (n % 100 < 10 or n % 100 >= 20):
        p = 1
    else:
        p = 2

    return str(n) + ' ' + endings[p]
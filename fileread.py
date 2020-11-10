import json


def read(path):
    '''文本中读取字典'''
    file = open(path, "r")
    js = file.read()
    dic = json.loads(js)
    file.close()
    return dic

import json


def write(path, text):
    js = json.dumps(text)
    file = open(path, "w")
    file.write(js)
    file.close()

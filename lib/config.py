import json


def get_data():
    with open("config.json", "rb") as f:
        data = json.load(f)
    return data



def __getattr__(attr):
    if attr.startswith("get_"):
        return (lambda: get_data()[attr.removeprefix("get_")])
    return get_data()[attr]


def __dir__():
    return [i for i in get_data().keys()]

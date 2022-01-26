import os
from tqdm import tqdm
import importlib


loaded_handlers = []

def load_handlers():
    for handler in os.listdir("handlers/"):
        if handler.endswith(".py"):
            handler = handler.removesuffix(".py")
            handle = __import__("handlers."+handler)
            loaded_handlers.append(handle)

def reload_handlers():
    for handle in tqdm(loaded_handlers, desc="Reloading handlers"):
        importlib.reload(handle)

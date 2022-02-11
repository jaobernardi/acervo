import os
import importlib


loaded_handlers = []

def load_handlers():
    for handler in os.listdir("handlers/"):
        if handler.endswith(".py"):
            handler = handler.removesuffix(".py")
            handle = __import__("handlers."+handler)
            loaded_handlers.append(handle)

def reload_handlers():
    for handle in loaded_handlers:
        importlib.reload(handle)

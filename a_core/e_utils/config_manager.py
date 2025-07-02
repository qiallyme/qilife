# utils/config_manager.py
import os
from dotenv import dotenv_values, set_key

ENV_PATH = ".env"

def get_config():
    return dotenv_values(ENV_PATH)

def update_config(key, value):
    set_key(ENV_PATH, key, value)

"""
This file contains helper functions.
"""

import time
import json

def journal (message: str) :
    """
    Journal some information to the log file.
    """
    t = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
    with open ("log.txt", 'a') as f :
        f.write(t + ": " + message + '\n')

def readchecked () -> list :
    """
    Read the list of the checked posts from json file
    """
    with open ("checked.json", 'r') as f :
        return json.load(f)

def writechecked (checked: list) -> None :
    """
    Write the list of the checked posts to json file
    """
    with open ("checked.json", 'w') as f :
        json.dump(checked, f)
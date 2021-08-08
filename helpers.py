"""
This file contains helper functions.
"""

import time

def journal (message: str) :
    """
    Journal some information to the log file.
    """
    t = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
    with open ("log.txt", 'a') as f :
        f.write(t + ": " + message + '\n')
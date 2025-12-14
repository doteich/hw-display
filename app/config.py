import os
import re

def loadConfig():
    data = {
    }


    data["debug"] = bool(os.getenv("debug") or False)
    data["screenRotation"] = int(os.getenv("screenRotation") or 2)

    return data

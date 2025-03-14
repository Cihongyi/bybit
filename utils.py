import math
import hashlib
import time

def floor(x,digit):
    return math.floor(x * 10**digit) / 10.0**digit

def hash_id():
    return hashlib.md5(str(time.time()).encode("utf-8")).hexdigest()


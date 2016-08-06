import time
import configReader
from random import Random

def GetIntMillisecond():
    return int(time.time())

def GetRandomStr(randomlength=configReader.GetSystemConfig().randomPswLen):
    str = ''
    chars = 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789'
    length = len(chars) - 1
    random = Random()
    for i in range(randomlength):
        str += chars[random.randint(0, length)]
    return str

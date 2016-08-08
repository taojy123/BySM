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

def GetNumberFromString(str):
    value = None
    try:
        value = int(str)
    except:
        pass
    return value

def GetIntMillisecondByFormatStr(timeStr):
    timeArray = time.strptime(timeStr, "%Y-%m-%d")
    timeStamp = int(time.mktime(timeArray))
    return timeStamp

def GetFormatStrByIntMillisecond(timeStamp):
    timeArray = time.localtime(timeStamp)
    formatStr = time.strftime("%Y-%m-%d", timeArray)
    # %Y-%m-%d %H:%M:%S
    return formatStr

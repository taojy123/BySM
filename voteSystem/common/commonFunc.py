import time
import configReader
from random import Random
import xlrd
import os

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

def ReadExcel(fileName, removeFile=False):
    dataList = []
    workbook = xlrd.open_workbook(fileName)
    sheet1 = workbook.sheet_by_index(0)
    if sheet1.nrows == 0:
        return dataList

    for i in range(sheet1.nrows):
        row = sheet1.row(i)
        rowData = []
        for j in range(sheet1.ncols):
            rowData.append(row[j].value.encode('utf-8'))
        dataList.append(rowData)

    if os.path.exists(fileName) and removeFile:
        os.remove(fileName)

    return dataList


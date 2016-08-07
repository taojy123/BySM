from pymongo import MongoClient
from common.configReader import GetDBConfig

conn = MongoClient(GetDBConfig().dbPos, GetDBConfig().dbPort)
g_connCache = {}

def GetDataCol(tableName):
    global  g_connCache
    col = g_connCache.get(tableName, None)

    if not col:
        col = conn[GetDBConfig().dbName][tableName]
        g_connCache[tableName] = col

    return col

def SearchData(tableName, condition={}):
    col = GetDataCol(tableName)
    return col.find(condition)
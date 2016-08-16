#!/usr/bin/python
# -*- coding: GBK -*-

class ConfigObj:
    def __init__(self):
        return

def ReadConfig(fileName):
    configFile = open(fileName, 'r')
    obj = ConfigObj()
    for configLine in configFile.readlines():
        configLine = configLine.strip('\n')
        configLine = configLine.strip('\r\n')
        configLine = configLine.strip()
        
        if configLine.startswith('#') or not configLine:
            continue
        
        variable = configLine.split('=')[0].strip()
        value = configLine.split('=')[1].strip()
        try:
            value = eval(value)
        except:
            pass
            
        setattr(obj, variable, value)
        
    return obj

g_config = {}

def GetConfig(fileName):
    global g_config
    if not g_config.has_key(fileName):
        g_config[fileName] = ReadConfig(fileName)
    return g_config[fileName]

def ReLoadConfig(fileName):
    global g_config
    if g_config.has_key(fileName):
        g_config[fileName] = ReadConfig(fileName)
    return

def GetSystemConfig():
    return GetConfig('config/systemConfig.ini')

def GetDBConfig():
    return GetConfig('config/dbConfig.ini')


from daoStruct import DaoStruct
from common.mongoDBCtrl import GetDataCol

class DaoBase():
    def __init__(self, primary, loadData=True):
        self._className = self.__class__.__name__
        self._primay = primary
        self._hasData = None
        self._structDict = None

        self.initDataStruct(loadData)
        return

    def hasData(self):
        return self._hasData

    def initDataStruct(self, loadData):
        self._structDict = DaoStruct.get(self._className, None)

        colData = None
        if loadData:
            colData = self.getDataCol().find_one({'Primary': self._primay})
            if colData:
                self._hasData = True

        for attrName, attrType in self._structDict.iteritems():
            value = None
            if not colData:
                value = self.typeDefaultValue(attrType)
            else:
                value = colData[attrName]

            setattr(self, attrName, value)
        return

    def typeDefaultValue(self, valueType):
        if valueType == int:
            return 0

        elif valueType == str:
            return ''

        elif valueType == dict:
            return {}

        elif valueType == list:
            return []

        return None

    def getDataCol(self):
        return GetDataCol(self._className)

    def loadData(self):
        if self._primay == None:
            return

        colData = self.getDataCol().find_one({'Primary':self._primay})
        if not colData:
            return

        for attrName, attrType in self._structDict.iteritems():
            setattr(self, attrName, attrName)

        self._hasData = True
        return

    def setPrimary(self, primary):
        self._primay = primary
        return

    def getPrimary(self):
        return self._primay

    def saveData(self):
        saveDict = {}
        saveDict['Primary'] = self._primay
        for attrName, attrType in self._structDict.iteritems():
            attrValue = getattr(self, attrName)
            try:
                attrValue = attrType(attrValue)
            except:
                pass
            saveDict[attrName] = attrValue

        col = self.getDataCol()
        colData = col.find_one({'Primary': self._primay})
        if not colData:
            col.insert(saveDict)
        else:
            col.update({'Primary': self._primay}, {'$set': saveDict})

        return

    def removeData(self):
        if not self.hasData():
            return
        col = self.getDataCol()
        col.remove({"Primary":self._primay})
        return
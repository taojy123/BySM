# coding:GBK

from operBase import OperBase
from common.configReader import GetSystemConfig, ReLoadConfig
from bottle import redirect
from dao.userAccDao import UserAccDao
from dao.voteItemDao import VoteItemDao
from common import shareDefine, commonFunc, mongoDBCtrl
import time

def validate_admin_login_decorator(fun):
    def wrapper(self, request, *args, **kwargs):
        if not self.validateAdminLogin(request):
            return self.redirectLogin()
        return fun(self, request, *args, **kwargs)
    return wrapper


class AdminOper(OperBase):
    def __init__(self):
        OperBase.__init__(self)
        return

    def adminLogin(self, request):
        if self.validateAdminLogin(request):
            return self.voterMgr(request, False)

        return self.responseTemplate()

    def adminLoginValidate(self, request):
        userName = request.forms.get('username')
        try:
            userName = int(userName)
        except:
            pass
        password = request.forms.get('password')
        try:
            password = int(password)
        except:
            pass
        loginSuccess = False
        if userName == GetSystemConfig().accountName and password == GetSystemConfig().accountPsw:
            loginSuccess = True
            session = request.environ.get('beaker.session')
            session['adminName'] = userName
            session['adminPsw'] = password
            return self.voterMgr(request, False)

        return self.responseTemplate(tplName='adminLogin', loginSuccess=loginSuccess)

    def validateAdminLogin(self, request):
        session = request.environ.get('beaker.session')
        sessionAdminName = session.get('adminName', None)
        sessionAdminPsw = session.get('adminPsw', None)
        if sessionAdminName and sessionAdminPsw:
            return True

        return False

    @validate_admin_login_decorator
    def adminLoginOut(self, request):
        session = request.environ.get('beaker.session')
        del session['adminName']
        del session['adminPsw']
        return self.redirectLogin()

    def redirectLogin(self):
        return redirect('/admin/adminLogin')

    @validate_admin_login_decorator
    def addVoter(self, request):
        return self.responseTemplate()

    @validate_admin_login_decorator
    def addBeVoter(self, request):
        return self.responseTemplate(tplName='addVoter', userType=shareDefine.UserAccType_BeVoter);

    def addVoterData(self, request):
        userName = request.forms.get('voterName')
        if not userName:
            return self.voterMgr(request)

        userType = self.getIntUserType(request)

        userAccDao = UserAccDao(userName)
        if userAccDao.hasData():
            return self.responseTemplate(tplName='addVoter', userNameExist=True, userType=userType)

        name = request.forms.get('name')
        remark = request.forms.get('remark')
        if len(remark) > 200:
            remark = remark[:200]

        userAccDao.userAcc = userName
        userAccDao.userPsw = commonFunc.GetRandomStr()
        userAccDao.userName = name
        userAccDao.userType = userType
        userAccDao.regTime = commonFunc.GetIntMillisecond()
        userAccDao.remark = remark
        userAccDao.seqKey = self.getNextSeq('UserAccSeq')
        userAccDao.saveData()

        mgr = self.getUserTypeMgr(userType)

        return mgr(request)

    def getUserTypeMgr(self, userType):
        func = None
        if userType == shareDefine.UserAccType_Voter:
            func = self.voterMgr
        else:
            func = self.beVoterMgr
        return func

    @validate_admin_login_decorator
    def editVoter(self, request):
        voterAcc = request.GET.get('editVoter')
        userAccDao = UserAccDao(voterAcc)
        if not userAccDao.hasData():
            return self.voterMgr(request, False)

        return self.responseTemplate(userAccDao=userAccDao, userType=self.getIntUserType(request, False))

    def getIntUserType(self, request, isPost=True):
        if isPost:
            userType = request.forms.get('userType')
        else:
            userType = request.GET.get('userType')

        if userType == None:
            userType = shareDefine.UserAccType_Voter

        userType = int(userType)
        return userType

    @validate_admin_login_decorator
    def editVoterData(self, request):
        userName = request.forms.get('voterName')
        voterPsw = request.forms.get('voterPsw')
        if userName and voterPsw:
            userAccDao = UserAccDao(userName)
            if userAccDao.hasData():
                name = request.forms.get('name')
                remark = request.forms.get('remark')
                if len(remark) > 200:
                    remark = remark[:200]

                userAccDao.userPsw = voterPsw
                userAccDao.userName = name
                userAccDao.remark = remark
                userAccDao.saveData()

        userType = self.getIntUserType(request)
        mgr = self.getUserTypeMgr(userType)

        return mgr(request)

    @validate_admin_login_decorator
    def deleteVoterData(self, request):
        userAcc = request.GET.get('userAcc')
        userAccDao = UserAccDao(userAcc)
        userAccDao.removeData()

        userType = self.getIntUserType(request, False)
        mgr = self.getUserTypeMgr(userType)

        return mgr(request)

    @validate_admin_login_decorator
    def findVoterData(self, request):
        keyword = request.GET.get('keyword')
        if not keyword:
            return self.voterMgr(request)

        userType = self.getIntUserType(request, False)
        col = mongoDBCtrl.GetDataCol('UserAccDao')
        colDataList = col.find({'$or':[{'Primary': {'$regex': keyword}}, {'userName': {'$regex': keyword}}], 'userType':userType})
        if colDataList.count() > 0:
            colDataList.sort("regTime", -1)

        return self.voterMgr(request, False, userType, colDataList, keyword)

    def voterMgr(self, request, validate=True, userType=shareDefine.UserAccType_Voter, colDataList=None, keyword=''):
        if validate and not self.validateAdminLogin(request):
            return self.redirectLogin()

        if not colDataList:
            colDataList = mongoDBCtrl.SearchData('UserAccDao',{'userType':userType})
            if colDataList.count() > 0:
                colDataList.sort("regTime", -1)

        return self.responseTemplate(userType=userType, dataList=list(colDataList), keyword=keyword)

    def beVoterMgr(self, request, validate=True):
        return self.voterMgr(request, validate=validate, userType=shareDefine.UserAccType_BeVoter)

    def voteItemMgr(self, request, validate=True, colDataList=None, keywordYear='', keywordName=''):
        if validate and not self.validateAdminLogin(request):
            return self.redirectLogin()

        if not colDataList:
            colDataList = mongoDBCtrl.SearchData('VoteItemDao')
            if colDataList.count() > 0:
                colDataList.sort("addVoteTime", -1)

        voterNameDict = {}
        beVoterNameDict = {}
        if colDataList.count() > 0:
            voterNameDict, beVoterNameDict = self.getVoteBeVoterNameDict()

        return self.responseTemplate(dataList=list(colDataList), voterNameDict=voterNameDict, beVoterNameDict=beVoterNameDict, keywordYear=keywordYear, keywordName=keywordName)

    def getVoteBeVoterNameDict(self):
        voterNameDict = {}
        beVoterNameDict = {}
        col = mongoDBCtrl.GetDataCol('UserAccDao')
        colDataList = mongoDBCtrl.SearchData('VoteItemDao')
        for colData in colDataList:
            beVoterNameList = []
            for beVoterAcc in colData['beVoterInfoDict'].iterkeys():
                accColData = col.find_one({'userAcc': beVoterAcc})
                if accColData:
                    beVoterNameList.append(accColData['userName'])
            beVoterNameDict[colData['Primary']] = beVoterNameList

            voterNameList = []
            for voterAcc in colData['voterInfoDict'].iterkeys():
                accColData = col.find_one({'userAcc': voterAcc})
                if accColData:
                    voterNameList.append(accColData['userName'])
            voterNameDict[colData['Primary']] = voterNameList
        return voterNameDict, beVoterNameDict

    @validate_admin_login_decorator
    def addVoteItem(self, request):
        return self.responseTemplate()

    @validate_admin_login_decorator
    def findVoterAjax(self, request):
        userType = self.getIntUserType(request, False);
        keyword = request.GET.get('keyword')

        if keyword == None:
            searchDict = {'userType': userType}
        else:
            searchDict = {'$or': [{'Primary': {'$regex': keyword}}, {'userName': {'$regex': keyword}}], 'userType': userType}

        col = mongoDBCtrl.GetDataCol('UserAccDao')
        colDataList = col.find(searchDict)

        if colDataList.count() > 0:
            colDataList.sort("regTime", -1)

        return self.responseTemplate(dataList=list(colDataList), userType=userType)

    @validate_admin_login_decorator
    def addVoteItemData(self, request):
        primary = int(request.POST.get('primary'))
        voteItemData = VoteItemDao(primary)
        voteItemData.year = request.POST.get('year')
        voteItemData.name = request.POST.get('name')
        voteItemData.voterTicketCnt = request.POST.get('voterTicketCnt')
        voteItemData.beVoterPassCnt = request.POST.get('beVoterPassCnt')
        voteItemData.isUnSign = request.POST.get('isUnSign')
        remark = request.POST.get('remark')
        if len(remark) > 200:
            remark = remark[:200]
        voteItemData.remark = remark
        if not voteItemData.hasData():
            voteItemData.addVoteTime = commonFunc.GetIntMillisecond()
            voteItemData.setPrimary(self.getNextSeq('VoteItemSeq'))

        voterInfoDict = {}
        voterListStr = request.POST.get('voterListStr')
        for voterAcc in voterListStr.split('_'):
            voterDetailDict = {'voterLeftTicket':int(request.POST.get('voterTicketCnt')), 'voteRec':{}}
            voterInfoDict[voterAcc] = voterDetailDict

        beVoterInfoDict = {}
        beVoterListStr = request.POST.get('beVoterListStr')
        for beVoterAcc in beVoterListStr.split('_'):
            beVoterInfoDict[beVoterAcc] = 0

        endTime = commonFunc.GetIntMillisecondByFormatStr(request.POST.get('endTime'))

        voteItemData.endTime = endTime
        voteItemData.voterInfoDict = voterInfoDict
        voteItemData.beVoterInfoDict = beVoterInfoDict
        voteItemData.saveData()

        return self.voteItemMgr(request)

    @validate_admin_login_decorator
    def editVoteItem(self, request):
        primary = request.GET.get('primary')
        if primary == None:
            return self.voteItemMgr(request)

        voteItemData = VoteItemDao(int(primary))
        if not voteItemData.hasData():
            return self.voteItemMgr(request)

        voterInfoDict = {}
        for voterAcc in voteItemData.voterInfoDict.iterkeys():
            voterData = UserAccDao(voterAcc)
            voterInfoDict[voterAcc] = voterData.userName

        beVoterInfoDict = {}
        for beVoterAcc in voteItemData.beVoterInfoDict.iterkeys():
            beVoterData = UserAccDao(beVoterAcc)
            beVoterInfoDict[beVoterAcc] = beVoterData.userName

        return self.responseTemplate(tplName='addVoteItem', voteItemData=voteItemData, voterInfoDict=voterInfoDict, beVoterInfoDict=beVoterInfoDict)

    @validate_admin_login_decorator
    def deleteVoteItem(self, request):
        primary = request.GET.get('primary')

        if primary:
            voteItemData = VoteItemDao(int(primary))
            voteItemData.removeData()

        return self.voteItemMgr(request)

    @validate_admin_login_decorator
    def findVoteItem(self, request):
        keywordYear = request.GET.get('keywordYear')
        keywordName = request.GET.get('keywordName')
        isUnsign = request.GET.get('isUnsign')

        searchDict = {}
        if keywordYear:
            searchDict['year'] = int(keywordYear)

        if keywordName:
            searchDict['name'] = {'$regex': keywordName}

        if isUnsign:
            searchDict['isUnSign'] = int(isUnsign)

        col = mongoDBCtrl.GetDataCol('VoteItemDao')
        colDataList = col.find(searchDict)

        if isUnsign:
            return self.backVote(request, colDataList=colDataList, keywordYear=keywordYear, keywordName=keywordName)

        return self.voteItemMgr(request, colDataList=colDataList, keywordYear=keywordYear, keywordName=keywordName)

    @validate_admin_login_decorator
    def backVote(self, request, keywordYear='', keywordName='', colDataList=None):
        if not colDataList:
            colDataList = mongoDBCtrl.SearchData('VoteItemDao', {'isUnSign':0})

        voterNameDict = {}
        beVoterNameDict = {}
        canVoteDict = {}
        if colDataList.count() > 0:
            voterNameDict, beVoterNameDict = self.getVoteBeVoterNameDict()
            colDataList2 = mongoDBCtrl.SearchData('VoteItemDao', {'isUnSign':0})
            curIntTime = int(time.time())
            for colData in colDataList2:
                canVote = True
                if curIntTime >= colData["endTime"]:
                    canVote = False
                canVoteDict[colData['Primary']] = canVote

            colDataList.sort("addVoteTime", -1)

        return self.responseTemplate(dataList=list(colDataList), keywordYear=keywordYear, keywordName=keywordName, voterNameDict=voterNameDict, beVoterNameDict=beVoterNameDict, canVoteDict=canVoteDict)

    @validate_admin_login_decorator
    def selectBackVote(self, request, voteItem=None):
        if voteItem == None:
            voteItem = int(request.GET.get('selectBackVote'))
        voteItemData = VoteItemDao(voteItem)
        hasData = False
        voterRecInfoDict = {}
        for voterAcc, voteInfo in voteItemData.voterInfoDict.iteritems():
            voteRecList =[]
            for beVoteAcc, beVoteItmeList in voteInfo['voteRec'].iteritems():
                for beVoteTime in beVoteItmeList:
                    voteDetailObj = {
                        'time':beVoteTime,
                        'beVoteAcc':beVoteAcc,
                        'beVoteName':UserAccDao(beVoteAcc).userName
                    }
                    voteRecList.append(voteDetailObj)
                    hasData = True
            if len(voteRecList) == 0:
                continue

            voterRecInfoDict[voterAcc] = [UserAccDao(voterAcc).userName, voteRecList]

        return self.responseTemplate(voterRecInfoDict=voterRecInfoDict, hasData=hasData, voteItem=voteItem)

    @validate_admin_login_decorator
    def doBackVote(self, request):
        voteItem = int(request.POST.get('voteItem'))
        voterAcc = request.POST.get('voterAcc')

        voteItemData = VoteItemDao(voteItem)
        voteRecDict = voteItemData.voterInfoDict[voterAcc]['voteRec']
        voteDict = {}
        for beVoteAcc, voteRecList in voteRecDict.iteritems():
            recTicNum = len(voteRecList)
            voteItemData.voterInfoDict[voterAcc]['voterLeftTicket'] += recTicNum
            voteItemData.beVoterInfoDict[beVoteAcc] -= recTicNum

        voteItemData.voterInfoDict[voterAcc]['voteRec'] = {}
        voteItemData.saveData()

        return self.selectBackVote(request, voteItem=voteItem)

    @validate_admin_login_decorator
    def voterTable(self, request, keyword=''):
        infoList = []
        searchDict = {}
        if keyword:
            searchDict = {'$or': [{'Primary': keyword}, {'userName': keyword}]}

        searchDict['userType'] = shareDefine.UserAccType_Voter

        col = mongoDBCtrl.GetDataCol('UserAccDao')
        userColDataList = col.find(searchDict)
        for userColData in userColDataList:
            colDataList = mongoDBCtrl.SearchData('VoteItemDao')
            if colDataList.count() > 0:
                colDataList.sort("addVoteTime", -1)
            for colDataItem in colDataList:
                if colDataItem['voterInfoDict'].has_key(userColData['userAcc']):
                    curIntTime = int(time.time())
                    isEnd = 0
                    if curIntTime >= colDataItem["endTime"]:
                        isEnd = 1

                    dataObj = {
                        'year':colDataItem['year'],
                        'name':colDataItem['name'],
                        'voterTicketCnt':colDataItem['voterTicketCnt'],
                        'voterLeftTicket':colDataItem['voterInfoDict'][userColData['userAcc']]['voterLeftTicket'],
                        'isEnd':isEnd,
                        'userAcc':userColData['userAcc'],
                        'userName':userColData['userName']
                    }
                    infoList.append(dataObj)

        return self.responseTemplate(infoList=infoList, keyword=keyword)

    @validate_admin_login_decorator
    def findVoterVoteData(self, request):
        return self.voterTable(request, request.GET.get('keyword'))

    @validate_admin_login_decorator
    def beVoterTable(self, request, keyword=''):
        infoList = []
        searchDict = {}
        if keyword:
            searchDict = {'$or': [{'Primary': keyword}, {'userName': keyword}]}

        searchDict['userType'] = shareDefine.UserAccType_BeVoter

        col = mongoDBCtrl.GetDataCol('UserAccDao')
        userColDataList = col.find(searchDict)
        for userColData in userColDataList:
            colDataList = mongoDBCtrl.SearchData('VoteItemDao')
            if colDataList.count() > 0:
                colDataList.sort("addVoteTime", -1)
            for colDataItem in colDataList:
                if colDataItem['beVoterInfoDict'].has_key(userColData['userAcc']):
                    curIntTime = int(time.time())
                    isEnd = 0
                    if curIntTime >= colDataItem["endTime"]:
                        isEnd = 1

                    dataObj = {
                        'year': colDataItem['year'],
                        'name': colDataItem['name'],
                        'beVoterPassCnt': colDataItem['beVoterPassCnt'],
                        'beVotetCnt': colDataItem['beVoterInfoDict'][userColData['userAcc']],
                        'isEnd': isEnd,
                        'userAcc': userColData['userAcc'],
                        'userName': userColData['userName']
                    }
                    infoList.append(dataObj)
        return self.responseTemplate(infoList=infoList, keyword=keyword)

    @validate_admin_login_decorator
    def findBeVoterVoteData(self, request):
        return self.beVoterTable(request, request.GET.get('keyword'))

    @validate_admin_login_decorator
    def changeAdminPsw(self, request):
        return self.responseTemplate()

    @validate_admin_login_decorator
    def doChangeAdminPsw(self, request):
        oldPsw = request.POST.get('passwordOld')
        try:
            oldPsw = int(oldPsw)
        except:
            pass

        newPsw = request.POST.get('passwordNew')

        oldPswErr = False
        changeSuccess = False
        if oldPsw != GetSystemConfig().accountPsw:
            oldPswErr = True
        else:
            configFileR = open('config/systemConfig.ini', 'r')
            content = configFileR.read()
            configFileR.close()
            content = content.replace('accountPsw = %s'%oldPsw, 'accountPsw = %s'%newPsw)
            configFile = open('config/systemConfig.ini', 'w')
            configFile.write(content)
            configFile.close()
            changeSuccess = True
            ReLoadConfig('config/systemConfig.ini')

        return self.responseTemplate(tplName='changeAdminPsw', oldPswErr=oldPswErr, changeSuccess=changeSuccess)

    @validate_admin_login_decorator
    def findVoteItemTable(self, request):
        keywordYear = request.GET.get('keywordYear')
        keywordName = request.GET.get('keywordName')
        return self.voteRecTable(request, keywordYear, keywordName)

    @validate_admin_login_decorator
    def voteRecTable(self, request, keywordYear='', keywordName=''):
        infoList = []
        searchDict = {}
        if keywordYear:
            searchDict['year'] = int(keywordYear)

        if keywordName:
            searchDict['name'] = {'$regex': keywordName}

        col = mongoDBCtrl.GetDataCol('VoteItemDao')
        colDataList = col.find(searchDict)
        if colDataList.count() > 0:
            colDataList.sort("addVoteTime", -1)

        for colData in colDataList:
            voterList = []
            hasTicketVoterList = []
            for voterAcc, voterInfo in colData['voterInfoDict'].iteritems():
                voterName = UserAccDao(voterAcc).userName
                voterList.append(voterName)
                if voterInfo['voterLeftTicket'] > 0:
                    hasTicketVoterList.append(voterName)

            beVoterList = []
            passBeVoterList = []
            for beVoterAcc, beVoterTicket in colData['beVoterInfoDict'].iteritems():
                beVoterName = UserAccDao(beVoterAcc).userName
                beVoterList.append(beVoterName)
                if beVoterTicket >= colData['beVoterPassCnt']:
                    passBeVoterList.append(beVoterName)

            dataObj = {
                'addVoteTime':colData['addVoteTime'],
                'year':colData['year'],
                'name':colData['name'],
                'voterList': voterList,
                'beVoterList':beVoterList,
                'beVoterPassCnt':colData['beVoterPassCnt'],
                'hasTicketVoterList':hasTicketVoterList,
                'passBeVoterList':passBeVoterList,
                'endTime':colData['endTime']
            }
            infoList.append(dataObj)

        return self.responseTemplate(infoList=infoList, keywordYear=keywordYear, keywordName=keywordName)
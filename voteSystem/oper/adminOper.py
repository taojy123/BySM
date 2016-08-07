# coding:GBK

from operBase import OperBase
from common.configReader import GetSystemConfig
from bottle import redirect
from dao.userAccDao import UserAccDao
from dao.voteItemDao import VoteItemDao
from common import shareDefine, commonFunc, mongoDBCtrl

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
        password = request.forms.get('password')
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
        if userAccDao.hasData():
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

    def voteItemMgr(self, request, validate=True, colDataList=None):
        if validate and not self.validateAdminLogin(request):
            return self.redirectLogin()

        if not colDataList:
            colDataList = mongoDBCtrl.SearchData('VoteItemDao')
            if colDataList.count() > 0:
                colDataList.sort("addVoteTime", -1)

        voterNameDict = {}
        beVoterNameDict = {}
        if colDataList.count() > 0:
            col = mongoDBCtrl.GetDataCol('UserAccDao')
            colDataList2 = mongoDBCtrl.SearchData('VoteItemDao')
            for colData in colDataList2:
                beVoterNameList = []
                for beVoterAcc in colData['beVoterInfoDict'].iterkeys():
                    accColData = col.find_one({'userAcc':beVoterAcc})
                    if accColData:
                        beVoterNameList.append(accColData['userName'])
                beVoterNameDict[colData['Primary']] = beVoterNameList

                voterNameList = []
                for voterAcc in colData['voterInfoDict'].iterkeys():
                    accColData = col.find_one({'userAcc':voterAcc})
                    if accColData:
                        voterNameList.append(accColData['userName'])
                voterNameDict[colData['Primary']] = voterNameList

        return self.responseTemplate(dataList=list(colDataList), voterNameDict=voterNameDict, beVoterNameDict=beVoterNameDict)

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
        voteItemData = VoteItemDao(0)
        voteItemData.year = request.POST.get('year')
        voteItemData.name = request.POST.get('name')
        voteItemData.voterTicketCnt = request.POST.get('voterTicketCnt')
        voteItemData.beVoterPassCnt = request.POST.get('beVoterPassCnt')
        voteItemData.isUnSign = request.POST.get('isUnSign')
        remark = request.POST.get('remark')
        if len(remark) > 200:
            remark = remark[:200]
        voteItemData.remark = remark
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

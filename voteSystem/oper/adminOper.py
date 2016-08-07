from operBase import OperBase
from common.configReader import GetSystemConfig
from bottle import redirect
from dao.userAccDao import UserAccDao
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

        return self.voterMgr(request, False, userType, colDataList)

    def voterMgr(self, request, validate=True, userType=shareDefine.UserAccType_Voter, colDataList=None):
        if validate and not self.validateAdminLogin(request):
            return self.redirectLogin()

        if not colDataList:
            colDataList = mongoDBCtrl.SearchData('UserAccDao',{'userType':userType})
            if colDataList.count() > 0:
                colDataList.sort("regTime", -1)

        return self.responseTemplate(userType=userType, dataList=list(colDataList))

    def beVoterMgr(self, request, validate=True):
        return self.voterMgr(request, validate=validate, userType=shareDefine.UserAccType_BeVoter)
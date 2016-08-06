from operBase import OperBase
from common.configReader import GetSystemConfig
from bottle import redirect
from dao.userAccDao import UserAccDao
from common import shareDefine, commonFunc, mongoDBCtrl

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

    def voterMgr(self, request, validate=True):
        if validate and not self.validateAdminLogin(request):
            return self.redirectLogin()

        colDataList = mongoDBCtrl.SearchData('UserAccDao')

        return self.responseTemplate(dataList=list(colDataList))

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

    def addVoter(self, request):
        if not self.validateAdminLogin(request):
            return self.redirectLogin()

        return self.responseTemplate()

    def addVoterData(self, request):
        userName = request.forms.get('voterName')
        if not userName:
            return self.voterMgr(request)

        userAccDao = UserAccDao(userName)
        if userAccDao.hasData():
            return self.responseTemplate(tplName='addVoter', userNameExist=True)

        name = request.forms.get('name')
        remark = request.forms.get('remark')
        if len(remark) > 200:
            remark = remark[:200]

        userAccDao.userAcc = userName
        userAccDao.userPsw = commonFunc.GetRandomStr()
        userAccDao.userName = name
        userAccDao.userType = shareDefine.UserAccType_Voter
        userAccDao.regTime = commonFunc.GetIntMillisecond()
        userAccDao.remark = remark
        userAccDao.saveData()

        return self.voterMgr(request)

    def editVoter(self, request):
        if not self.validateAdminLogin(request):
            return self.redirectLogin()

        voterAcc = request.GET.get('editVoter')
        userAccDao = UserAccDao(voterAcc)
        if not userAccDao.hasData():
            return self.voterMgr(request, False);

        return self.responseTemplate(userAccDao=userAccDao)

    def editVoterData(self, request):
        if not self.validateAdminLogin(request):
            return self.redirectLogin()

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

        return self.voterMgr(request)

    def deleteVoterData(self, request):
        if not self.validateAdminLogin(request):
            return self.redirectLogin()

        userAcc = request.GET.get('userAcc')
        userAccDao = UserAccDao(userAcc)
        if userAccDao.hasData():
            userAccDao.removeData()

        return self.voterMgr(request)

    def findVoterData(self, request):
        if not self.validateAdminLogin(request):
            return self.redirectLogin()

        keyword = request.GET.get('keyword')
        if not keyword:
            return self.voterMgr(request)

        col = mongoDBCtrl.GetDataCol('UserAccDao')
        colDataList = col.find({'$or':[{'Primary': {'$regex': keyword}}, {'userName': {'$regex': keyword}}]})
        if colDataList.count() > 0:
            colDataList.sort("regTime", -1)

        return self.responseTemplate(tplName='voterMgr',dataList=list(colDataList))
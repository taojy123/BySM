# coding:GBK

from operBase import OperBase
from common.configReader import GetSystemConfig
from bottle import redirect
from dao.userAccDao import UserAccDao
from dao.voteItemDao import VoteItemDao
from common import shareDefine, commonFunc, mongoDBCtrl
import time

def validate_admin_login_decorator(fun):
    def wrapper(self, request, *args, **kwargs):
        if not self.validateVoterLogin(request):
            return self.redirectLogin()
        return fun(self, request, *args, **kwargs)
    return wrapper


class VoterOper(OperBase):
    def __init__(self):
        OperBase.__init__(self)
        return

    def voterLogin(self, request):
        if self.validateVoterLogin(request):
            return self.voteItems(request, False)

        return self.responseTemplate()

    def validateVoterLogin(self, request):
        session = request.environ.get('beaker.session')
        sessionVoterName = session.get('voterName', None)
        sessionVoterPsw = session.get('voterPsw', None)
        if sessionVoterName and sessionVoterPsw:
            return True

        return False

    def voteItems(self, request, isValidateLogin=True, colDataList=None):
        if isValidateLogin and not self.validateVoterLogin(request):
            return self.redirectLogin()

        session = request.environ.get('beaker.session')
        userAcc = session['voterName']
        if not colDataList:

            voterAcc = 'voterInfoDict.{username}'.format(username=userAcc)
            col = mongoDBCtrl.GetDataCol('VoteItemDao')
            colDataList = col.find({voterAcc: {'$exists': True}})

        beVoterNameDict = {}
        canVoteDict = {}
        if colDataList.count() > 0:
            col = mongoDBCtrl.GetDataCol('UserAccDao')
            colDataList2 = mongoDBCtrl.SearchData('VoteItemDao')
            curIntTime = int(time.time())
            for colData in colDataList2:
                beVoterNameList = []
                for beVoterAcc in colData['beVoterInfoDict'].iterkeys():
                    accColData = col.find_one({'userAcc': beVoterAcc})
                    if accColData:
                        beVoterNameList.append(accColData['userName'])
                beVoterNameDict[colData['Primary']] = beVoterNameList

                canVote = True
                if curIntTime >= (colData["endTime"] + 24 * 60 * 60):
                    canVote = False
                canVoteDict[colData['Primary']] = canVote

        return self.responseTemplate(colDataList=colDataList, userAcc=userAcc, beVoterNameDict=beVoterNameDict, canVoteDict=canVoteDict)

    def redirectLogin(self):
        return redirect('/voter/voterLogin')

    def voterLoginValidate(self, request):
        userName = request.forms.get('username')
        password = request.forms.get('password')
        loginSuccess = False

        userData = UserAccDao(userName);
        if userData.hasData() and userData.userPsw == password and userData.userType == shareDefine.UserAccType_Voter:
            loginSuccess = True
            session = request.environ.get('beaker.session')
            session['voterName'] = userName
            session['voterPsw'] = password
            return self.voteItems(request, False)

        return self.responseTemplate(tplName='voterLogin', loginSuccess=loginSuccess)

    @validate_admin_login_decorator
    def voterLoginOut(self, request):
        session = request.environ.get('beaker.session')
        del session['voterName']
        del session['voterPsw']
        return self.redirectLogin()

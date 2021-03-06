# coding:GBK

from operBase import OperBase
from common.configReader import GetSystemConfig
from bottle import redirect
from dao.userAccDao import UserAccDao
from dao.voteItemDao import VoteItemDao
from common import shareDefine, commonFunc, mongoDBCtrl
import time
from common.utils import get_keypair,get_T,verified_by_admin

def validate_admin_login_decorator(fun):
    def wrapper(self, request, *args, **kwargs):
        if not self.validateVoterLogin(request):
            return self.redirectLogin()
        return fun(self, request, *args, **kwargs)
    return wrapper

def validate_beVoter_login_decorator(fun):
    def wrapper(self, request, *args, **kwargs):
        if not self.validateBeVoterLogin(request):
            return self.redirectbeVoterLogin()
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

    def validateBeVoterLogin(self, request):
        session = request.environ.get('beaker.session')
        sessionVoterName = session.get('beVoterName', None)
        sessionVoterPsw = session.get('beVoterPsw', None)
        if sessionVoterName and sessionVoterPsw:
            return True

        return False

    def voteItems(self, request, isValidateLogin=True, colDataList=None, keywordYear='', keywordName=''):
        if isValidateLogin and not self.validateVoterLogin(request):
            return self.redirectLogin()

        userAcc = self.getUserAcc(request)
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
                if curIntTime >= colData["endTime"]:
                    canVote = False
                canVoteDict[colData['Primary']] = canVote

            colDataList.sort("addVoteTime", -1)

        return self.responseTemplate(colDataList=colDataList, userAcc=userAcc, beVoterNameDict=beVoterNameDict, canVoteDict=canVoteDict, keywordYear=keywordYear, keywordName=keywordName)

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

    @validate_admin_login_decorator
    def findVoteItem(self, request):
        keywordYear = request.GET.get('keywordYear')
        keywordName = request.GET.get('keywordName')

        searchDict = {}
        if keywordYear:
            searchDict['year'] = int(keywordYear)

        if keywordName:
            searchDict['name'] = {'$regex': keywordName}

        userAcc = self.getUserAcc(request)
        voterAcc = 'voterInfoDict.{username}'.format(username=userAcc)
        searchDict[voterAcc] = {'$exists': True}

        col = mongoDBCtrl.GetDataCol('VoteItemDao')
        colDataList = col.find(searchDict)

        return self.voteItems(request, colDataList=colDataList, isValidateLogin=False, keywordName=keywordName, keywordYear=keywordYear)

    @validate_admin_login_decorator
    def doVote(self, request):
        voteItem = request.GET.get('voteItem')
        if not voteItem:
            return self.voteItems(request)

        voteItem = int(voteItem)
        voteItemData = VoteItemDao(voteItem)
        if not voteItemData.hasData():
            return self.voteItems(request)

        # 实名投票在另外一个页面处理
        if not voteItemData.isUnSign:
            return self.doSignVote(request, False, voteItemData, voteItem)

        pubkey, privkey = get_keypair()

        beVoterInfoList = []
        for userAcc, beVoteTicket in voteItemData.beVoterInfoDict.iteritems():
            userData = UserAccDao(userAcc)
            if not userData.hasData():
                continue

            setattr(userData, 'beVoteTicket', beVoteTicket)
            beVoterInfoList.append(userData)

        return self.responseTemplate(pubkey=pubkey, beVoterInfoList=beVoterInfoList, voteItem=voteItem)

    def doSignVote(self, request, isValidateLogin=True, voteItemData=None, voteItem=0, noticket=False, signVoteSuccess=False):
        if isValidateLogin and not self.validateVoterLogin(request) or not voteItemData:
            return self.voteItems(request, False)

        beVoterInfoList = []
        for userAcc, beVoteTicket in voteItemData.beVoterInfoDict.iteritems():
            userData = UserAccDao(userAcc)
            if not userData.hasData():
                continue

            setattr(userData, 'beVoteTicket', beVoteTicket)
            beVoterInfoList.append(userData)

        leftTicket = voteItemData.voterInfoDict[self.getUserAcc(request)]['voterLeftTicket']

        return self.responseTemplate(beVoterInfoList=beVoterInfoList, voteItem=voteItem, noticket=noticket, signVoteSuccess=signVoteSuccess, leftTicket=leftTicket)

    @validate_admin_login_decorator
    def signVote(self, request):
        beVoterSeq = request.POST.get('beVoterSeq')
        voteItem = int(request.POST.get('voteItem'))

        beVoterIDList = beVoterSeq.split('_')
        voterAcc = self.getUserAcc(request)
        voteItemData = VoteItemDao(voteItem)
        leftTicket = voteItemData.voterInfoDict[voterAcc]['voterLeftTicket']
        if leftTicket < len(beVoterIDList):
            return self.doSignVote(request, False, voteItemData, voteItem, True)

        for beVoterID in beVoterIDList:
            self.voteLogic(int(beVoterID), voteItemData, request, voteItem)

        return self.doSignVote(request, False, voteItemData, voteItem, signVoteSuccess=True)

    def voteLogic(self, beVoterSeqID, voteItemData, request, voteItem):
        col = mongoDBCtrl.GetDataCol('UserAccDao')
        colData = col.find_one({'seqKey': beVoterSeqID})

        voterAcc = self.getUserAcc(request)

        voteItemData.voterInfoDict[voterAcc]['voterLeftTicket'] -= 1
        voteItemData.beVoterInfoDict[colData['userAcc']] += 1

        voterVoteRecDict = voteItemData.voterInfoDict[voterAcc]['voteRec']
        voterVoteInfoList = voterVoteRecDict.get(colData['userAcc'], [])
        voterVoteInfoList.append(int(time.time()))
        voterVoteRecDict[colData['userAcc']] = voterVoteInfoList

        voteItemData.saveData()
        return

    def unsignVote(self, request):
        session = request.environ.get('beaker.session')
        if session.has_key('voterName'):
            del session['voterName']
            del session['voterPsw']
        return self.responseTemplate()

    @validate_admin_login_decorator
    def getUnsignTicket(self, request):
        userAcc = self.getUserAcc(request)
        userAccData = UserAccDao(userAcc)
        if not userAccData.hasData():
            return 'error'

        voteItem = request.POST.get('voteItem')
        if not voteItem:
            return 'error'

        voteItemData = VoteItemDao(int(voteItem))
        if not voteItemData.hasData():
            return 'error'

        C = request.POST.get('C')
        if not C:
            return 'error'

        leftTicket = voteItemData.voterInfoDict[userAcc]['voterLeftTicket']
        if leftTicket < 1:
            return 'noticket'

        T = get_T(int(C))

        voteItemData.voterInfoDict[userAcc]['voterLeftTicket'] -= 1
        voteItemData.saveData()
        return str(T)

    def getUserAcc(self, request):
        session = request.environ.get('beaker.session')
        return session['voterName']

    def doUnsignVote(self, request):
        voteKey = request.POST.get('vote_key')
        if not voteKey:
            return self.unsignVote(request)

        voteKeyList = self.getVoteKey()
        if voteKey in voteKeyList:
            return self.responseTemplate(tplName='unsignVote', voteKeyVotd=True, voteKey=voteKey)

        m = 0
        U = 0
        S = 0
        try:
            voteKeyStrList = voteKey.split(',')
            m = int(voteKeyStrList[0].strip()[1:])
            U = int(voteKeyStrList[1].strip())
            S = int(voteKeyStrList[2].strip()[:-1])
        except:
            return self.responseTemplate(tplName='unsignVote', voteKeyFormatError=True, voteKey=voteKey)

        if not verified_by_admin(m, U, S):
            return self.responseTemplate(tplName='unsignVote', voteKeyError=True, voteKey=voteKey)

        voteItem = int(str(m)[:-4])
        userSeq = int(str(m)[4:])

        col = mongoDBCtrl.GetDataCol('UserAccDao')
        colData = col.find_one({'seqKey':userSeq})

        voteItemData = VoteItemDao(voteItem)
        voteItemData.beVoterInfoDict[colData['userAcc']] += 1
        voteItemData.saveData()

        voteKeyList.append(voteKey)
        self.saveVoteKey(voteKeyList)

        return self.responseTemplate(tplName='unsignVote', voteSuccess=True)

    def saveVoteKey(self, voteKeyList):
        col = mongoDBCtrl.GetDataCol('VoteKeyDao')
        if col.find().count() < 1:
            col.insert({'Primary':1, 'voteKeyList':voteKeyList})
        else:
            col.update({'Primary':1}, {'$set': {'voteKeyList':voteKeyList}})
        return

    def getVoteKey(self):
        col = mongoDBCtrl.GetDataCol('VoteKeyDao')
        if col.find().count() < 1:
            return []
        return col.find_one()['voteKeyList']

    @validate_admin_login_decorator
    def editVoter(self, request):
        userAcc = self.getUserAcc(request)
        userData = UserAccDao(userAcc)
        return self.responseTemplate(userAccDao=userData, userType=shareDefine.UserAccType_Voter, isVoter=True, noPsw=True)

    @validate_admin_login_decorator
    def editVoterData(self, request):
        userAcc = self.getUserAcc(request)
        userData = UserAccDao(userAcc)

        self.setAddData(request, userData)
        userData.saveData()

        return self.responseTemplate(tplName="editVoter", userAccDao=userData, userType=shareDefine.UserAccType_Voter, isVoter=True, success=True, noPsw=True)

    @validate_admin_login_decorator
    def changePsw(self, request):
        return self.responseTemplate()

    @validate_admin_login_decorator
    def doChangePsw(self, request):
        userAcc = self.getUserAcc(request)
        userData = UserAccDao(userAcc)

        if userData.userPsw != request.POST.get('passwordOld'):
            return self.responseTemplate(tplName='changePsw', oldPswErr=True)

        userData.userPsw = request.POST.get('passwordNew')
        userData.saveData()

        return self.responseTemplate(tplName='changePsw', changeSuccess=True)





#---------------------------------------参评人-------------------------------------------

    def beVoterLogin(self, request):
        return self.responseTemplate()

    def beVoterLoginValidate(self, request):
        userName = request.forms.get('username')
        password = request.forms.get('password')
        loginSuccess = False

        userData = UserAccDao(userName);
        if userData.hasData() and userData.userPsw == password and userData.userType == shareDefine.UserAccType_BeVoter:
            loginSuccess = True
            session = request.environ.get('beaker.session')
            session['beVoterName'] = userName
            session['beVoterPsw'] = password

            return self.editBeVoter(request)

        return self.responseTemplate(tplName='beVoterLogin', loginSuccess=loginSuccess)

    @validate_beVoter_login_decorator
    def editBeVoter(self, request):
        userAcc = self.getBeVoterAcc(request)
        userData = UserAccDao(userAcc)
        return self.responseTemplate(tplName='editVoter', userAccDao=userData, userType=shareDefine.UserAccType_BeVoter, isBeVoter=True, noPsw=True)

    def getBeVoterAcc(self, request):
        session = request.environ.get('beaker.session')
        return session['beVoterName']

    @validate_beVoter_login_decorator
    def editBeVoterData(self, request):
        userAcc = self.getBeVoterAcc(request)
        userData = UserAccDao(userAcc)

        self.setAddData(request, userData)
        userData.saveData()

        return self.responseTemplate(tplName="editVoter", userAccDao=userData, userType=shareDefine.UserAccType_BeVoter,
                                     isBeVoter=True, success=True, noPsw=True)

    @validate_beVoter_login_decorator
    def changeBeVoterPsw(self, request):
        return self.responseTemplate(tplName='changePsw', isBeVoter=True)

    @validate_beVoter_login_decorator
    def doChangeBeVoterPsw(self, request):
        userAcc = self.getBeVoterAcc(request)
        userData = UserAccDao(userAcc)

        if userData.userPsw != request.POST.get('passwordOld'):
            return self.responseTemplate(tplName='changePsw', isBeVoter=True, oldPswErr=True)

        userData.userPsw = request.POST.get('passwordNew')
        userData.saveData()

        return self.responseTemplate(tplName='changePsw', changeSuccess=True, isBeVoter=True)

    @validate_beVoter_login_decorator
    def beVoterLoginOut(self, request):
        session = request.environ.get('beaker.session')
        del session['beVoterName']
        del session['beVoterPsw']
        return self.redirectbeVoterLogin()

    def redirectbeVoterLogin(self):
        return redirect('/voter/beVoterLogin')

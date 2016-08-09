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

        pubkey, privkey = get_keypair()

        beVoterInfoList = []
        for userAcc, beVoteTicket in voteItemData.beVoterInfoDict.iteritems():
            userData = UserAccDao(userAcc)
            if not userData.hasData():
                continue

            setattr(userData, 'beVoteTicket', beVoteTicket)
            beVoterInfoList.append(userData)

        return self.responseTemplate(pubkey=pubkey, beVoterInfoList=beVoterInfoList, voteItem=voteItem)

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
            U = int(voteKeyStrList[1])
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

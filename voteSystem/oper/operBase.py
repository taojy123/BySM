from bottle import template
import traceback
from common.mongoDBCtrl import GetDataCol
from common import shareDefine, commonFunc

class OperBase():
    def __init__(self):

        return

    def getIntUserType(self, request, isPost=True):
        if isPost:
            userType = request.forms.get('userType')
        else:
            userType = request.GET.get('userType')

        if userType == None:
            userType = shareDefine.UserAccType_Voter

        userType = int(userType)
        return userType

    def responseTemplate(self, **kwargs):
        tplName = ''
        if kwargs.has_key('tplName'):
            tplName = kwargs['tplName']
        else:
            stackInfo = traceback.format_stack()[-2]
            start = stackInfo.find('in ') + 3
            end = stackInfo.find('\n')
            tplName = stackInfo[start:end]

        return template(tplName + '.html', kwargs)

    def getNextSeq(self, tableName, startID=1):
        col = GetDataCol(tableName)
        seqData = col.find_one()
        if not seqData:
            seqData = {'seq':startID}
            col.insert(seqData)
            nextSeq = startID
        else:
            curSeq = seqData['seq']
            nextSeq = curSeq + 1
            seqData['seq'] = nextSeq
            col.update({'seq':curSeq}, seqData)

        return nextSeq

    def setAddData(self, request, userAccDao):
        name = request.forms.get('name')
        shenfenzheng = request.forms.get('shenfenzheng')
        shengri = request.forms.get('shengri')
        if shengri:
            shengri = commonFunc.GetIntMillisecondByFormatStr(shengri)
        sex = request.forms.get('sex')
        zhicheng = request.forms.get('zhicheng')
        zhichengLv = request.forms.get('zhichengLv')
        zhiwu = request.forms.get('zhiwu')
        zuigaoxueli = request.forms.get('zuigaoxueli')
        jianjie = request.forms.get('jianjie')
        biyeyuanxiao = request.forms.get('biyeyuanxiao')
        ruzhishijian = request.forms.get('ruzhishijian')
        if ruzhishijian:
            ruzhishijian = commonFunc.GetIntMillisecondByFormatStr(ruzhishijian)

        zhuyaojingli = request.forms.get('zhuyaojingli')
        xueshuchengguo = request.forms.get('xueshuchengguo')
        huojiangxinxi = request.forms.get('huojiangxinxi')

        remark = request.forms.get('remark')
        if len(remark) > 200:
            remark = remark[:200]

        userAccDao.userName = name
        userAccDao.shenfenzheng = shenfenzheng
        userAccDao.shengri = shengri
        userAccDao.sex = sex
        userAccDao.zhicheng = zhicheng
        userAccDao.zhichengLv = zhichengLv
        userAccDao.zhiwu = zhiwu
        userAccDao.zuigaoxueli = zuigaoxueli
        userAccDao.jianjie = jianjie
        userAccDao.biyeyuanxiao = biyeyuanxiao
        userAccDao.ruzhishijian = ruzhishijian
        userAccDao.zhuyaojingli = zhuyaojingli
        userAccDao.xueshuchengguo = xueshuchengguo
        userAccDao.huojiangxinxi = huojiangxinxi

        userAccDao.remark = remark
        return
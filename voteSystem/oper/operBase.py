from bottle import template
import traceback
from common.mongoDBCtrl import GetDataCol

class OperBase():
    def __init__(self):

        return

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
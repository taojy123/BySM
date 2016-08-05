from bottle import route, run, abort, static_file, template, get, post, request, response, redirect, view
import bottle
from common import configReader
from common.operMapping import OperClassNameList
from oper.adminOper import AdminOper

@route('/static/<filepath:path>')
def server_static(filepath):
    return static_file(filepath, root='./static')


@route('/admin/:funcName')
@route('/admin/:funcName/')
def admin_oper(funcName = ''):
    global g_operClassObj

    operClassObj = g_operClassObj.get('AdminOper', None)
    if operClassObj and hasattr(operClassObj, funcName):
        return getattr(operClassObj, funcName)(request)

    abort(404, 'Page Not Found!')

g_operClassObj = {}

def initOperClass():
    global  g_operClassObj
    for className in OperClassNameList:
        operObj = getClass(className)
        g_operClassObj[className] = operObj
    return

def getClass(className):
    return eval(className + '()')

if '__main__' == __name__:
    bottle.TEMPLATES.clear()
    initOperClass()
    run(host=configReader.GetSystemConfig().webPos, port=configReader.GetSystemConfig().webPort)

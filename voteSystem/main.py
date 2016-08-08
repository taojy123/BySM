import StringIO

import BeautifulSoup
import xlwt

from bottle import route, run, abort, static_file, template, get, post, request, response, redirect, view, hook
import bottle
from common import configReader
from common.operMapping import OperClassNameList
import bottle_beaker as beaker
from oper.adminOper import AdminOper
from oper.voterOper import VoterOper


@hook('before_request')
def strip_path():
    request.environ['PATH_INFO'] = request.environ['PATH_INFO'].rstrip('/')


@route('/static/<filepath:path>')
def server_static(filepath):
    return static_file(filepath, root='./static')


@route('/admin/:funcName', method=["GET", "POST"])
def admin_oper(funcName=''):
    return operPro(funcName, 'AdminOper')

@route('/voter/:funcName', method=["GET", "POST"])
def voter_oper(funcName=''):
    return operPro(funcName, 'VoterOper')

def operPro(funcName, operName):
    global g_operClassObj

    operClassObj = g_operClassObj.get(operName, None)
    if operClassObj and hasattr(operClassObj, funcName):
        return getattr(operClassObj, funcName)(request)

    return abort(404, 'Page Not Found!')

g_operClassObj = {}

def initOperClass():
    global  g_operClassObj
    for className in OperClassNameList:
        operObj = getClass(className)
        g_operClassObj[className] = operObj
    return

def getClass(className):
    return eval(className + '()')


@post('/output', method="POST")
def output():
    data = request.params.data
    begin_index = int(request.params.get('begin_index', 0))
    end_index = int(request.params.get('end_index', -1))

    wb = xlwt.Workbook()
    ws = wb.add_sheet('output')

    soup = BeautifulSoup.BeautifulSoup(data)

    thead_soup = soup.find('thead')
    th_soups = thead_soup.findAll('th')
    th_soups = th_soups[begin_index:end_index]

    j = 0
    for th_soup in th_soups:
        th = th_soup.getText()
        ws.write(0, j, th)
        j += 1

    tbody_soup = soup.find('tbody')
    tr_soups = tbody_soup.findAll('tr')

    i = 1
    for tr_soup in tr_soups:
        td_soups = tr_soup.findAll('td')
        td_soups = td_soups[begin_index:end_index]

        j = 0
        for td_soup in td_soups:
            td = td_soup.getText()
            ws.write(i, j, td)
            j += 1

        i += 1

    s = StringIO.StringIO()
    wb.save(s)
    s.seek(0)
    data = s.read()

    response.headers['Content-Type'] = 'application/octet-stream'
    response.headers['Content-Disposition'] = 'attachment;filename="output.xls"'

    return data


app = beaker.middleware.SessionMiddleware(bottle.app(), configReader.GetSystemConfig().session_opts)


if '__main__' == __name__:
    bottle.TEMPLATES.clear()
    initOperClass()
    run(app=app, host=configReader.GetSystemConfig().webPos, port=configReader.GetSystemConfig().webPort)

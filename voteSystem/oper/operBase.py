from bottle import template
import traceback

class OperBase():
    def __init__(self):

        return

    def responseTemplate(self, **kwargs):
        stackInfo = traceback.format_stack()[-2]
        start = stackInfo.find('in ') + 3
        end = stackInfo.find('\n')
        tplName = stackInfo[start:end]
        return template(tplName, kwargs)
testStr = '  File "F:\\voteSystem\\trunk\\proj\\server\\oper\\adminOper.py", line 11, in adminLogin\n    print traceback.format_stack()\n'
start = testStr.find('in ') + 3
end = testStr.find('\n')
print start
print end
print testStr[start:end]
print len(testStr[start:end])
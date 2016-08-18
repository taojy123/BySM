# coding:GBK
DaoStruct = {
'UserAccDao':{
    'userAcc':str,
    'userPsw':str,
    'userName':str,
    'userType':int,
    'regTime':int,
    'seqKey':int,
    'shenfenzheng':str,
    'shengri':int,
    'sex':int,
    'zhicheng':str,
    'zhichengLv':str,
    'zhiwu':str,
    'zuigaoxueli':str,
    'remark':str,
#--------评委-------------
    'jianjie':str,
#--------参评人-----------
    'biyeyuanxiao':str,
    'ruzhishijian':int,
    'zhuyaojingli':str,
    'xueshuchengguo':str,
    'huojiangxinxi':str
},

'VoteItemDao':{
    'seqID':int,
    'year':int,
    'name':str,
    'voterTicketCnt':int,
    'beVoterPassCnt':int,
    'isUnSign':int,
    'voterInfoDict':dict,
    # {
    #     评委账号:{
    #         'voterLeftTicket': 持有票数,
    #         'voteRec':{
    #             '参评人账号名':[
    #                 投票时间
    #             ]
    #         }
    #     }
    # }
    'beVoterInfoDict':dict,
    # {
    #     参评人账号:参评人被投票数
    # }
    'remark':str,
    'endTime':int,
    'addVoteTime':int
}
}
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
#--------��ί-------------
    'jianjie':str,
#--------������-----------
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
    #     ��ί�˺�:{
    #         'voterLeftTicket': ����Ʊ��,
    #         'voteRec':{
    #             '�������˺���':[
    #                 ͶƱʱ��
    #             ]
    #         }
    #     }
    # }
    'beVoterInfoDict':dict,
    # {
    #     �������˺�:�����˱�ͶƱ��
    # }
    'remark':str,
    'endTime':int,
    'addVoteTime':int
}
}
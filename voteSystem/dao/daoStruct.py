# coding:GBK
DaoStruct = {
'UserAccDao':{
    'userAcc':str,
    'userPsw':str,
    'userName':str,
    'userType':int,
    'regTime':int,
    'remark':str,
    'seqKey':int,
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
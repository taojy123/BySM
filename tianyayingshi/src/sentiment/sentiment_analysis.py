#import csv
#import pymongo
from snownlp import SnowNLP
import sys
import copy
sys.path.append("../")
import jieba
from pymongo import MongoClient

client = MongoClient()
client = MongoClient('localhost',27017)
db = client.MongoDB
collection = db.blogposts
collection2 = db.movieList

def sentiment_analysis(post):
    comment_sentiment=[]
    a=0
    while a<len(post['reply_content_list']):

        reply_content = post['reply_content_list'][a]['reply_content']
                
        sentence_list = []
        for sentence in SnowNLP(reply_content).sentences:
            numbers = SnowNLP(sentence).sentiments
            sentence_list.append(numbers)

        a=a+1

        if len(sentence_list) != 0:
            
            average = float(sum(sentence_list))/len(sentence_list)
        
            comment_sentiment.append(average)
        

    collection.update({"_id":post['_id']},{'$set':{'comment_sentiment':comment_sentiment}},upsert=False,multi=False) ##update to MongoDB


    #click_count = post['click_count']
    #reply_count = post['reply_count']


    #cal = float(post['click_count'])*0.2 + float(len(post['reply_count']))*0.8
    cal = float(post['click_count'])*0.2 + float(post['reply_count'])*0.8
    collection.update({"_id":post['_id']},{'$set':{'popularity':cal}},upsert=False,multi=False)

# def compareTitle():
#     index = 0
#     movie_title = []
#     for names in collection2.find():
#         while (index < len(names['movie_name'])):
#             
#             name = names['movie_name'][index]
#         
#             if name in post['title']:
#                 movie_title.append(name)
# 
#             index=index+1
# 
#         collection.update({"_id":post['_id']},{'$set':{'movie_title':movie_title}},upsert=False,multi=False)

def filterSentence(sentence):
    stop_file = open('stop-words_chinese_1_zh.txt','r')  ##open file from .txt
    for line in stop_file.readlines():
        line = line.strip()
        line = tryEncode(line)
        sentence = tryEncode(sentence)
        if line in sentence:
            sentence = replaceAllSameWord(line, sentence)
    return sentence

def replaceAllSameWord(line, sentence):
    while True:
        sentence = sentence.replace(line,"")      ##remove the stopword
        if line not in sentence:
            break
    return sentence

def tryEncode(strarg):
    try:
        strarg = strarg.decode('gbk')
    except:
        try:
            strarg = strarg.decode('utf-8')
        except:
            pass
    return strarg

def segComment(post): #return a list
    result_list = []
    i=0
    while i<len(post['reply_content_list']):
        reply_content = filterSentence(post['reply_content_list'][i]['reply_content'])
        i=i+1
        result = jieba.cut_for_search(reply_content)
        result = generatorToList(result)
        result_list.append(result)
    return result_list

def removeRepeat(result_list):
    norepeat_list = []
    for result in result_list:
        if not result in norepeat_list:
            norepeat_list.append(result)
    return norepeat_list
    
def findSentimentWord(result):
    positive_word_file_path = 'positive_sentiment_words.txt'
    negative_word_file_path = 'negative_sentiment_words.txt'
    pos_indexList = []
    neg_indexList = []
    index = 0
    for result_word in result:
        result_word = tryEncode(result_word)
        word_type = getSentimentWordIndex(positive_word_file_path, result_word)
        if word_type:
            pos_indexList.append(index)
        else:
            word_type = getSentimentWordIndex(negative_word_file_path, result_word)
            if word_type:
                neg_indexList.append(index)
        index += 1
 
    return pos_indexList,neg_indexList

def getSentimentWordIndex(file_name, result_word):
    words_file = open(file_name,'r')
    for word in words_file.readlines():
        word = word.strip()
        word = tryEncode(word)
        if word == result_word:
            return 1
    return 0
        
def bef_and_aft(post, pos_indexList, neg_indexList, result):
    pos_keywordList=[]
    for pos_index in pos_indexList:
        keyword1 = getKeyWord(result,pos_index-2)
        keyword2 = getKeyWord(result,pos_index-1)
        keyword3 = getKeyWord(result,pos_index+1)
        keyword4 = getKeyWord(result,pos_index+2)
        pos_keywordList.append([keyword1,keyword2,keyword3,keyword4])
 
    neg_keywordList=[]
    for neg_index in neg_indexList:
        keyword1 = getKeyWord(result,neg_index-2)
        keyword2 = getKeyWord(result,neg_index-1)
        keyword3 = getKeyWord(result,neg_index+1)
        keyword4 = getKeyWord(result,neg_index+2)
        neg_keywordList.append([keyword1,keyword2,keyword3,keyword4])

    print pos_keywordList
    print neg_keywordList

    pos_keywordList = collection.find({ "_id" : post['_id'] })[0]['pos_keywords'] + pos_keywordList
    neg_keywordList = collection.find({ "_id" : post['_id'] })[0]['neg_keywords'] + neg_keywordList
        
    collection.update({"_id":post['_id']},{'$set':{'pos_keywords':pos_keywordList}},upsert=True,multi=False)
    collection.update({"_id":post['_id']},{'$set':{'neg_keywords':neg_keywordList}},upsert=True,multi=False)


    return
    
def getKeyWord(result, index):
    keyWord = ''
    try:
        keyWord = result[index]
    except:
        pass
    return keyWord

def generatorToList(generator):
    parse_list = []
    for item in generator:
        parse_list.append(item)
    return parse_list

def addKeyWordsField(post):
    collection.update({"_id":post['_id']},{'$set':{'pos_keywords':[]}},upsert=False,multi=False)
    collection.update({"_id":post['_id']},{'$set':{'neg_keywords':[]}},upsert=False,multi=False)
    return

if __name__ == '__main__':
    i = 0
    for post in collection.find():
        print "===================", i, "=========================="
        i += 1
        sentiment_analysis(post)
        result_list = segComment(post)
        addKeyWordsField(post)
        for result in result_list:
            result = removeRepeat(result)
            pos_indexList,neg_indexList = findSentimentWord(result)
            bef_and_aft(post, pos_indexList, neg_indexList, result)
    print 'Chinese Sentiment Analysis Success!'
    
    
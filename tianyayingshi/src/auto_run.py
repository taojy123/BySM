import time
import os


while True:

    print "--------------------- begin ---------------------"

    # cmd1 = "c:\Python27\Scripts\scrapy.exe crawl tianyaSpider"
    cmd1 = "scrapy crawl tianyaSpider"
    os.system(cmd1)

    time.sleep(5)

    os.chdir("./sentiment")

    # cmd2 = "c:\Python27\python.exe sentiment_analysis.pyc"
    cmd2 = "python sentiment_analysis.pyc"
    os.system(cmd2)

    os.chdir("..")


    print "--------------------- finish ---------------------"

    time.sleep(1800)




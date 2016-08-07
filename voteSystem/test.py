a = "2016-8-7"
import time
timeArray = time.strptime(a, "%Y-%m-%d")
timeStamp = int(time.mktime(timeArray))
print timeStamp

print time.time()
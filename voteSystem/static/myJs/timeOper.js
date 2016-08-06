var serverMilliSecToStr = function(milliSec){
    var dateObj = new Date(milliSec*1000);
    Year = dateObj.getFullYear();
    Month= dateObj.getMonth()+1;
    Day = dateObj.getDate();
    Hour = dateObj.getHours();
    Minute = dateObj.getMinutes();
    Second = dateObj.getSeconds();

    CurrentDate = '';
    CurrentDate += Year + "-";
    CurrentDate += get2lengthTimeStr(Month) + '-';
    CurrentDate += get2lengthTimeStr(Day) + ' ';
    CurrentDate += get2lengthTimeStr(Hour) + ':';
    CurrentDate += get2lengthTimeStr(Minute) + ':';
    CurrentDate += get2lengthTimeStr(Second);
    return CurrentDate;
}

var get2lengthTimeStr = function(time){
    if (time >= 10 ) return time.toString()
    return '0' + time.toString()
}
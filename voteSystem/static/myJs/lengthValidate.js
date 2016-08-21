var userNameValiDate = function(){
    return valiDateCommon('userNameValidate', '工作证号', 4)
};

var userPswValiDate = function(){
    return valiDateCommon('passwordValiDate', '密码', 20)
};

var valiDateCommon = function(id, validateStr, length){
    var obj = document.getElementById(id);
    if(!obj) return true;

    var hidden = true;

    if(obj.previousElementSibling){
        if(validateStr == '工作证号'){
            if(obj.previousElementSibling.value.length != 4){
                obj.innerText = validateStr + '长度必须为4位';
                hidden = false;
            }
        }else{
            if(obj.previousElementSibling.value.length < 1){
                hidden = false;
                obj.innerText = validateStr + '不能为空';
            }else if(obj.previousElementSibling.value.length >= length){
                hidden = false;
                obj.innerText = '长度不能超过' + length;
            }
        }
    }

    if(hidden == false) setTimeout('document.getElementById("' + id + '").hidden = true', 3000);

    obj.hidden = hidden;
    return hidden;
};

var valiDateNameAndPsw = function(){
    if(!userNameValiDate()) return false;
    if(!userPswValiDate()) return false;

    return true;
};

var validateVoterInfo = function(checkName){
    if(checkName == undefined) checkName = true;

    if(checkName && !userNameValiDateEx()) return false;

    if(!checkShenfenzheng()){
        showAffirm('身份证号格式不正确')
        return false;
    }

    if($('#shengri').val() && !dateValidate('#shengri')) return false;

    if($('#ruzhishijian').val() && !dateValidate('#ruzhishijian')) return false;

    return true;
}

var dateValidate = function(id){
        var dateStr = $(id).val();
        var regExp = /^(\d{4})\-(\d{2})\-(\d{2})$/;

        if(!regExp.test(dateStr)){
            showAffirm('日期格式请按照yyyy-mm-dd格式输入');
            return false;
        }

        var year = dateStr.split('-')[0];
        if(year < 1970){
            showAffirm('年份不能小于1970年');
            return false;
        }

        return true;
};

var checkNoInput = function(id, affirmName, checkIsNaN){
        var value = $(id).val();
        var valueLen = value.length;

        if(!valueLen){
            showAffirm('请输入' + affirmName);
            return false;
        }

        if(checkIsNaN){
            var isString = isNaN(value);
            if(isString){
                showAffirm(affirmName + '请输入数字');
                return false;
            }else if(parseInt(value) == 0){
                showAffirm(affirmName + '不能为0');
                return false;
            }
        }

        return true;
};

var userNameValiDateEx = function(){
    var userName = $('#userName').val();
    if(!userName || userName.length !=4){
        showAffirm('工作证号长度必须为4');
        return false;
    }

    var name = $('#name').val();
    if(!name){
        showAffirm('姓名不能为空');
        return false;
    }

    return true;
};

var aCity={11:"北京",12:"天津",13:"河北",14:"山西",15:"内蒙古",21:"辽宁",22:"吉林",23:"黑龙江",31:"上海",32:"江苏",33:"浙江",34:"安徽",35:"福建",36:"江西",37:"山东",41:"河南",42:"湖北",43:"湖南",44:"广东",45:"广西",46:"海南",50:"重庆",51:"四川",52:"贵州",53:"云南",54:"西藏",61:"陕西",62:"甘肃",63:"青海",64:"宁夏",65:"新疆",71:"台湾",81:"香港",82:"澳门",91:"国外"}
var  checkShenfenzheng = function(){
    var sId = $('#shenfenzheng').val();
    if(sId == '') return true;

    var iSum=0 ;
    var info="" ;
    if(!/^\d{17}(\d|x)$/i.test(sId)) return false;
    sId=sId.replace(/x$/i,"a");
    if(aCity[parseInt(sId.substr(0,2))]==null) return false;
    var sBirthday=sId.substr(6,4)+"-"+Number(sId.substr(10,2))+"-"+Number(sId.substr(12,2));
    var d=new Date(sBirthday.replace(/-/g,"/")) ;
    if(sBirthday!=(d.getFullYear()+"-"+ (d.getMonth()+1) + "-" + d.getDate()))return false;
    for(var i = 17;i>=0;i --) iSum += (Math.pow(2,i) % 11) * parseInt(sId.charAt(17 - i),11) ;
    if(iSum%11!=1) return false;
    //aCity[parseInt(sId.substr(0,2))]+","+sBirthday+","+(sId.substr(16,1)%2?"男":"女");//此次还可以判断出输入的身份证号的人性别
    return true;
};

var showAffirm = function(affirm){
    if(!affirm) return;
    $('#alertInfo').attr('hidden', false);
    $('#alertInfo').html(affirm);
}

var fileValiDate = function(){
     var filepath = $("input[name='file']").val();
    console.log(filepath)
     if(!filepath){
         alert('请先选择excel文件再导入')
         return false;
     }

     var extStart = filepath.lastIndexOf(".");
     var ext = filepath.substring(extStart, filepath.length).toUpperCase();
     if (ext != ".XLS" && ext != ".XLSX") {
         alert("excel文件限于xls,xlsx格式");
         return false;
     }
    $('.main').html('导入中...')
    return true;
}
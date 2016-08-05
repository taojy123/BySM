var userNameValiDate = function(){
    return valiDateCommon('userNameValidate', '用户名', 20)
};

var userPswValiDate = function(){
    return valiDateCommon('passwordValiDate', '密码', 20)
};

var valiDateCommon = function(id, validateStr, length){
    var obj = document.getElementById(id);
    if(!obj) return true;

    var hidden = true;

    if(obj.previousElementSibling){
        if(obj.previousElementSibling.value.length < 1){
            hidden = false;
            obj.innerText = validateStr + '不能为空';
        }else if(obj.previousElementSibling.value.length >= length){
            hidden = false;
            obj.innerText = '长度不能超过' + length;
        }
    }
    console.log(id)
    if(hidden == false) setTimeout('document.getElementById("' + id + '").hidden = true', 3000);

    obj.hidden = hidden;
    return hidden;
};

var valiDateNameAndPsw = function(){
    if(!userNameValiDate()) return false;
    if(!userPswValiDate()) return false;

    return true;
};

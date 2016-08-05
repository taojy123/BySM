
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">

    <title>投票管理系统</title>

    <link href="/static/css/bootstrap.css" rel="stylesheet">
    <link href="/static/css/bootstrap-table.css" rel="stylesheet"/>
    <link href="/static/css/dashboard.css" rel="stylesheet">
    <link href="/static/css/jquery.searchableSelect.css" rel="stylesheet">
    <link href="/static/css/bootstrap-datetimepicker.css" rel="stylesheet">

    <script src="/static/js/jquery-1.10.2.js"></script>
    <script src="/static/js/bootstrap.js"></script>
    <script src="/static/js/bootstrap-table.js"></script>
    <script src="/static/js/jquery.searchableSelect.js"></script>
    <script src="/static/js/bootstrap-datetimepicker.js"></script>
    <script src="/static/js/locales/bootstrap-datetimepicker.zh-CN.js"></script>
    <script src="/static/myJs/lengthValidate.js"></script>
    <style>
        .form-control{
            display:inline;
            width:auto;
        }
        .form-group{
            white-space:nowrap;
        }
        .form_datetime{
            float: left;
        }
        
            .staff_required{
                display: none !important;
            }
        
    </style>

</head>

<body>

<div class="navbar navbar-inverse navbar-fixed-top" role="navigation">
    <div class="container-fluid">
        <div class="navbar-header">
            <button type="button" class="navbar-toggle collapsed" data-toggle="collapse" data-target=".navbar-collapse">
                <span class="sr-only">Toggle navigation</span>
                <span class="icon-bar"></span>
                <span class="icon-bar"></span>
                <span class="icon-bar"></span>
            </button>
            <a class="navbar-brand" href="/">投票管理系统</a>
        </div>
        <div id="navbar" class="navbar-collapse collapse">
            <ul class="nav navbar-nav navbar-right">
                <li><a href="/">欢迎</a></li>
            </ul>
        </div><!--/.nav-collapse -->
    </div>
</div>

<div class="container-fluid">
    <div class="row">

        <div class="col-sm-3 col-md-2 sidebar">

            <ul class="nav nav-sidebar">

                <li id="shops"><a href="/shops/">Shop Management</a></li>
                <li id="appointments"><a href="/appointments/">Appointment Scheduling</a></li>
                <li id="customers"><a href="/customers/">Client Management</a></li>
                <li id="gift_cards"><a href="/gift_cards/">Gift Card Management</a></li>
                <li id="sessions"><a href="/sessions/">POS</a></li>
                <li id="reminders"><a href="/reminders/">Remind Settings</a></li>

                <li id="login"><a href="/admin/adminLogin">登录</a></li>
                

            </ul>
        </div>

        <div class="col-sm-9 col-sm-offset-3 col-md-10 col-md-offset-2 main">

            
    <h2 class="sub-header">登录</h2>

    

    <form id="form" action="." method="POST" class="form-horizontal">

        <input type="hidden" name="next" value="/customers/">

        <div class="form-group">
            <label  class="col-sm-2 control-label" >用户名:</label>
            <input type="text" class="form-control"  style="display:inline;width:auto;" name="username" >
            <label class="alert alert-danger control-label" id="userNameValidate" hidden="true"></label>
        </div>

        <div class="form-group">
            <label  class="col-sm-2 control-label" >密码:</label>
            <input type="password" class="form-control"  style="display:inline;width:auto;" name="password" >
            <label class="alert alert-danger control-label" id="passwordValiDate" hidden="true"></label>
        </div>

        <div class="form-group">
            <label  class="col-sm-2 control-label" ></label>
            <button type="submit" class="btn btn-success" onclick="return valiDateNameAndPsw()">登录</button>
        </div>
    </form>


    <script>
        $("#login").addClass('active')
    </script>



        </div>
    </div>
</div>

<script>
    $('.search').searchableSelect();

    $(".form_datetime").datetimepicker({
        format: 'yyyy-mm-dd',
        autoclose: true,
        todayBtn: true,
        minView: 2,
        language: 'zh-CN'
    });
</script>




</body>
</html>

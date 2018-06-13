(function($,window){
    var $subChk = $("input[name='subChk']");
    var setResource;
    roleList = {
        //初始化
        init: function(){
            //显示隐藏列
            var menu_text = "";
            var table = $("#dataTable tr th:gt(1)");
            menu_text += "<li><label><input type=\"checkbox\" checked=\"checked\" class=\"toggle-vis\" data-column=\"" + parseInt(2) +"\" disabled />"+ table[0].innerHTML +"</label></li>"
            for(var i = 1; i < table.length; i++){
                menu_text += "<li><label><input type=\"checkbox\" checked=\"checked\" class=\"toggle-vis\" data-column=\"" + parseInt(i+2) +"\" />"+ table[i].innerHTML +"</label></li>"
            };
            $("#Ul-menu-text").html(menu_text);
            //表格列定义
            var columnDefs = [ {
                //第一列，用来显示序号
                "searchable" : false,
                "orderable" : false,
                "targets" : 0
            } ];
            var columns = [
                {
                    //第一列，用来显示序号
                    "data" : null,
                    "class" : "text-center"
                },
                {
                    "data" : null,
                    "class" : "text-center",
                    render : function(data, type, row, meta) {
                        var idStr = row.idstr;
                        var result = '';
                        result += '<input  type="checkbox" name="subChk"  value="' + idStr + '" />';
                        return result;
                    }
                },
                {
                    "data" : null,
                    "class" : "text-center", //操作按钮
                    render : function(data, type, row, meta) {
                        var idStr = row.idstr;
                        console.log('idstr:',idStr);
                        var editUrlPath = myTable.editUrl + idStr ; //修改地址
                        var result = '';
                        //修改按钮
                        var isAdminStr = $("#isAdmin").attr("value");
                        var isAdmin = isAdminStr == 'true';
                        if (isAdmin && idStr == 'ROLE_ADMIN') { // 若为超级管理员，禁用超级管理员角色的修改按钮 
                        	 result += '<button disabled href="'+editUrlPath+'" data-target="#commonSmWin" data-toggle="modal"  type="button" class="editBtn btn-default deleteButton"><i class="fa fa-ban"></i>修改</button>&nbsp;';
                        }else if (!isAdmin && (idStr == 'ROLE_ADMIN' || idStr == 'POWER_USER')) {  // 若为普通管理员，禁用超级管理员角色和普通管理员角色的修改按钮  
                        	 result += '<button disabled href="'+editUrlPath+'" data-target="#commonSmWin" data-toggle="modal"  type="button" class="editBtn btn-default deleteButton"><i class="fa fa-ban"></i>修改</button>&nbsp;';
                        }else{
                        	 result += '<button href="'+editUrlPath+'" data-target="#commonSmWin" data-toggle="modal"  type="button" class="editBtn editBtn-info"><i class="fa fa-pencil"></i>修改</button>&nbsp;';
                        }
                        if (data.delFlag == false) { //即刻体验角色不允许删除
                        	//删除按钮
                            result += '<button disabled type="button" class="editBtn btn-default deleteButton"><i class="fa fa-ban"></i>删除</button>&nbsp;';
                        } else {
                        	//删除按钮
                            result += '<button type="button" onclick="roleList.deleteRole(\''+idStr+'\')" class="deleteButton editBtn disableClick"><i class="fa fa-trash-o"></i>删除</button>';
                        }
                        return result;
                    }
                }, {
                    "data" : "name",
                    "class" : "text-center"
                },  {
                    "data" : "notes",
                    "class" : "text-center"
                }, {
                    "data" : null,
                    "class" : "text-center", //最后一列，操作按钮
                    render : function(data, type, row, meta) {
                        var idStr = row.idstr;
                        return "<a onclick='roleList.showPermission(\"" + idStr
                        + "\")'>预览</a>";
                    }
                }
            ];
            //ajax参数
            var ajaxDataParamFun = function(d) {
                d.simpleQueryParam = $('#simpleQueryParam').val(); //模糊查询
            };
            //表格setting
            var setting = {
                suffix  : '/',
                listUrl : 'role/list/',
                editUrl : 'role/edit/',
                deleteUrl : 'role/delete_/',
                deletemoreUrl : 'role/deletemore',
                enableUrl : 'user/enable_',
                disableUrl : 'user/disable_',
                columnDefs : columnDefs, //表格列定义
                columns : columns, //表格列
                dataTableDiv : 'dataTable', //表格
                ajaxDataParamFun : ajaxDataParamFun, //ajax参数
                pageable : true, //是否分页
                showIndexColumn : true, //是否显示第一列的索引列
                enabledChange : true
            };
            myTable = new TG_Tabel.createNew(setting);
            myTable.init();
            //操作权限 
            setResource = {
                async: {
                    type: "post",
                    enable: true,
                    autoParam: ["id"],
                    dataType: "json",
                    // data:{'csrfmiddlewaretoken': '{{ csrf_token }}'},
                },
                check: {
                    enable: true,
                    chkStyle: "checkbox",
                    chkboxType: {
                        "Y": "s",
                        "N": "s"
                    },
                    radioType: "all"
                },
                view: {
                    dblClickExpand: false
                },
                data: {
                    simpleData: {
                        enable: true
                    }
                },
                callback: {
                    beforeClick: roleList.beforeClickResource,
                    onCheck: roleList.onCheckResource
                }
            }
        },
        // 删除角色
        deleteRole: function(id){
            if (id == "ROLE_ADMIN" || id == "POWER_USER") {
                layer.msg(roleNoDelete,{move:false});
            }else{
                myTable.deleteItem(id);
            }
        },
        subChk: function(){
            $("#checkAll").prop("checked",$subChk.length == $subChk.filter(":checked").length ? true: false);
        },
        //批量删除
        deleteMuch: function(){
            //判断是否至少选择一项
            var chechedNum = $("input[name='subChk']:checked").length;
            if (chechedNum == 0) {
                layer.msg(selectItem,{move:false});
                return;
            }
            var checkedList = new Array();
            var flag = true;
            $("input[name='subChk']:checked").each(function() {
                if ($(this).val() == "ROLE_ADMIN" || $(this).val() == "POWER_USER") {
                    flag = false;
                    return false;
                }else{
                    checkedList.push($(this).val());
                }
            });
            if (flag) {
                myTable.deleteItems({
                    'deltems' : checkedList.join(";")
                });
            }else{
                layer.msg(roleNoDelete,{move:false});
            }
        },
        //点击预览 
        showPermission: function(id){
            $('#showPermissionDiv').modal('show');
            var url="role/choicePermissionTree/";
            var parameter={ "roleId": id};
            json_ajax("POST",url,"json",true,parameter, roleList.showPermissionCallback);
        },
        //返回方法 
        showPermissionCallback: function(data){
            for(var i = 0; i < data.length; i++){
                data[i].chkDisabled = true;     
            }; 
            $.fn.zTree.init($("#resourceDemo"), setResource, data);
            $.fn.zTree.getZTreeObj("resourceDemo").expandAll(false);
        },
        beforeClickResource: function(treeId, treeNode){
            var zTree = $.fn.zTree.getZTreeObj("resourceDemo");
            zTree.checkNode(treeNode, !treeNode.checked, null, true);
            return false;
        },
        onCheckResource: function(e, treeId, treeNode){
            var zTree = $.fn.zTree.getZTreeObj("resourceDemo"), nodes = zTree
                .getCheckedNodes(true), v = "";
            for (var i = 0, l = nodes.length; i < l; i++) {
                v += nodes[i].name + ",";
            }
        },
        //刷新列表
        refreshTable:function(){
        	$("#simpleQueryParam").val("");
            myTable.requestData();
        }
    }
    $(function(){
        roleList.init();
        $('input').inputClear();
        //全选
        $("#checkAll").click(function() {
            $("input[name='subChk']").prop("checked", this.checked);
        });
        //单选
        $subChk.on("click",roleList.subChk);
        $("#del_model").on("click",roleList.deleteMuch);
        myTable.add('commonWin', 'permissionForm', null, null);
        $("#refreshTable").on("click",roleList.refreshTable);
    })
})($,window)

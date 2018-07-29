(function (window, $) {
    var submissionFlag = false;
    var serialnumber = $("#serialnumber").val();
    var deviceType = $("#deviceType").val();
    var serialnumberError = $("#serialnumber-error");
    var deviceFlag = false;
    addMeterManagement = {
        init: function () {
            var setting = {
                async: {
                    url: "/entm/user/oranizationtree/",
                    tyoe: "post",
                    enable: true,
                    autoParam: ["id"],
                    contentType: "application/json",
                    dataType: "json",
                    dataFilter: addMeterManagement.ajaxDataFilter
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
                    beforeClick: addMeterManagement.beforeClick,
                    onClick: addMeterManagement.onClick
                }
            };
            $.fn.zTree.init($("#ztreeDemo"), setting, null);
            // laydate.render({elem: '#installDate', theme: '#6dcff6'});
            // laydate.render({elem: '#procurementDate', theme: '#6dcff6'});
        },
        beforeClick: function (treeId, treeNode) {
            var check = (treeNode);
            return check;
        },
        onClick: function (e, treeId, treeNode) {
            var zTree = $.fn.zTree.getZTreeObj("ztreeDemo"), nodes = zTree
                .getSelectedNodes(), v = "";
            n = "";
            nodes.sort(function compare(a, b) {
                return a.id - b.id;
            });
            for (var i = 0, l = nodes.length; i < l; i++) {
                n += nodes[i].name;
                v += nodes[i].uuid + ",";
            }
            if (v.length > 0)
                v = v.substring(0, v.length - 1);
            var cityObj = $("#zTreeOrganSel");
            cityObj.val(n);
            $("#groupId").val(v);
            $("#zTreeContent").hide();
        },
        //显示菜单
        showMenu: function () {
            if ($("#zTreeContent").is(":hidden")) {
                var inpwidth = $("#zTreeOrganSel").width();
                var spwidth = $("#zTreeOrganSelSpan").width();
                var allWidth = inpwidth + spwidth + 21;
                if (navigator.appName == "Microsoft Internet Explorer") {
                    $("#zTreeContent").css("width", (inpwidth + 7) + "px");
                } else {
                    $("#zTreeContent").css("width", allWidth + "px");
                }
                $(window).resize(function () {
                    var inpwidth = $("#zTreeOrganSel").width();
                    var spwidth = $("#zTreeOrganSelSpan").width();
                    var allWidth = inpwidth + spwidth + 21;
                    if (navigator.appName == "Microsoft Internet Explorer") {
                        $("#zTreeContent").css("width", (inpwidth + 7) + "px");
                    } else {
                        $("#zTreeContent").css("width", allWidth + "px");
                    }
                })
                $("#zTreeContent").show();
            } else {
                $("#zTreeContent").hide();
            }
            $("body").bind("mousedown", addMeterManagement.onBodyDown);
        },
        //隐藏菜单
        hideMenu: function () {
            $("#zTreeContent").fadeOut("fast");
            $("body").unbind("mousedown", addMeterManagement.onBodyDown);
        },
        onBodyDown: function (event) {
            if (!(event.target.id == "menuBtn" || event.target.id == "zTreeContent" || $(
                    event.target).parents("#zTreeContent").length > 0)) {
                addMeterManagement.hideMenu();
            }
        },
        //组织树预处理函数
        ajaxDataFilter: function (treeId, parentNode, responseData) {
            addMeterManagement.hideErrorMsg();//隐藏错误提示样式
            var isAdminStr = $("#isAdmin").attr("value");    // 是否是admin
            var isAdmin = isAdminStr == 'true';
            var userGroupId = $("#userGroupId").attr("value");  // 用户所属组织 id
            var userGroupName = $("#userGroupName").attr("value");  // 用户所属组织 name
            //如果根企业下没有节点,就显示错误提示(根企业下不能创建终端)
            if (responseData != null && responseData != "" && responseData != undefined && responseData.length >= 1) {
                if (!isAdmin) { // 不是admin，默认组织为当前组织
                    $("#groupId").val(userGroupId);
                    $("#zTreeOrganSel").val(userGroupName);
                } else { // admin，默认组织为树结构第一个组织
                    $("#groupId").val(responseData[0].uuid);
                    $("#zTreeOrganSel").attr("value", responseData[0].name);
                }
                return responseData;
            } else {
                addMeterManagement.showErrorMsg("您需要先新增一个组织", "zTreeOrganSel");
                return;
            }
        },
        doSubmit: function () {
            if (submissionFlag) {  // 防止重复提交
                return;
            } else {
                deviceType = $("#deviceType").val();
                serialnumber = $("#serialnumber").val();
                addMeterManagement.serialnumberValidates();
                if ($("#serialnumber").val() != "" && deviceFlag) {
                    if (addMeterManagement.validates()) {
                        submissionFlag = true;
                        $("#addForm").ajaxSubmit(function (data) {
                            var json = eval("(" + data + ")");
                            if (json.success) {
                                $("#commonWin").modal("hide");
                                myTable.requestData();
                            } else {
                                layer.msg(json.msg);
                            }
                        });
                    }
                }
            }
        },
        serialnumberValidates: function () {
        
            // var regName = /^(?=.*[0-9a-zA-Z])[0-9a-zA-Z]{1,20}$/;
            // if (serialnumber != "" && !regName.test(serialnumber)) {
            //     serialnumberError.html("请输入字母/数字，范围（车）7~15（人）1~20");
            //     serialnumberError.show();
            //     deviceFlag = false;
            // }
            // else 
            if (serialnumber == "") {
                serialnumberError.html("请输入终端号，范围：1~20");
                serialnumberError.show();
                deviceFlag = false;
            }
            else {
                addMeterManagement.deviceAjax();
            }
            
        },
        validates: function () {
            return $("#addForm").validate({
                rules: {
                    /*serialnumber: {
                        required: true,
                        checkDeviceNumber: "#deviceType",
                        isRightfulString: true,
                        remote: {
                            type: "post",
                            async: false,
                            url: "/devm/meter/repetition",
                            data: {
                                username: function () {
                                    return $("#serialnumber").val();
                                }
                            }
                        }
                    },*/
                    
                    belongto: {
                        required: true
                    },
                    simid: {
                        required: true,
                        maxlength: 50
                    },
                    mtype: {
                        required: true,
                        maxlength: 50
                    },
                    // isVideo: {
                    //     maxlength: 6
                    // },
                    protocol: {
                        maxlength: 64
                    },
                    check_cycle: {
                        maxlength: 11
                    },
                    dn: {
                        required: false,
                        maxlength: 6
                    },
                    // manuFacturer: {
                    //     maxlength: 100
                    // },
                    R: {
                        maxlength: 100
                    },
                    q3: {
                        required: false,
                        maxlength: 50
                    }
                },
                messages: {
                    /*serialnumber: {
                        required: serialnumberNull,
                        checkDeviceNumber: serialnumberError,
                        isRightfulString: serialnumberError,
                        remote: serialnumberExists
                    },*/
                    belongto: {
                        required: "所属组织不能为空",
                        maxlength: publicSize50
                    },
                    simid: {
                        required: publicNull
                    },
                    mtype: {
                        required: deviceTypeNull,
                        maxlength: publicSize50
                    },
                    protocol: {
                        required: publicNull,
                        maxlength: publicSize50
                    },
                    check_cycle: {
                        maxlength: publicSize6
                    },
                    dn: {
                        maxlength: publicSize64
                    },
                    R: {
                        maxlength: publicSize10
                    },
                    q3: {
                        required: publicNull,
                        maxlength: publicSize6
                    }
                },
                submitHandler: function (form) {
                    var typeVal = $("#deviceType").val();
                    var serialnumber = $("#serialnumber").val();
                    // if (typeVal == "5") {
                    //     $("#serialnumber-error").html("请输入终端号，范围：1~20");
                    //     var reg = /^(?=.*[0-9a-zA-Z])[0-9a-zA-Z-]{1,20}$/;
                    //     if (!reg.test(serialnumber)) {
                    //         alert("请输入终端号，范围：1~20");
                    //         return;
                    //     }
                    // }
                }
            }).form();
        },
        deviceTypeChange: function () {
            if ($("#deviceType").val() == 5) {
                $("#functionalType").find("option[value='" + 1 + "']").remove();
                $("#functionalType").find("option[value='" + 2 + "']").remove();
                $("#functionalType").find("option[value='" + 3 + "']").remove();
                $("#functionalType").find("option[value='" + 4 + "']").remove();
                $("#functionalType").find("option[value='" + 5 + "']").remove();
                $("#functionalType").append("<option value='4'>手咪设备</option>");
            } else {
                $("#functionalType").find("option[value='" + 1 + "']").remove();
                $("#functionalType").find("option[value='" + 2 + "']").remove();
                $("#functionalType").find("option[value='" + 3 + "']").remove();
                $("#functionalType").find("option[value='" + 4 + "']").remove();
                $("#functionalType").find("option[value='" + 5 + "']").remove();
                $("#functionalType").append("<option value='1'>简易型车机</option><option value='2'>行车记录仪</option><option value='3'>对讲设备</option><option  value='5'>超长待机设备</option>");
            }
        },
        showErrorMsg: function (msg, inputId) {
            if ($("#error_label_add").is(":hidden")) {
                $("#error_label_add").text(msg);
                $("#error_label_add").insertAfter($("#" + inputId));
                $("#error_label_add").show();
            } else {
                $("#error_label_add").is(":hidden");
            }
        },
        //错误提示信息隐藏
        hideErrorMsg: function () {
            $("#error_label_add").is(":hidden");
            $("#error_label_add").hide();
        },
        deviceAjax: function () {
            $.ajax({
                    type: "post",
                    url: "/devm/meter/repetition/",
                    data: {serialnumber: serialnumber},
                    success: function (d) {
                        var result = $.parseJSON(d);
                        if (!result) {
                            serialnumberError.html("表具编号已存在！");
                            serialnumberError.show();
                            deviceFlag = false;
                        }
                        else {
                            serialnumberError.hide();
                            deviceFlag = true;
                        }
                    }
                }
            )
        }
    }
    $(function () {
        $('input').inputClear();
        //初始化
        addMeterManagement.init();
        $('input').inputClear();

        // $("#deviceType").on("change", function () {
        //     deviceType = $(this).val();
        //     serialnumber = $("#serialnumber").val();
        //     addMeterManagement.serialnumberValidates();
        // })
        $("#serialnumber").bind("input propertychange change", function (event) {
            // deviceType = $("#deviceType").val();
            serialnumber = $(this).val();
            $.ajax({
                    type: "post",
                    url: "/devm/meter/repetition/",
                    data: {serialnumber: serialnumber},
                    success: function (d) {
                        var result = $.parseJSON(d);
                        if (!result) {
                            serialnumberError.html("表具编号已存在！");
                            serialnumberError.show();
                            deviceFlag = false;
                        }
                        else {
                            addMeterManagement.serialnumberValidates();
                        }
                    }
                }
            )
        });

        //显示菜单
        $("#zTreeOrganSel").bind("click", addMeterManagement.showMenu);
        //提交
        $("#doSubmit").bind("click", addMeterManagement.doSubmit);
    })
})(window, $)

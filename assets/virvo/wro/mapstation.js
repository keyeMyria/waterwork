(function($,window){
    var selectTreeId = '';
    var selectDistrictId = '';
    var zNodes = null;
    var log, className = "dark";
    var newCount = 1;
    var columnDefs;
    var columns;
    var setting;
    var treeSetting;
    var idStr;
    var OperationId;
    var selectTreeIdAdd="";
    var startOperation;// 点击运营资质类别的修改按钮时，弹出界面时运营资质类别文本的内容
    var expliant;// 点击运营资质类别的修改按钮时，弹出界面时说明文本的内容
    var vagueSearchlast = $("#userType").val();
    var overlay;
    var getdmamapusedata_flag = 0;
    var markerInfoWindow = null;
    var markerList = [];

    mapStation = {
        init: function(){
            // map
            var layer = new AMap.TileLayer({
                  zooms:[3,20],    //可见级别
                  visible:true,    //是否可见
                  opacity:1,       //透明度
                  zIndex:0         //叠加层级
            });
            

            map = new AMap.Map('map-container',{
                zoom: 15,  //设置地图显示的缩放级别
                center: [118.438781,29.871515],
                layers:[layer], //当只想显示标准图层时layers属性可缺省
                viewMode: '2D',  //设置地图模式
                lang:'zh_cn',  //设置地图语言类型
            });

            
            
            
            
            
        },
        //构建自定义信息窗体
        createInfoWindow:function (title, content) {
            var info = document.createElement("div");
            info.className = "info";
     
            //可以通过下面的方式修改自定义窗体的宽高
            //info.style.width = "400px";
            // 定义顶部标题
            var top = document.createElement("div");
            var titleD = document.createElement("div");
            var closeX = document.createElement("img");
            top.className = "info-top";
            titleD.innerHTML = title;
            closeX.src = "http://webapi.amap.com/images/close2.gif";
            closeX.onclick = mapStation.closeInfoWindow();
     
            top.appendChild(titleD);
            top.appendChild(closeX);
            info.appendChild(top);
     
            // 定义中部内容
            var middle = document.createElement("div");
            middle.className = "info-middle";
            middle.style.backgroundColor = 'white';
            middle.innerHTML = content;
            info.appendChild(middle);
     
            // 定义底部内容
            var bottom = document.createElement("div");
            bottom.className = "info-bottom";
            bottom.style.position = 'relative';
            bottom.style.top = '0px';
            bottom.style.margin = '0 auto';
            var sharp = document.createElement("img");
            sharp.src = "http://webapi.amap.com/images/sharp.png";
            bottom.appendChild(sharp);
            info.appendChild(bottom);
            return info;
        },
        infoWindow:function(){
            // overlay = document.getElementById('js-overlay');
            markerInfoWindow = new AMap.InfoWindow({
                isCustom: true,  //使用自定义窗体
                // content: mapStation.createInfoWindow("title", overlay.innerHTML),
                // size:new AMap.Size(400,300),
                offset: new AMap.Pixel(16, -45),
                autoMove: true
            });
            return markerInfoWindow;
        },
        createMarker:function(station){
            var position = new AMap.LngLat(station.lng,station.lat);
            var marker = new AMap.Marker({
                position: position,   // 经纬度对象，也可以是经纬度构成的一维数组[116.39, 39.9]
                title: station.stationname
            });
            infow = mapStation.infoWindow();
            marker.on("mouseover",function(e){
                
                // var position = e.lnglat;
                // console.log(position);
                conts = mapStation.createStationInfo(station.stationname, station)

                infow.setContent(conts);
                // markerInfoWindow.setSize(AMap.Size(400,300));
                infow.open(map,position);
            });

            marker.on("mouseout",function(){
                infow.close();
            })

            return marker;
        },
        createStationInfo:function (title, content) {
            var info = document.createElement("div");
            info.className = "info";
     
            //可以通过下面的方式修改自定义窗体的宽高
            //info.style.width = "400px";
            // 定义顶部标题
            var stationname = document.createElement("div");
            stationname.innerHTML = "站点名称:" ;
            var span = document.createElement("span");
            span.className = "span2";
            span.innerHTML = content.stationname;
            stationname.appendChild(span);
            info.appendChild(stationname);
            
            var belongto = document.createElement("div");
            belongto.innerHTML = "所属组织:";
            var span = document.createElement("span");
            span.className = "span1";
            span.innerHTML = content.belongto;
            belongto.appendChild(span);
            info.appendChild(belongto);
            
            var relatemeter = document.createElement("div");
            relatemeter.innerHTML = "关联表具:";
            var span = document.createElement("span");
            span.className = "span1";
            span.innerHTML = content.serialnumber;
            relatemeter.appendChild(span);
            info.appendChild(relatemeter);
            
            var metertype = document.createElement("div");
            metertype.innerHTML = "表具类型:";
            var span = document.createElement("span");
            span.className = "span1";
            span.innerHTML = content.metertype;
            metertype.appendChild(span);
            info.appendChild(metertype);
            
            var meterdn = document.createElement("div");
            meterdn.innerHTML = "表具口径:";
            var span = document.createElement("span");
            span.className = "span1";
            span.innerHTML = content.dn;
            meterdn.appendChild(span);
            info.appendChild(meterdn);
            
            var meterstate = document.createElement("div");
            meterstate.innerHTML = "状&nbsp; &nbsp; &nbsp; 态:";
            var span = document.createElement("span");
            if(content.status == "在线"){
                span.className = "span3";
            }else{
                span.className = "span4";
            }
            span.innerHTML = content.status;
            meterstate.appendChild(span);
            info.appendChild(meterstate);
            
            var split = document.createElement("img");
            split.src = "/static/virvo/images/u3922.png";
            info.appendChild(split);

            var readtime = document.createElement("div");
            readtime.innerHTML = "采集时间:";
            var span = document.createElement("span");
            span.className = "span1";
            span.innerHTML = content.readtime;
            readtime.appendChild(span);
            info.appendChild(readtime);
            
            var flux = document.createElement("div");
            flux.innerHTML = "瞬时流量:";
            var span = document.createElement("span");
            span.className = "span1";
            span.innerHTML = content.flux;
            flux.appendChild(span);
            info.appendChild(flux);
            
            var accumuflux = document.createElement("div");
            accumuflux.innerHTML = "累积流量:";
            var span = document.createElement("span");
            span.className = "span1";
            span.innerHTML = content.totalflux;
            accumuflux.appendChild(span);
            info.appendChild(accumuflux);
            
            var press = document.createElement("div");
            press.innerHTML = "管网压力:";
            var span = document.createElement("span");
            span.className = "span1";
            span.innerHTML = content.press;
            press.appendChild(span);
            info.appendChild(press);
            
            var signlen = document.createElement("div");
            signlen.innerHTML = "信号强度:";
            var span = document.createElement("span");
            span.className = "span1";
            span.innerHTML = content.signal;
            signlen.appendChild(span);
            info.appendChild(signlen);
            
            
            // 定义底部内容
            var bottom = document.createElement("div");
            bottom.className = "info-bottom";
            bottom.style.position = 'relative';
            bottom.style.top = '10px';
            bottom.style.margin = '0 auto';
            var sharp = document.createElement("img");
            sharp.src = "http://webapi.amap.com/images/sharp.png";
            bottom.appendChild(sharp);
            info.appendChild(bottom);
            return info;
        },
        //关闭信息窗体
        closeInfoWindow:function () {
            map.clearInfoWindow();
        },
        
        userTree : function(){
            // 初始化文件树
            treeSetting = {
                async : {
                    url : "/dmam/district/dmatree/",
                    type : "post",
                    enable : true,
                    autoParam : [ "id" ],
                    dataType : "json",
                    data:{'csrfmiddlewaretoken': '{{ csrf_token }}'},
                    otherParam : {  // 是否可选 Organization
                        "isOrg" : "1",
                        // "csrfmiddlewaretoken": "{{ csrf_token }}"
                    },
                    dataFilter: mapStation.ajaxDataFilter
                },
                view : {
                    // addHoverDom : mapStation.addHoverDom,
                    // removeHoverDom : mapStation.removeHoverDom,
                    selectedMulti : false,
                    nameIsHTML: true,
                    // fontCss: setFontCss_ztree
                },
                edit : {
                    enable : true,
                    editNameSelectAll : true,
                    showRemoveBtn : false,//mapStation.showRemoveBtn,
                    showRenameBtn : false
                },
                data : {
                    simpleData : {
                        enable : true
                    }
                },
                callback : {
                    onClick : mapStation.zTreeOnClick
                }
            };
            $.fn.zTree.init($("#treeDemo"), treeSetting, zNodes);
            var treeObj = $.fn.zTree.getZTreeObj('treeDemo');treeObj.expandAll(true);
           
        },
        // 组织树预处理函数
        ajaxDataFilter: function(treeId, parentNode, responseData){
            var treeObj = $.fn.zTree.getZTreeObj("treeDemo");
            if (responseData) {
                for (var i = 0; i < responseData.length; i++) {
                        responseData[i].open = true;
                }
            }
            return responseData;
        },
        showLog: function(str){
            if (!log)
                log = $("#log");
                log.append("<li class='"+className+"'>" + str + "</li>");
            if (log.children("li").length > 8) {
                log.get(0).removeChild(log.children("li")[0]);
            }
        },
        selectAll: function(){
            var zTree = $.fn.zTree.getZTreeObj("treeDemo");
            zTree.treeSetting.edit.editNameSelectAll = $("#selectAll").attr("checked");
        },
        //点击节点
        zTreeOnClick: function(event, treeId, treeNode){
            selectTreeId = treeNode.id;
            selectDistrictId = treeNode.districtid;
            selectTreeIdAdd=treeNode.uuid;
            $('#simpleQueryParam').val("");
            mapStation.requireStation();
        },
        requireStation:function(){
            var data={"groupName":selectTreeId};
            var url="/monitor/getmapstationlist/";
            json_ajax("POST", url, "json", true,data,mapStation.buildstationinfo);
        },
        buildstationinfo:function(data){
            console.log(data);
            var stationinfo ;
            // for(var i = 0;i<markerList.length;i++){
            //     marker = markerList[i];
            //     console.log(marker);
            //     map.remove(marker)
            // }
            map.remove(markerList)
            markerList = [];
            if (data.obj != null && data.obj != ""){
                stationinfo = data.obj;
                
                for (var i = 0; i < stationinfo.length; i++){
                    station = stationinfo[i];
                    
                    if(station.lng == null)
                        continue;
                    marker = mapStation.createMarker(station);
                    markerList.push(marker);
                }

                
                map.add(markerList);

            }
            if(data.success == true){
                
            }
            
        },
        // ajax参数
        ajaxDataParamFun: function(d){
            d.simpleQueryParam = $('#simpleQueryParam').val(); // 模糊查询
            d.groupName = selectTreeId;
            d.districtId = selectDistrictId;
        },
        findDownKey:function(event){
            if(event.keyCode==13){
                mapStation.findOperation();
            }
        }
    }
    $(function(){
        $('input').inputClear().on('onClearEvent',function(e,data){
            var id = data.id;
            if(id == 'search_condition'){
                search_ztree('treeDemo',id,'group');
            };
        });
        var map;
        mapStation.userTree();
        
        mapStation.init();
        
        mapStation.requireStation();
        // map.on(['pointermove', 'singleclick'], mapStation.moveonmapevent);
        
    })
})($,window)

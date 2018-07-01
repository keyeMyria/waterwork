# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import get_object_or_404,render,redirect
from django.http import HttpResponse,JsonResponse,HttpResponseRedirect,StreamingHttpResponse
from django.contrib import messages
from django.template import TemplateDoesNotExist
import json
import random
from datetime import datetime

from mptt.utils import get_cached_trees
from mptt.templatetags.mptt_tags import cache_tree_children
from django.contrib.auth.mixins import PermissionRequiredMixin,UserPassesTestMixin
from django.template.loader import render_to_string
from django.shortcuts import render,HttpResponse
from django.views import View
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView,DeleteView,FormView
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import admin
from django.contrib.auth.models import Permission
from django.utils.safestring import mark_safe
from django.utils.encoding import escape_uri_path
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from collections import OrderedDict
from accounts.models import User,MyRoles
from accounts.forms import RoleCreateForm,MyRolesForm,RegisterForm,UserDetailChangeForm

from .utils import unique_cid_generator,unique_uuid_generator,unique_rid_generator
from .forms import OrganizationsAddForm,OrganizationsEditForm
from . models import Organizations
import os
from django.conf import settings
from .resources import UserResource,minimalist_xldate_as_datetime
from tablib import Dataset
# from django.core.urlresolvers import reverse_lazy



def error_404(request):
    return render(request,"404.html",{})

def error_500(request):
    return render(request,"500.html",{})

def i18n_javascript(request):
    return admin.site.i18n_javascript(request)


class StaticView(TemplateView):
    def get(self, request, page, *args, **kwargs):
        self.template_name = page
        print(page)
        response = super(StaticView, self).get(request, *args, **kwargs)
        try:
            return response.render()
        except TemplateDoesNotExist:
            raise Http404()


def room(request, room_name):
    return render(request, "entm/room.html", {
        "room_name_json": mark_safe(json.dumps(room_name))
    })

class AjaxableResponseMixin(object):
    """
    Mixin to add AJAX support to a form.
    Must be used with an object-based FormView (e.g. CreateView)
    """
    def form_invalid(self, form):
        response = super(AjaxableResponseMixin,self).form_invalid(form)
        # print("dasf:",form.cleaned_data.get("register_date"))
        err_str = ""
        for k,v in form.errors.items():
            print(k,v)
            err_str += v[0]
        if self.request.is_ajax():
            data = {
                "success": 0,
                "obj":{
                    "flag":0,
                    "errMsg":err_str
                    }
            }
            print(form.errors)
            return HttpResponse(json.dumps(data)) #JsonResponse(data)
            # return JsonResponse(form.errors, status=400)
        else:
            return response

    def form_valid(self, form):
        # We make sure to call the parent"s form_valid() method because
        # it might do some processing (in the case of CreateView, it will
        # call form.save() for example).
        response = super(AjaxableResponseMixin,self).form_valid(form)
        if self.request.is_ajax():
            data = {
                "success": 1,
                "obj":{"flag":1}
            }
            return HttpResponse(json.dumps(data)) #JsonResponse(data)
        else:
            return response



def recursive_node_to_dict(node,url_cat):
    result = {
        'id':node.pk,
        'name': node.name,
        'open':'true',
        'url':'/dma/{}/{}'.format(node.pk,url_cat),
        'target':'_self',
        'icon':"/static/virvo/images/站点管理/u842_1.png",
        'class':"J_menuItem",
    }
    
    children = [recursive_node_to_dict(c,url_cat) for c in node.get_children()]
    
    # get each node's station if exist
    if url_cat != '':
        try:
            sats = node.station.all()
            for s in sats:
                children.append({
                    'name':s.station_name,
                    'url':'/dma/{}/{}/{}'.format(node.pk,url_cat,s.id),
                    'target':'_self',
                    'icon':"/static/virvo/images/u3672.png",
                    # 'class':"J_menuItem",
                })
            # children.append({'name':})
        except:
            pass

    if children:
        result['children'] = children
    
    return result

def gettree(request):
    page_name = request.GET.get('page_name') or ''
    print(page_name)
    organs = Organization.objects.all()
    
    top_nodes = get_cached_trees(organs)

    dicts = []
    for n in top_nodes:
        dicts.append(recursive_node_to_dict(n,page_name))

    
    # print json.dumps(dicts, indent=4)

    virvo_tree = [{'name':'威尔沃','open':'true','children':dicts}]
    return JsonResponse({'trees':virvo_tree})                


choicetreedict=OrderedDict()
choicetreedict["datamonitor"]={
        "name":"数据监控",
        "submenu":[{
            "mapmonitor":{"name":"地图监控","sub":{"name":"可写"}},
            "realcurlv":{"name":"实时曲线","sub":{"name":"可写"}},
            "realdata":{"name":"实时数据","sub":{"name":"可写"}},
            "dmaonline":{"name":"DMA在线监控","sub":{"name":"可写"}},
        }],
    }
choicetreedict["firmmanager"] = {
        "name":"企业管理",
        "submenu":[{
            "rolemanager":{"name":"角色管理","sub":{"name":"可写"}},
            "organusermanager":{"name":"组织和用户管理","sub":{"name":"可写"}},
        }],
    }
choicetreedict["devicemanager"] = {
        "name":"设备管理",
        "submenu":[{
            "meters":{"name":"表具管理","sub":{"name":"可写"}},
            "simcard":{"name":"SIM卡管理","sub":{"name":"可写"}},
            "params":{"name":"参数指令","sub":{"name":"可写"}},
        }],
    }

choicetreedict["datanalys"] = {
        "name":"数据分析",
        "submenu":[{
            "dailyuse":{"name":"日用水分析","sub":{"name":"可写"}},
            "monthlyuse":{"name":"月用水分析","sub":{"name":"可写"}},
            "dmacxc":{"name":"DMA产销差分析","sub":{"name":"可写"}},
            "flownalys":{"name":"流量分析","sub":{"name":"可写"}},
            "comparenalys":{"name":"对比分析","sub":{"name":"可写"}},
            "peibiao":{"name":"配表分析","sub":{"name":"可写"}},
            "rawdata":{"name":"原始数据","sub":{"name":"可写"}},
            "mnf":{"name":"夜间最小流量","sub":{"name":"可写"}},
        }],
    }
choicetreedict["alarmcenter"] = {
        "name":"报警中心",
        "submenu":[{
            "stationalarm":{"name":"站点报警设置","sub":{"name":"可写"}},
            "dmaalarm":{"name":"DMA报警设置","sub":{"name":"可写"}},
            "queryalarm":{"name":"报警查询","sub":{"name":"可写"}},
        }],
    }
choicetreedict["basemanager"] = {
        "name":"基础管理",
        "submenu":[{
            "dmamanager":{"name":"dma管理","sub":{"name":"可写"}},
            "stationmanager":{"name":"站点管理","sub":{"name":"可写"}},
        }],
    }

choicetreedict["basenalys"] = {
        "name":"基准分析",
        "submenu":[{
            "dma":{"name":"DMA基准分析","sub":{"name":"可写"}},
            "mf":{"name":"最小流量分析","sub":{"name":"可写"}},
            "day":{"name":"日基准流量分析","sub":{"name":"可写"}},
        }],
    }
choicetreedict["systemconfig"] = {
        "name":"系统管理",
        "submenu":[{
            "personality":{"name":"平台个性化管理","sub":{"name":"可写"}},
            "system":{"name":"系统设置","sub":{"name":"可写"}},
            "retransit":{"name":"转发设置","sub":{"name":"可写"}},
            "icons":{"name":"图标配置","sub":{"name":"可写"}},
            "querylog":{"name":"日志查询","sub":{"name":"可写"}},
        }],
    }
choicetreedict["reporttable"] = {
        "name":"报表统计",
        "submenu":[{
            "querylog":{"name":"日志查询","sub":{"name":"可写"}},
            "alarm":{"name":"报警报表","sub":{"name":"可写"}},
            "dmastatics":{"name":"DMA统计报表","sub":{"name":"可写"}},
            "biguser":{"name":"大用户报表","sub":{"name":"可写"}},
            "flows":{"name":"流量报表","sub":{"name":"可写"}},
            "waters":{"name":"水量报表","sub":{"name":"可写"}},
            "biaowu":{"name":"表务报表","sub":{"name":"可写"}},
            "bigdata":{"name":"大数据报表","sub":{"name":"可写"}},
        }],
    }

def buildbasetree():
    ctree = []
    

    for key in choicetreedict.keys():
        pname = choicetreedict[key]["name"]
        pid = key
        

        tmp1 = {}
        tmp1["name"] = pname
        tmp1["pId"] = 0
        tmp1["id"] = pid
        tmp1["checked"] = "true"
        
        ctree.append(tmp1)
        
        submenu = choicetreedict[key]["submenu"][0]
        for sub_key in submenu.keys():
            name = submenu[sub_key]["name"]
            idstr = "{id}_{pid}".format(id=sub_key,pid=pid)
            cid = pid

            tmp2 = {}
            tmp2["name"] = name
            tmp2["pId"] = cid
            tmp2["id"] = idstr
            tmp2["checked"] = "true"
            
            ctree.append(tmp2)

        
            
            #可写
            edit_id = "{pid}_edit".format(pid=idstr)
            tmp3 = {}
            tmp3["name"] = "可写"
            tmp3["pId"] = idstr
            tmp3["id"] = edit_id
            tmp3["type"] = "premissionEdit"
            tmp3["checked"] = "true"
            
            ctree.append(tmp3)

            

    return ctree    


def buildchoicetree(request,permstree=None):
    ctree = []
    # print("buildtree permm:",permstree,type(permstree))
    user = request.user
    pt_dict = {}
    for pt in permstree:
        # print(pt["id"],pt["edit"])
        pt_dict[pt["id"]] = pt["edit"]


    for key in choicetreedict.keys():
        pname = choicetreedict[key]["name"]
        pid = key
        

        tmp1 = {}
        tmp1["name"] = pname
        tmp1["pId"] = 0
        tmp1["id"] = pid
        if key in pt_dict.keys():
            tmp1["checked"] = "true"
        else:
            if not user.has_menu_permission(pid):
                tmp1["chkDisabled"] = "true" 
        ctree.append(tmp1)
        
        submenu = choicetreedict[key]["submenu"][0]
        for sub_key in submenu.keys():
            name = submenu[sub_key]["name"]
            idstr = "{id}_{pid}".format(id=sub_key,pid=pid)
            cid = pid

            tmp2 = {}
            tmp2["name"] = name
            tmp2["pId"] = cid
            tmp2["id"] = idstr
            if idstr in pt_dict.keys():
                tmp2["checked"] = "true"
            else:
                if not user.has_menu_permission(idstr):
                    tmp2["chkDisabled"] = "true" 
            ctree.append(tmp2)

        
            
            #可写
            edit_id = "{pid}_edit".format(pid=idstr)
            tmp3 = {}
            tmp3["name"] = "可写"
            tmp3["pId"] = idstr
            tmp3["id"] = edit_id
            tmp3["type"] = "premissionEdit"
            if idstr in pt_dict.keys() and pt_dict[idstr] == True:
                tmp3["checked"] = "true"
            else:
                if not user.has_menu_permission_edit(idstr):
                    tmp3["chkDisabled"] = "true" 
            ctree.append(tmp3)

            

    return ctree



def choicePermissionTree(request):

    
    rid = request.POST.get("roleId") or ''
    print(" get choicePermissionTree",rid)

    
    # print('buildtree:',buildtree)

    if len(rid) <= 0:
        user = request.user
        if user.is_admin:
            return HttpResponse(json.dumps(buildbasetree()))
        permissiontree = user.Role.permissionTree

    else:
        instance = MyRoles.objects.get(rid=rid)
        permissiontree = instance.permissionTree


    if len(permissiontree) > 0:
        ptree = json.loads(permissiontree)
        buildtree = buildchoicetree(request,ptree)
            


    # return JsonResponse(dicts,safe=False)

    return HttpResponse(json.dumps(buildtree))

def oranizationtree(request):   
    organtree = []

    user = request.user
    organs = user.belongto #Organizations.objects.all()
    
    for o in organs.get_descendants(include_self=True):
        organtree.append({
            "name":o.name,
            "id":o.cid,
            "pId":o.pId,
            "type":"group",
            "uuid":o.uuid
        })

    
    result = dict()
    result["data"] = organtree
    
    # print(json.dumps(result))
    
    return HttpResponse(json.dumps(organtree))

    # return JsonResponse(organtree,safe=False)


def userlist(request):
    # print("userlist",request.POST)
    draw = 1
    length = 0
    start=0
    print('userlist:',request.user)
    if request.method == "GET":
        draw = int(request.GET.get("draw", 1))
        length = int(request.GET.get("length", 10))
        start = int(request.GET.get("start", 0))
        search_value = request.GET.get("search[value]", None)
        # order_column = request.GET.get("order[0][column]", None)[0]
        # order = request.GET.get("order[0][dir]", None)[0]
        groupName = request.GET.get("groupName")
        simpleQueryParam = request.POST.get("simpleQueryParam")
        # print("simpleQueryParam",simpleQueryParam)

    if request.method == "POST":
        draw = int(request.POST.get("draw", 1))
        length = int(request.POST.get("length", 10))
        start = int(request.POST.get("start", 0))
        pageSize = int(request.POST.get("pageSize", 10))
        search_value = request.POST.get("search[value]", None)
        # order_column = request.POST.get("order[0][column]", None)[0]
        # order = request.POST.get("order[0][dir]", None)[0]
        groupName = request.POST.get("groupName")
        simpleQueryParam = request.POST.get("simpleQueryParam")
        # print(request.POST.get("draw"))
        # print("groupName",groupName)
        # print("post simpleQueryParam",simpleQueryParam)

    print("get userlist:",draw,length,start,search_value)

    def u_info(u):
        rolename = u.Role.name if u.Role else ''
        groupname = u.belongto.name if u.belongto else ''
        return {
            "id":u.pk,
            "user_name":u.user_name,
            "real_name":u.real_name,
            "sex":u.sex,
            "phone_number":u.phone_number,
            "expire_date":u.expire_date,
            "groupName":groupname,
            "roleName":rolename,
            "email":u.email,
            "is_active":'1' if u.is_active else '0'
        }
    data = []
    #当前登录用户
    current_user = request.user
    
    userl = current_user.user_list()
    recordsTotal = len(userl)
    
    print("user all:",userl)
    if groupName != "":
        #查询的组织
        query_org = Organizations.objects.get(cid=groupName)
        userl = [u for u in userl if u.belongto == query_org]
        # print("query organ user,",userl)

    
    
    def search_user(u):
        if simpleQueryParam in u.user_name or simpleQueryParam in u.real_name or simpleQueryParam in u.email or simpleQueryParam in u.phone_number :
            return True


    if simpleQueryParam != "":
        print('simpleQueryParam:',simpleQueryParam)
        # userl = userl.filter(real_name__icontains=simpleQueryParam)
        userl = [u for u in userl if search_user(u) is True]
    
    for u in userl[start:start+length]:
        data.append(u_info(u))
    
    # recordsTotal = len(data)
    
    result = dict()
    result["records"] = data
    result["draw"] = draw
    result["success"] = "true"
    result["pageSize"] = pageSize
    result["totalPages"] = recordsTotal/pageSize
    result["recordsTotal"] = recordsTotal
    result["recordsFiltered"] = recordsTotal
    result["start"] = 0
    result["end"] = 0

    print(draw,pageSize,recordsTotal/pageSize,recordsTotal)
    
    return HttpResponse(json.dumps(result))
    # return JsonResponse([result],safe=False)


        

def rolelist(request):
    print('get rolelist:',request)
    draw = 1
    length = 0
    start=0
    if request.method == "GET":
        draw = int(request.GET.get("draw", 1))
        length = int(request.GET.get("length", 10))
        start = int(request.GET.get("start", 0))
        search_value = request.GET.get("search[value]", None)
        simpleQueryParam = request.POST.get("simpleQueryParam")
        # order_column = request.GET.get("order[0][column]", None)[0]
        # order = request.GET.get("order[0][dir]", None)[0]

    if request.method == "POST":
        draw = int(request.POST.get("draw", 1))
        length = int(request.POST.get("length", 10))
        start = int(request.POST.get("start", 0))
        pageSize = int(request.POST.get("pageSize", 10))
        search_value = request.POST.get("search[value]", None)
        simpleQueryParam = request.POST.get("simpleQueryParam")
        # order_column = request.POST.get("order[0][column]", None)[0]
        # order = request.POST.get("order[0][dir]", None)[0]

    # print("get rolelist:",draw,length,start,search_value)
    current_user = request.user
    

    data = []
    rolel = current_user.role_list()
    recordsTotal = len(rolel)

    def search_role(r):
        if simpleQueryParam in r.name:
            return True


    if simpleQueryParam != "":
        print('simpleQueryParam:',simpleQueryParam)
        # userl = userl.filter(real_name__icontains=simpleQueryParam)
        rolel = [r for r in rolel if search_role(r) is True]

    for r in rolel[start:start+length]:
        data.append({"idstr":r.rid,"name":r.name,"notes":r.notes})

    
    # recordsTotal = len(data) #rolel.count()

    result = dict()
    result["records"] = data
    result["draw"] = draw
    result["success"] = "true"
    result["pageSize"] = pageSize
    result["totalPages"] = recordsTotal/pageSize
    result["recordsTotal"] = recordsTotal
    result["recordsFiltered"] = recordsTotal
    result["start"] = 0
    result["end"] = 0
    
    return HttpResponse(json.dumps(result))
    # return JsonResponse([result],safe=False)


def findOperations(request):

    operarions_list = {
        # "exceptionDetailMsg":"",
        # "msg":"",
        "obj":{
                "operation":[
                {"explains":"自来水公司","id":"waterworks","operationType":"自来水公司"},
                {"explains":"非自来水公司","id":"nonwaterworks","operationType":"非自来水公司"},
                
            ]
        },
        "success":True
    }
   

    return JsonResponse(operarions_list)
    

"""
group add
"""
class UserGroupAddView(AjaxableResponseMixin,UserPassesTestMixin,CreateView):
    model = Organizations
    template_name = "entm/groupadd.html"
    form_class = OrganizationsAddForm
    success_url = reverse_lazy("entm:usermanager");

    # @method_decorator(permission_required("dma.change_stations"))
    def dispatch(self, *args, **kwargs):
        # print("dispatch",args,kwargs)
        if self.request.method == "GET":
            cid = self.request.GET.get("id")
            pid = self.request.GET.get("pid")
            kwargs["cid"] = cid
            kwargs["pId"] = pid
        return super(UserGroupAddView, self).dispatch(*args, **kwargs)

    def test_func(self):
        if self.request.user.has_menu_permission_edit('organusermanager_firmmanager'):
            return True
        return False

    def handle_no_permission(self):
        data = {
                "mheader": "修改用户",
                "err_msg":"您没有权限进行操作，请联系管理员."
                    
            }
        # return HttpResponse(json.dumps(err_data))
        return render(self.request,"entm/permission_error.html",data)

    def form_valid(self, form):
        """
        If the form is valid, redirect to the supplied URL.
        """
        # print("user group add here?:",self.request.POST)
        # print(form)
        # do something
        instance = form.save(commit=False)
        instance.is_org = True
        cid = self.request.POST.get("pId","oranization")  #cid is parent orgnizations
        organizaiton_belong = Organizations.objects.get(cid=cid)
        instance.parent = organizaiton_belong
        instance.pId = cid
        instance.cid = unique_cid_generator(instance,new_cid=cid)

        instance.uuid = unique_uuid_generator(instance)
        


        return super(UserGroupAddView,self).form_valid(form)   


    def get(self,request, *args, **kwargs):
        print("get::::",args,kwargs)
        form = super(UserGroupAddView, self).get_form()
        # Set initial values and custom widget
        initial_base = self.get_initial() #Retrieve initial data for the form. By default, returns a copy of initial.
        # initial_base["menu"] = Menu.objects.get(id=1)
        initial_base["cid"] = kwargs.get("cid")
        initial_base["pId"] = kwargs.get("pId")
        form.initial = initial_base
        
        return render(request,self.template_name,
                      {"form":form,})


"""
Group edit, manager
"""
class UserGroupEditView(AjaxableResponseMixin,UserPassesTestMixin,UpdateView):
    model = Organizations
    form_class = OrganizationsEditForm
    template_name = "entm/groupedit.html"
    success_url = reverse_lazy("entm:rolemanager");

    # @method_decorator(permission_required("dma.change_stations"))
    def dispatch(self, *args, **kwargs):
        # self.role_id = kwargs["pk"]
        return super(UserGroupEditView, self).dispatch(*args, **kwargs)

    def test_func(self):
        if self.request.user.has_menu_permission_edit('organusermanager_firmmanager'):
            return True
        return False

    def handle_no_permission(self):
        data = {
                "mheader": "修改用户",
                "err_msg":"您没有权限进行操作，请联系管理员."
                    
            }
        # return HttpResponse(json.dumps(err_data))
        return render(self.request,"entm/permission_error.html",data)

    def form_valid(self, form):
        """
        If the form is valid, redirect to the supplied URL.
        """
        print("group update here?:",self.request.POST)
        # print(form)
        # do something
        
                

        return super(UserGroupEditView,self).form_valid(form)

    def get_object(self):
        print(self.kwargs)
        return Organizations.objects.get(cid=self.kwargs["pId"])
        

"""
Group Detail, manager
"""
class UserGroupDetailView(DetailView):
    model = Organizations
    form_class = OrganizationsEditForm
    template_name = "entm/groupdetail.html"
    # success_url = reverse_lazy("entm:rolemanager");

    # @method_decorator(permission_required("dma.change_stations"))
    def dispatch(self, *args, **kwargs):
        # self.role_id = kwargs["pk"]
        return super(UserGroupDetailView, self).dispatch(*args, **kwargs)

    
    def get_object(self):
        print(self.kwargs)
        return Organizations.objects.get(cid=self.kwargs["pId"])

"""
Assets comment deletion, manager
"""
class UserGroupDeleteView(AjaxableResponseMixin,UserPassesTestMixin,DeleteView):
    model = Organizations
    # template_name = "aidsbank/asset_comment_confirm_delete.html"

    def dispatch(self, *args, **kwargs):
        # self.comment_id = kwargs["pk"]

        
        print(self.request.POST)
        kwargs["pId"] = self.request.POST.get("pId")
        print("delete dispatch:",args,kwargs)
        return super(UserGroupDeleteView, self).dispatch(*args, **kwargs)

    def test_func(self):
        if self.request.user.has_menu_permission_edit('organusermanager_firmmanager'):
            return True
        return False

    def handle_no_permission(self):
        data = {
                "success": 0,
                "msg":"您没有权限进行操作，请联系管理员."
                    
            }
        return HttpResponse(json.dumps(data))
        # return render(self.request,"entm/permission_error.html",data)

    def get_object(self,*args, **kwargs):
        print("delete objects:",self.kwargs,kwargs)
        return Organizations.objects.get(cid=kwargs["pId"])

    def delete(self, request, *args, **kwargs):
        """
        Calls the delete() method on the fetched object and then
        redirects to the success URL.
        """
        print("delete?",args,kwargs)
        self.object = self.get_object(*args,**kwargs)
            

        # 不能删除自己所属的组织
        if self.object == self.request.user.belongto:
            return JsonResponse({"success":False,"msg":"不能删除自己所属的组织"})

        #删除组织 需要删除该组织的用户 和角色
        users = self.object.users.all()
        print('delete ',self.object,'and users:',users)
        for u in users:
            u.Role.delete()     #删除用户
            u.delete()
        for r in self.object.roles.all():
            r.delete()
        self.object.delete()
        return JsonResponse({"success":True})
        
    

#check if useradd name exists
def verifyUserName(request):
    print("verifyUserName:",request.POST)

    username = request.POST.get("userName")
    bflag = not User.objects.filter(user_name=username).exists()

    return HttpResponse(json.dumps({"success":bflag}))

def verification(request):
    print("verification:",request.POST,request.user)
    user = request.user
    user_expiredate = user.expire_date
    authorizationDate = request.POST.get("expire_date") #authorizationDate
    print('authorizationDate:',authorizationDate)
    a = datetime.strptime(user_expiredate,"%Y-%m-%d")
    b = datetime.strptime(authorizationDate.strip(),"%Y-%m-%d")
    bflag = b <= a
    return HttpResponse(json.dumps({"success":bflag}))




# 角色管理
class RolesMangerView(LoginRequiredMixin,TemplateView):
    template_name = "entm/rolelist.html"

    def get_context_data(self, *args, **kwargs):
        context = super(RolesMangerView, self).get_context_data(*args, **kwargs)
        context["page_title"] = "角色管理"
        context["page_menu"] = "企业管理"
        
        return context  


def roleimport(request):

    return HttpResponse(json.dumps({"success":"roleimport"}))


def roleexport(request):

    return HttpResponse(json.dumps({"success":"roleexport"}))

"""
Roles creation, manager
"""
class RolesAddView(AjaxableResponseMixin,UserPassesTestMixin,CreateView):
    model = MyRoles
    template_name = "entm/roleadd.html"
    form_class = RoleCreateForm
    success_url = reverse_lazy("entm:rolemanager");

    # @method_decorator(permission_required("dma.change_stations"))
    def dispatch(self, *args, **kwargs):
        return super(RolesAddView, self).dispatch(*args, **kwargs)

    def test_func(self):
        if self.request.user.has_menu_permission_edit('rolemanager_firmmanager'):
            return True
        return False

    def handle_no_permission(self):
        data = {
                "mheader": "添加角色",
                "err_msg":"您没有权限进行操作，请联系管理员."
                    
            }
        # return HttpResponse(json.dumps(err_data))
        return render(self.request,"entm/permission_error.html",data)

    def form_valid(self, form):
        """
        If the form is valid, redirect to the supplied URL.
        """
        # print("role create here?:",self.request.POST)
        # print(form)
        # do something
        permissiontree = form.cleaned_data.get("permissionTree")
        ptree = json.loads(permissiontree)
        instance = form.save()
        instance.rid = unique_rid_generator(instance)
        user = self.request.user
        #角色uid保存当前用户的uuid
        instance.uid = user.uuid   # or uuid
        # 角色所属组织，取当前用户的所属组织
        instance.belongto = user.belongto
        

        # for pt in ptree:
        #     pname = pt["id"]
        #     p_edit = pt["edit"]
        #     perms = Permission.objects.get(codename=pname)
            
        #     if p_edit:
        #         node_edit = "{}_edit".format(pname)
        #         perms_edit = Permission.objects.get(codename=node_edit)
        #         instance.permissions.add(perms)
        #         instance.permissions.add(perms_edit)


        return super(RolesAddView,self).form_valid(form)


"""
Roles edit, manager
"""
class RoleEditView(AjaxableResponseMixin,UserPassesTestMixin,UpdateView):
    model = MyRoles
    form_class = MyRolesForm
    template_name = "entm/roleedit.html"
    success_url = reverse_lazy("entm:rolemanager");

    # @method_decorator(permission_required("dma.change_stations"))
    def dispatch(self, *args, **kwargs):
        print('roleedit dispatch:',self.request,args,kwargs)
        return super(RoleEditView, self).dispatch(*args, **kwargs)

    def test_func(self):
        if self.request.user.has_menu_permission_edit('rolemanager_firmmanager'):
            return True
        return False

    def handle_no_permission(self):
        data = {
                "mheader": "修改用户",
                "err_msg":"您没有权限进行操作，请联系管理员."
                    
            }
        # return HttpResponse(json.dumps(err_data))
        return render(self.request,"entm/permission_error.html",data)

    def get_object(self,*args, **kwargs):
        print("role edit get object:",self.kwargs,kwargs)
        return MyRoles.objects.get(rid=self.kwargs["cn"])

    def form_valid(self, form):
        """
        If the form is valid, redirect to the supplied URL.
        """
        # print("role edit here?:",self.request.POST)
        # print(form)
        # do something
        permissiontree = self.request.POST.get("permissionTree")
        # print('permissiontree:',permissiontree)
        # print('user:',self.request.user.user_name)
        
        # ptree = json.loads(permissiontree)
        # instance = self.object
        # old_permissions = instance.permissions.all()
        # instance.permissions.clear()

        # for pt in ptree:
        #     pname = pt["id"]
        #     p_edit = pt["edit"]
        #     perms = Permission.objects.get(codename=pname)
            
        #     if p_edit:
        #         node_edit = "{}_edit".format(pname)
        #         perms_edit = Permission.objects.get(codename=node_edit)
        #         instance.permissions.add(perms)
        #         instance.permissions.add(perms_edit)
                

        return super(RoleEditView,self).form_valid(form)
        


def roledeletemore(request):
    print(request,request.POST)
    deltems = request.POST.get("deltems")
    deltems_list = deltems.split(';')

    if not request.user.has_menu_permission_edit('rolemanager_firmmanager'):
        return HttpResponse(json.dumps({"success":0,"msg":"您没有权限进行操作，请联系管理员."}))

    #被分配了的角色不可以删除
    assigned_roles = []
    for u in User.objects.all():
        assigned_roles.append(u.Role)
    
    flag = 0
    for uid in deltems_list:
        r = MyRoles.objects.get(rid=uid)
        # print('delete Role ',r)
        if r in assigned_roles:
            flag = 1
        else:
            r.delete()
    if flag:
        return HttpResponse(json.dumps({"success":0,"msg":"被分配了的角色不可以删除"}))
    return HttpResponse(json.dumps({"success":1}))


"""
Assets comment deletion, manager
"""
class RoleDeleteView(AjaxableResponseMixin,UserPassesTestMixin,DeleteView):
    model = MyRoles
    
    def dispatch(self, *args, **kwargs):
        print('role delete dispatch:',self.request,args,kwargs)

        print("role delete:",args,kwargs)
        
        return super(RoleDeleteView, self).dispatch(*args, **kwargs)

    def test_func(self):
        if self.request.user.has_menu_permission_edit('rolemanager_firmmanager'):
            return True
        return False

    def handle_no_permission(self):
        data = {
                "success": 0,
                "msg":"您没有权限进行操作，请联系管理员."
                    
            }
        return HttpResponse(json.dumps(data))
        # return render(self.request,"entm/permission_error.html",data)

    def get_object(self,*args, **kwargs):
        print("delete objects:",self.kwargs,kwargs)
        return MyRoles.objects.get(rid=self.kwargs["cn"])

    def delete(self, request, *args, **kwargs):
        """
        Calls the delete() method on the fetched object and then
        redirects to the success URL.
        """
        print("delete?",args,kwargs)
        self.object = self.get_object(*args,**kwargs)
        print('delete role ',self.object)
        #被分配了的角色不可以删除
        assigned_roles = []
        for u in User.objects.all():
            assigned_roles.append(u.Role)
        print('assigned_roles:',assigned_roles)
        if self.object in assigned_roles:
            return HttpResponse(json.dumps({"success":0,"msg":"被分配了的角色不可以删除"}))
        # for g in self.object.groups.all():
        #     g.user_set.remove(self.object)

        self.object.delete()
        result = dict()
        # result["success"] = 1
        return HttpResponse(json.dumps({"success":1}))


"""
组织和用户管理
"""
class UserMangerView(LoginRequiredMixin,TemplateView):
    template_name = "entm/userlist.html"

    def get_context_data(self, *args, **kwargs):
        context = super(UserMangerView, self).get_context_data(*args, **kwargs)
        context["page_menu"] = "企业管理"
        # context["page_submenu"] = "组织和用户管理"
        context["page_title"] = "组织和用户管理"

        # context["user_list"] = User.objects.all()
        

        return context  


"""
User add, manager
"""
class UserAddView(AjaxableResponseMixin,UserPassesTestMixin,CreateView):
    model = User
    template_name = "entm/useradd.html"
    form_class = RegisterForm
    success_url = reverse_lazy("entm:usermanager")
    # permission_required = ('entm.rolemanager_perms_firmmanager_edit', 'entm.organusermanager_perms_basemanager_edit')

    # @method_decorator(permission_required("dma.change_stations"))
    def dispatch(self, *args, **kwargs):
        #uuid is selectTreeIdAdd namely organizations uuid
        if self.request.method == 'GET':
            uuid = self.request.GET.get("uuid")
            kwargs["uuid"] = uuid

        if self.request.method == 'POST':
            uuid = self.request.POST.get("uuid")
            kwargs["uuid"] = uuid
        print("uuid:",kwargs.get('uuid'))
        return super(UserAddView, self).dispatch(*args, **kwargs)

    def test_func(self):
        if self.request.user.has_menu_permission_edit('organusermanager_firmmanager'):
            return True
        return False

    def handle_no_permission(self):
        data = {
                "mheader": "增加用户",
                "err_msg":"您没有权限进行操作，请联系管理员."
                    
            }
        # return HttpResponse(json.dumps(err_data))
        return render(self.request,"entm/permission_error.html",data)

    def form_valid(self, form):
        """
        If the form is valid, redirect to the supplied URL.
        """
        print("user  add here?:",self.request.POST)
        print(self.kwargs,self.args)
        # print(form)
        # do something
        user = self.request.user
        user_groupid = user.belongto.cid
        instance = form.save(commit=False)
        uid = self.request.POST.get('user_name')
        groupId = self.request.POST.get('groupId') # organization cid
        if user_groupid == groupId:
            data = {
                "success": 0,
                "obj":{
                    "flag":0,
                    "errMsg":"非管理员不能创建自己同级的用户,请重新选择所属企业。"
                    }
            }
            
            return HttpResponse(json.dumps(data)) #JsonResponse(data)
        organization = Organizations.objects.get(cid=groupId)
        instance.belongto = organization
        
        instance.idstr=groupId  #所属组织 cid

        instance.uuid=unique_uuid_generator(instance)

        # 用户状态
        is_active = self.request.POST.get('is_active')
        if is_active == '0':
            instance.is_active = False
        else:
            instance.is_active = True

        return super(UserAddView,self).form_valid(form)   

    def get_context_data(self, *args, **kwargs):
        context = super(UserAddView, self).get_context_data(*args, **kwargs)

        print('useradd context',args,kwargs,self.request)
        uuid = self.request.GET.get('uuid') or ''
        
        groupId = ''
        groupname = ''
        if len(uuid) > 0:
            organ = Organizations.objects.get(uuid=uuid)
            groupId = organ.cid
            groupname = organ.name
        # else:
        #     user = self.request.user
        #     groupId = user.belongto.cid
        #     groupname = user.belongto.name
        
        context["groupId"] = groupId
        context["groupname"] = groupname

        print("user add context data gourpId and groupname:",groupId,groupname)
        

        return context  


"""
User edit, manager
"""
class UserEditView(AjaxableResponseMixin,UserPassesTestMixin,UpdateView):
    model = User
    form_class = UserDetailChangeForm
    template_name = "entm/useredit.html"
    success_url = reverse_lazy("entm:usermanager")
    # login_url = None
    # permission_denied_message = 'Not allowed edit user,please contact manager'
    # permission_required = ('entm.erwqrqwer', 'entm.qewrqerq')
    # permission_required = ('entm.rolemanager_perms_firmmanager_edit', 'entm.organusermanager_perms_basemanager_edit')

    # @method_decorator(permission_required("dma.change_stations"))
    def dispatch(self, *args, **kwargs):
        # self.user_id = kwargs["pk"]
        return super(UserEditView, self).dispatch(*args, **kwargs)

    def test_func(self):
        if self.request.user.has_menu_permission_edit('organusermanager_firmmanager'):
            return True
        return False

    def handle_no_permission(self):
        data = {
                "mheader": "修改用户",
                "err_msg":"您没有权限进行操作，请联系管理员."
                    
            }
        # return HttpResponse(json.dumps(err_data))
        return render(self.request,"entm/permission_error.html",data)

    def form_invalid(self, form):
        """
        If the form is valid, redirect to the supplied URL.
        """
        print("user edit form_invalid:::")
        return super(UserEditView,self).form_invalid(form)

    def form_valid(self, form):
        """
        If the form is valid, redirect to the supplied URL.
        """
        print(form)
        print(self.request.POST)
        user = self.request.user
        user_groupid = user.belongto.cid
        instance = form.save(commit=False)
        uid = self.request.POST.get('user_name')
        groupId = self.request.POST.get('groupId') # organization cid
        if user_groupid == groupId:
            data = {
                "success": 0,
                "obj":{
                    "flag":0,
                    "errMsg":"非管理员不能创建自己同级的用户,请重新选择所属企业。"
                    }
            }
            
            return HttpResponse(json.dumps(data)) #JsonResponse(data)
        organization = Organizations.objects.get(cid=groupId)
        instance.belongto = organization
        
        instance.idstr=groupId  #所属组织 cid
        # 用户状态
        is_active = self.request.POST.get('is_active')
        if is_active == '0':
            instance.is_active = False
        else:
            instance.is_active = True
        # instance.uuid=unique_uuid_generator(instance)
        return super(UserEditView,self).form_valid(form)
        # role_list = MyRoles.objects.get(id=self.role_id)
        # return HttpResponse(render_to_string("dma/role_manager.html", {"role_list":role_list}))

    # def get_context_data(self, **kwargs):
    #     context = super(UserEditView, self).get_context_data(**kwargs)
    #     context["page_title"] = "修改用户"
    #     return context


class AssignRoleView(TemplateView,UserPassesTestMixin):
    """docstring for AssignRoleView"""
    template_name = "entm/assignrole.html"

    def test_func(self):
        if self.request.user.has_menu_permission_edit('organusermanager_firmmanager'):
            return True
        return False

    def handle_no_permission(self):
        data = {
                "mheader": "修改用户",
                "err_msg":"您没有权限进行操作，请联系管理员."
                    
            }
        # return HttpResponse(json.dumps(err_data))
        return render(self.request,"entm/permission_error.html",data)
        
    def get_context_data(self, **kwargs):
        context = super(AssignRoleView, self).get_context_data(**kwargs)
        context["page_title"] = "分配角色"
        # created_by_user = MyRoles.objects.filter(uid=self.request.user.uuid) 
        context["role_list"] = self.request.user.role_list()
        pk = kwargs["pk"]
        # context["object_id"] = pk
        context["object"] = self.get_object()
        return context

    def get_object(self):
        # print(self.kwargs)
        return User.objects.get(id=self.kwargs["pk"])

    def post(self,request,*args,**kwargs):
        print ("assinrole:",request.POST)
        print(kwargs)
        context = self.get_context_data(**kwargs)

        role_ids = request.POST.get("roleIds").split(",")
        print("role_ids:",role_ids)
        #只允许一个角色
        user = self.get_object()
        print("user:",user)

        rolename = ''
        for ri in role_ids:
            role = MyRoles.objects.get(id=int(ri))
            user.groups.add(role)
            print("role:",role)
            user.Role = role

            # permission_set = role.permissions.all()
            # user.user_permissions.add(permission_set)
        # user.Role = rolename
        
        user.save()

        data = {
                "msg": "分配完成",
                "obj":{"flag":1}
            }
        return JsonResponse(data)
        


class AssignStnView(TemplateView,UserPassesTestMixin):
    """docstring for AssignRoleView"""
    template_name = "entm/assignstn.html"
        
    def test_func(self):
        
        if self.request.user.has_menu_permission_edit('organusermanager_firmmanager'):
            return True
        return False

    def handle_no_permission(self):
        data = {
                "mheader": "修改用户",
                "err_msg":"您没有权限进行操作，请联系管理员."
                    
            }
        # return HttpResponse(json.dumps(err_data))
        return render(self.request,"entm/permission_error.html",data)

    def get_context_data(self, **kwargs):
        context = super(AssignStnView, self).get_context_data(**kwargs)
        context["page_title"] = "分配角色"
        context["role_list"] = MyRoles.objects.all()
        pk = kwargs["pk"]
        context["object_id"] = pk
        context["user"] = User.objects.get(pk=pk)
        return context

    def get_object(self):
        # print(self.kwargs)
        return User.objects.get(id=self.kwargs["pk"])

    def post(self,request,*args,**kwargs):
        
        context = self.get_context_data(**kwargs)

        role = request.POST.get("checks[]")
        user = context["user"]
        # user.Role = role
        group = MyRoles.objects.filter(name__iexact=role).first()
        
        user.groups.add(group)
        user.save()

        data = {
                "msg": "分配完成",
                "obj":{"flag":1}
            }
        return JsonResponse(data)


def userdeletemore(request):
    # print('userdeletemore',request,request.POST)

    if not request.user.has_menu_permission_edit('organusermanager_firmmanager'):
        return HttpResponse(json.dumps({"success":0,"msg":"您没有权限进行操作，请联系管理员."}))

    deltems = request.POST.get("deltems")
    deltems_list = deltems.split(';')

    for uid in deltems_list:
        u = User.objects.get(id=int(uid))
        # print('delete user ',u)
        #删除用户 并且删除用户在分组中的角色
        for g in u.groups.all():
            g.user_set.remove(u)
        u.delete()

    return HttpResponse(json.dumps({"success":1}))

"""
Assets comment deletion, manager
"""
class UserDeleteView(AjaxableResponseMixin,UserPassesTestMixin,DeleteView):
    model = User
    # template_name = "aidsbank/asset_comment_confirm_delete.html"

    def test_func(self):
        
        if self.request.user.has_menu_permission_edit('organusermanager_firmmanager'):
            return True
        return False

    def handle_no_permission(self):
        data = {
                "success": 0,
                "msg":"您没有权限进行操作，请联系管理员."
                    
            }
        HttpResponse(json.dumps(data))
        # return render(self.request,"entm/permission_error.html",data)

    def dispatch(self, *args, **kwargs):
        # self.comment_id = kwargs["pk"]

        print("user delete:",args,kwargs)
        
        return super(UserDeleteView, self).dispatch(*args, **kwargs)

    def get_object(self,*args, **kwargs):
        # print("delete objects:",self.kwargs,kwargs)
        return User.objects.get(pk=kwargs["pk"])

    def delete(self, request, *args, **kwargs):
        """
        Calls the delete() method on the fetched object and then
        redirects to the success URL.
        """
        print("delete?",args,kwargs)
        self.object = self.get_object(*args,**kwargs)

        #delete user role in groups
        for g in self.object.groups.all():
            g.user_set.remove(self.object)

        self.object.delete()
        result = dict()
        # result["success"] = 1
        return HttpResponse(json.dumps({"success":1}))
        

class AuthStationView(TemplateView):
    """docstring for AuthStationView"""
    template_name = "dma/auth_station.html"
        
    def get_context_data(self, **kwargs):
        context = super(AuthStationView, self).get_context_data(**kwargs)
        context["page_title"] = "分配角色"
        return context        

class UserImportView(TemplateView,UserPassesTestMixin):
    """docstring for AssignRoleView"""
    template_name = "entm/importuser.html"
        
    def test_func(self):
        
        if self.request.user.has_menu_permission_edit('organusermanager_firmmanager'):
            return True
        return False

    def handle_no_permission(self):
        data = {
                "mheader": "修改用户",
                "err_msg":"您没有权限进行操作，请联系管理员."
                    
            }
        # return HttpResponse(json.dumps(err_data))
        return render(self.request,"entm/permission_error.html",data)

    def get_context_data(self, **kwargs):
        context = super(UserImportView, self).get_context_data(**kwargs)
        context["page_title"] = "导入用户"
        
        return context

    # def get_object(self):
    #     # print(self.kwargs)
    #     return User.objects.get(id=self.kwargs["pk"])

    def check_row(self, row, **kwargs):
        user = kwargs["user"]
        print("row :::",row)

        err_msg = []
        
        username = str(row[u'用户名'])
        print('username:',username)
        # 从excel读上来的数据全是数字都是float类型
        if '.' in username:
            if isinstance(row[u'用户名'],float):
                username = str(int(row[u'用户名']))
                
        bflag = User.objects.filter(user_name=username).exists()
        if bflag:
            err_msg.append(u"用户%s已存在"%(username))


        # Excel save date as float
        authorizationDate = row[u'授权截止日期']
        if isinstance(authorizationDate,str):
            b = datetime.strptime(authorizationDate.strip(),"%Y-%m-%d")
        else:
            authorizationDate = int(row[u'授权截止日期'])
            b = minimalist_xldate_as_datetime(authorizationDate,0)

        user_expiredate = user.expire_date
        print(authorizationDate,user_expiredate)
        
        a = datetime.strptime(user_expiredate,"%Y-%m-%d")
        # 
        
        print('time a:',a,"b:",b)
        bflag = b <= a
        if not bflag:
            err_msg.append(u"用户授权截止日期大于当前用户的截止日期%s"%(user_expiredate))

        phone_number = str(row[u'手机'])
        if '.' in phone_number:
            if isinstance(row[u'手机'],float):
                phone_number = str(int(row[u'手机']))
                row[u'手机'] = phone_number

        gender = row[u'性别']
        if gender == u'男':
            row[u'性别'] = 1
        elif gender == u'女':
            row[u'性别'] = 2
        else:
            err_msg.append(u"请输入正确的性别")

        state = row[u'启停状态']
        if state == u'启用':
            row[u'启停状态'] = True
        elif state == u'停用':
            row[u'启停状态'] = False
        else:
            err_msg.append(u"请输入正确的启停状态")

        org_name = row[u'所属组织']
        org = Organizations.objects.filter(name=org_name)
        print('org:',org)
        if org.exists():
            row[u'所属组织'] = org[0]
        else:
            row[u'所属组织'] = org[0]
            err_msg.append(u"该组织%s不存在"%(org_name))

        role_name = row[u'角色']
        role = MyRoles.objects.filter(name=role_name)
        print('role:',role)
        if role.exists():
            row[u'角色'] = role[0]
        else:
            row[u'角色'] = None
            err_msg.append(u"该角色%s不存在"%(role_name))

        return err_msg


    def post(self,request,*args,**kwargs):
        
        context = self.get_context_data(**kwargs)
        print('importuser post:',self.request)

        user = request.user

        person_resource = UserResource()
        dataset = Dataset()
        # dataset.headers = ('user_name', 'real_name', 'sex','phone_number','email','is_active','expire_date','belongto','Role')
        new_persons = self.request.FILES['file']
        # print('new_persons:',new_persons.read())
        file_contents = new_persons.read()  #.decode('iso-8859-15')
        imported_data = dataset.load(file_contents,'xls')
        print('imported_data:',imported_data.dict)
        kwargs["user"] = user

        row_count = 0
        err_msgs = []
        for row in imported_data.dict:
            row_count += 1

            err = self.check_row(row,**kwargs)
            print('check row :',row_count,err)
            if len(err) > 0:
                emsg = u'第%s条错误:<br/>'%(row_count) + '<br/>'.join(e for e in err)
                err_msgs.append(emsg)

        err_count = len(err_msgs)
        success_count = row_count - err_count
        print('err_msgs:',err_msgs)
        if err_count > 0:
            msg = '导入结果:正确%s条<br />'%(success_count)+'错误%s条<br/>'%(err_count)+'<br/>'.join(e for e in err_msgs)
            
        else:
            msg = '导入结果:成功导入%s条<br />'%(success_count)+'失败%s条<br/>'%(err_count)
            person_resource.import_data(dataset, dry_run=False,**kwargs)  # Actually import now

        # result = person_resource.import_data(dataset, dry_run=True,**kwargs)  # Test the data import
        # if not result.has_errors():
        #     person_resource.import_data(dataset, dry_run=False,**kwargs)  # Actually import now
        
        data={"exceptionDetailMsg":"null",
                "msg":msg,
                "obj":"null",
                "success":True
        }
        
        return HttpResponse(json.dumps(data))


def importProgress(request):
    return HttpResponse(json.dumps({'success':1}))

def download(request):
    file_path = os.path.join(settings.STATICFILES_DIRS[0] , '用户模板.xls') #development
    
    # file_path = os.path.join(settings.STATIC_ROOT , '用户模板.xls')
    print('file_path:',file_path)
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = 'attachment; filename=' + escape_uri_path("用户模板.xls")
            return response
    # raise Http404
    return HttpResponse(json.dumps({'success':0,'msg':'file not found'}))


def userexport(request):
    user_resource = UserResource()
    user_query_set = request.user.user_list_queryset()
    dataset = user_resource.export(user_query_set)
    response = HttpResponse(dataset.xls, content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="atest2.xls"'
    return response
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

from entm.utils import unique_cid_generator,unique_uuid_generator,unique_rid_generator
from entm.forms import OrganizationsAddForm,OrganizationsEditForm
from entm.models import Organizations
from legacy.models import Bigmeter,District,Community
from . models import WaterUserType
from legacy.forms import StationsForm
from . forms import WaterUserTypeForm
import os
from django.conf import settings

from waterwork.mixins import AjaxableResponseMixin
import logging

logger_info = logging.getLogger('info_logger')
logger_error = logging.getLogger('error_logger')




def dmatree(request):   
    organtree = []

    user = request.user
    organs = user.belongto #Organizations.objects.all()
    
    for o in organs.get_descendants(include_self=True):
        organtree.append({
            "name":o.name,
            "id":o.cid,
            "pId":o.pId,
            "districtid":'',
            "type":"group",
            "uuid":o.uuid
        })

    # district
    districts = District.objects.all()
    for d in districts:
        organtree.append({
            "name":d.name,
            "id":d.id,
            "districtid":d.id,
            "pId":organs.cid,
            "type":"district",
            "icon":"/static/virvo/resources/img/u8836.png",
            "uuid":''
        })
        # bigmeters = Bigmeter.objects.filter(districtid=d.id)
        # for b in bigmeters:
        #     organtree.append({
        #     "name":b.username,
        #     "id":b.userid,
        #     "stationid":b.userid,
        #     "pId":d.id,
        #     "type":"station",
        #     "icon":"/static/virvo/resources/img/u8836.png",
        #     "uuid":''
        # })

    #bigmeter

    
    result = dict()
    result["data"] = organtree
    
    # print(json.dumps(result))
    
    return HttpResponse(json.dumps(organtree))


def stationlist(request):
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
        districtId = request.POST.get("districtId")
        simpleQueryParam = request.POST.get("simpleQueryParam")
        # print(request.POST.get("draw"))
        print("groupName",groupName)
        print("districtId:",districtId)
        # print("post simpleQueryParam",simpleQueryParam)

    print("get userlist:",draw,length,start,search_value)

    #当前登录用户
    current_user = request.user

    def u_info(u):
        
        return {
            "id":u.pk,
            "username":u.username,
            "usertype":u.usertype,
            "simid":u.simid,
            "dn":u.dn,
            "belongto":u.districtid.name,#current_user.belongto.name,
            "metertype":u.metertype,
            "serialnumber":u.serialnumber,
            "big_user":1,
            "focus":1,
            "createdate":u.createdate
        }
    data = []
    
    
    # userl = current_user.user_list()

    bigmeters = Bigmeter.objects.all()
    
    
    # print("user all:",userl)
    if districtId != "":
        #查询的组织
        query_district = District.objects.get(id=districtId)
        bigmeters = [u for u in bigmeters if u.districtid == query_district]
        # print("query organ user,",userl)

    
    
    # def search_user(u):
    #     if simpleQueryParam in u.user_name or simpleQueryParam in u.real_name or simpleQueryParam in u.email or simpleQueryParam in u.phone_number :
    #         return True


    # if simpleQueryParam != "":
    #     print('simpleQueryParam:',simpleQueryParam)
    #     # userl = userl.filter(real_name__icontains=simpleQueryParam)
    #     userl = [u for u in userl if search_user(u) is True]
    
    # for u in userl[start:start+length]:
    #     data.append(u_info(u))

    

    for m in bigmeters[start:start+length]:
        data.append(u_info(m))
    
    recordsTotal = len(bigmeters)
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



class DistrictMangerView(LoginRequiredMixin,TemplateView):
    template_name = "dmam/districtlist.html"

    def get_context_data(self, *args, **kwargs):
        context = super(DistrictMangerView, self).get_context_data(*args, **kwargs)
        context["page_menu"] = "dma管理"
        # context["page_submenu"] = "组织和用户管理"
        context["page_title"] = "dma分区管理"

        # context["user_list"] = User.objects.all()
        

        return context  

    """
group add
"""
class DistrictAddView(AjaxableResponseMixin,UserPassesTestMixin,CreateView):
    model = Organizations
    template_name = "dmam/groupadd.html"
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
        return super(DistrictAddView, self).dispatch(*args, **kwargs)

    def test_func(self):
        if self.request.user.has_menu_permission_edit('dmamanager_basemanager'):
            return True
        return False

    def handle_no_permission(self):
        data = {
                "mheader": "修改用户",
                "err_msg":"您没有权限进行操作，请联系管理员."
                    
            }
        # return HttpResponse(json.dumps(err_data))
        return render(self.request,"dmam/permission_error.html",data)

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
        


        return super(DistrictAddView,self).form_valid(form)   


    def get(self,request, *args, **kwargs):
        print("get::::",args,kwargs)
        form = super(DistrictAddView, self).get_form()
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
class DistrictEditView(AjaxableResponseMixin,UserPassesTestMixin,UpdateView):
    model = Organizations
    form_class = OrganizationsEditForm
    template_name = "dmam/groupedit.html"
    success_url = reverse_lazy("entm:rolemanager");

    # @method_decorator(permission_required("dma.change_stations"))
    def dispatch(self, *args, **kwargs):
        # self.role_id = kwargs["pk"]
        return super(DistrictEditView, self).dispatch(*args, **kwargs)

    def test_func(self):
        if self.request.user.has_menu_permission_edit('dmamanager_basemanager'):
            return True
        return False

    def handle_no_permission(self):
        data = {
                "mheader": "修改用户",
                "err_msg":"您没有权限进行操作，请联系管理员."
                    
            }
        # return HttpResponse(json.dumps(err_data))
        return render(self.request,"dmam/permission_error.html",data)

    def form_valid(self, form):
        """
        If the form is valid, redirect to the supplied URL.
        """
        print("group update here?:",self.request.POST)
        # print(form)
        # do something
        
                

        return super(DistrictEditView,self).form_valid(form)

    def get_object(self):
        print(self.kwargs)
        return Organizations.objects.get(cid=self.kwargs["pId"])
        

"""
Group Detail, manager
"""
class DistrictDetailView(DetailView):
    model = Organizations
    form_class = OrganizationsEditForm
    template_name = "dmam/groupdetail.html"
    # success_url = reverse_lazy("entm:rolemanager");

    # @method_decorator(permission_required("dma.change_stations"))
    def dispatch(self, *args, **kwargs):
        # self.role_id = kwargs["pk"]
        return super(DistrictDetailView, self).dispatch(*args, **kwargs)

    
    def get_object(self):
        print(self.kwargs)
        return Organizations.objects.get(cid=self.kwargs["pId"])

"""
Assets comment deletion, manager
"""
class DistrictDeleteView(AjaxableResponseMixin,UserPassesTestMixin,DeleteView):
    model = Organizations
    # template_name = "aidsbank/asset_comment_confirm_delete.html"

    def dispatch(self, *args, **kwargs):
        # self.comment_id = kwargs["pk"]

        
        print(self.request.POST)
        kwargs["pId"] = self.request.POST.get("pId")
        print("delete dispatch:",args,kwargs)
        return super(DistrictDeleteView, self).dispatch(*args, **kwargs)

    def test_func(self):
        if self.request.user.has_menu_permission_edit('dmamanager_basemanager'):
            return True
        return False

    def handle_no_permission(self):
        data = {
                "success": 0,
                "msg":"您没有权限进行操作，请联系管理员."
                    
            }
        return HttpResponse(json.dumps(data))
        # return render(self.request,"dmam/permission_error.html",data)

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




"""
用水性质
"""

def findusertypeByusertype(request):
    print(request.POST)
    usertype = request.POST.get('type')
    flag = not WaterUserType.objects.filter(usertype=usertype).exists()

    return JsonResponse(flag, safe=False)

def usertypeadd(request):
    if not request.user.has_menu_permission_edit('stationmanager_basemanager'):
        return HttpResponse(json.dumps({"success":0,"msg":"您没有权限进行操作，请联系管理员."}))

    print('usertypeadd:',request.POST)
    usertypeform = WaterUserTypeForm(request.POST or None)

    if usertypeform.is_valid():
        obj = WaterUserType.objects.create(
            usertype = usertypeform.cleaned_data.get('usertype'),
            explains = usertypeform.cleaned_data.get('explains'))

    if usertypeform.errors:
        print(usertypeform.errors)

    return HttpResponse(json.dumps({"success":1}))

def usertypeedit(request):
    pass


def usertypedeletemore(request):
    if not request.user.has_menu_permission_edit('stationmanager_basemanager'):
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


def userdeletemore(request):
    # print('userdeletemore',request,request.POST)

    if not request.user.has_menu_permission_edit('dmamanager_basemanager'):
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
class UsertypeDeleteView(AjaxableResponseMixin,UserPassesTestMixin,DeleteView):
    model = WaterUserType
    # template_name = "aidsbank/asset_comment_confirm_delete.html"

    def test_func(self):
        
        if self.request.user.has_menu_permission_edit('stationmanager_basemanager'):
            return True
        return False

    def handle_no_permission(self):
        data = {
                "success": 0,
                "msg":"您没有权限进行操作，请联系管理员."
                    
            }
        HttpResponse(json.dumps(data))
        # return render(self.request,"dmam/permission_error.html",data)

    def dispatch(self, *args, **kwargs):
        # self.comment_id = kwargs["pk"]

        print("user delete:",args,kwargs)
        
        return super(StationDeleteView, self).dispatch(*args, **kwargs)

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
        

class StationMangerView(LoginRequiredMixin,TemplateView):
    template_name = "dmam/stationlist.html"

    def get_context_data(self, *args, **kwargs):
        context = super(StationMangerView, self).get_context_data(*args, **kwargs)
        context["page_menu"] = "dma管理"
        # context["page_submenu"] = "组织和用户管理"
        context["page_title"] = "站点管理"

        # context["user_list"] = User.objects.all()
        

        return context  


"""
User add, manager
"""
class StationAddView(AjaxableResponseMixin,UserPassesTestMixin,CreateView):
    model = User
    template_name = "dmam/useradd.html"
    form_class = RegisterForm
    success_url = reverse_lazy("entm:usermanager")
    # permission_required = ('entm.rolemanager_perms_basemanager_edit', 'entm.dmamanager_perms_basemanager_edit')

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
        return super(StationAddView, self).dispatch(*args, **kwargs)

    def test_func(self):
        if self.request.user.has_menu_permission_edit('stationmanager_basemanager'):
            return True
        return False

    def handle_no_permission(self):
        data = {
                "mheader": "增加用户",
                "err_msg":"您没有权限进行操作，请联系管理员."
                    
            }
        # return HttpResponse(json.dumps(err_data))
        return render(self.request,"dmam/permission_error.html",data)

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
        context = super(StationAddView, self).get_context_data(*args, **kwargs)

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
class StationEditView(AjaxableResponseMixin,UserPassesTestMixin,UpdateView):
    model = Bigmeter
    form_class = StationsForm
    template_name = "dmam/stationedit.html"
    success_url = reverse_lazy("entm:usermanager")
    
    # @method_decorator(permission_required("dma.change_stations"))
    def dispatch(self, *args, **kwargs):
        # self.user_id = kwargs["pk"]
        return super(StationEditView, self).dispatch(*args, **kwargs)

    def get_object(self):
        return Bigmeter.objects.get(commaddr=self.kwargs["caddr"])

    def test_func(self):
        if self.request.user.has_menu_permission_edit('stationmanager_basemanager'):
            return True
        return False

    def handle_no_permission(self):
        data = {
                "mheader": "修改站点",
                "err_msg":"您没有权限进行操作，请联系管理员."
                    
            }
        # return HttpResponse(json.dumps(err_data))
        return render(self.request,"dmam/permission_error.html",data)

    def form_invalid(self, form):
        """
        If the form is valid, redirect to the supplied URL.
        """
        print("user edit form_invalid:::")
        return super(StationEditView,self).form_invalid(form)

    def form_valid(self, form):
        """
        If the form is valid, redirect to the supplied URL.
        """
        print(form)
        print(self.request.POST)
        user = self.request.user
        
        # instance.uuid=unique_uuid_generator(instance)
        return super(StationEditView,self).form_valid(form)
        # role_list = MyRoles.objects.get(id=self.role_id)
        # return HttpResponse(render_to_string("dma/role_manager.html", {"role_list":role_list}))

    # def get_context_data(self, **kwargs):
    #     context = super(UserEditView, self).get_context_data(**kwargs)
    #     context["page_title"] = "修改用户"
    #     return context



def userdeletemore(request):
    # print('userdeletemore',request,request.POST)

    if not request.user.has_menu_permission_edit('dmamanager_basemanager'):
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
class StationDeleteView(AjaxableResponseMixin,UserPassesTestMixin,DeleteView):
    model = User
    # template_name = "aidsbank/asset_comment_confirm_delete.html"

    def test_func(self):
        
        if self.request.user.has_menu_permission_edit('stationmanager_basemanager'):
            return True
        return False

    def handle_no_permission(self):
        data = {
                "success": 0,
                "msg":"您没有权限进行操作，请联系管理员."
                    
            }
        HttpResponse(json.dumps(data))
        # return render(self.request,"dmam/permission_error.html",data)

    def dispatch(self, *args, **kwargs):
        # self.comment_id = kwargs["pk"]

        print("user delete:",args,kwargs)
        
        return super(StationDeleteView, self).dispatch(*args, **kwargs)

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
        
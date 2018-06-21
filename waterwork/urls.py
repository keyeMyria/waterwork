# -*- coding:utf-8 -*-

"""leakage URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url,include,handler404,handler500
from django.contrib import admin

from entm.views import i18n_javascript,error_404,error_500,StaticView
from django.views.generic import TemplateView
from django.views.generic.base import RedirectView
from django.contrib.auth.views import LogoutView

from accounts.views import LoginView, RegisterView

urlpatterns = [
    url(r'^favicon\.ico$', RedirectView.as_view(url='/static/images/favicon.ico')),
    url(r'^admin/jsi18n', i18n_javascript),
    url(r'^admin/', admin.site.urls),
    url(r'^$',LoginView.as_view(), name='login'),
    # url(r'^$',TemplateView.as_view(template_name='_vbase.html'),name='home'),

    url(r'^(?P<page>.+\.html)$', StaticView.as_view()),

    #使用hplus页面布局是iframe加载的首页项
    url(r'^index/$', TemplateView.as_view(template_name='_hplus_vbase.html'), name='index'),

    url(r'^accounts/$', RedirectView.as_view(url='/account')),
    url(r'^account/', include("accounts.urls", namespace='account')),
    url(r'^register/$', RegisterView.as_view(), name='register'),
    url(r'^login/$', LoginView.as_view(), name='login'),
    url(r'^logout/$', LogoutView.as_view(), name='logout'),
    
    #monitor
    url(r'^monitor/', include('monitor.urls', namespace='monitor')),

    #waterwork
    url(r'^entm/', include('entm.urls', namespace='entm')),
    
]

handler404 = error_404
handler500 = error_500
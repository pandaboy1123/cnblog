"""cnblog URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path
from django.conf.urls import url
from django.views.static import serve
from blog import views
from cnblog import settings
from blog.check_views import pcgetcaptcha
from blog.check_views import pcvalidate
from blog.check_views import pcajax_validate
from blog.check_views import mobileajax_validate
from blog.check_views import home

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', views.login),
    path('logout/', views.logout),
    path('register/', views.register),
    path('index/', views.index),
    path('digg/', views.digg),
    path('comment/', views.comment),
    path('get_comment_tree/', views.get_comment_tree),
    # re_path('^$', views.index),
    path('get_validCode_img/', views.get_validCode_img),
    # media配置
    re_path(r"media/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT}),
    # 个人站点配置
    re_path('^(?P<username>\w+)/(?P<condition>tag|category|archive)/(?P<param>.*)/$', views.home_site),
    re_path('^(?P<username>\w+)/$', views.home_site),
    re_path('^(?P<username>\w+)/articles/(?P<article_id>\d+)$', views.article_detail),
    # 后台管理url
    re_path("cn_backend/$", views.cn_backend),
    re_path("cn_backend/add_article/$", views.add_article),
    # 认证路由
    url(r'^pc-geetest/register', pcgetcaptcha, name='pcgetcaptcha'),
    url(r'^mobile-geetest/register', pcgetcaptcha, name='mobilegetcaptcha'),
    url(r'^pc-geetest/validate$', pcvalidate, name='pcvalidate'),
    url(r'^pc-geetest/ajax_validate', pcajax_validate, name='pcajax_validate'),
    url(r'^mobile-geetest/ajax_validate', mobileajax_validate, name='mobileajax_validate'),
    # url(r'/*/', home, name='home'),
]

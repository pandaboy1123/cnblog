from django.shortcuts import render, HttpResponse, redirect
from blog.utils.ValidCode import get_valid_code_img
from django.http import JsonResponse
from django.contrib import auth
from django.views.decorators.csrf import csrf_exempt
from blog.Myforms import UserForm
from blog.models import UserInfo, Comment
from blog import models
from django.db.models import Count
from django.db.models import F
import json
from django.db import transaction
from bs4 import BeautifulSoup
from django.db.models.functions import TruncMonth
from django.contrib.auth.decorators import login_required
import os
from cnblog import settings
# Create your views here.


@csrf_exempt
def login(request):
    if request.method == 'POST':
        response = {'user': None, 'msg': None}
        user = request.POST.get("user")
        pwd = request.POST.get("pwd")
        # valid_code = request.POST.get("valid_code")
        # valid_code_str = request.session.get('valid_code_str')
        # if valid_code.upper() == valid_code_str.upper():
        user = auth.authenticate(username=user, password=pwd)
        if user:
            auth.login(request, user)
            response['user'] = user.username
            return JsonResponse(response)
        else:
            response["msg"] = "账号或密码错误!!"
            return JsonResponse(response)
        # else:
        #     response['msg'] = "验证码错误!!!"
        # return JsonResponse(response)
    return render(request, 'login.html')


def get_validCode_img(request):
    data = get_valid_code_img(request)
    return HttpResponse(data)


def logout(request):
    auth.logout(request)
    return redirect("/login/")


def index(request):
    article_list = models.Article.objects.all()
    return render(request, 'index.html', {"article_list": article_list})


def register(request):
    if request.is_ajax():
        # print(request.POST)
        form = UserForm(request.POST)
        response = {"user": None, "msg": None}
        if form.is_valid():
            response["user"] = form.cleaned_data.get("user")
            #     生成一条用户记录
            user = form.cleaned_data.get('user')
            pwd = form.cleaned_data.get('pwd')
            re_pwd = form.cleaned_data.get('re_pwd')
            email = form.cleaned_data.get('email')
            avatar_obj = request.FILES.get('avatar')
            extra = {}
            if avatar_obj:
                extra["avatar"] = avatar_obj
                UserInfo.objects.create_user(username=user, password=pwd, email=email, **extra)
        else:
            # print(form.cleaned_data)
            # print(form.errors)
            response["msg"] = form.errors
        return JsonResponse(response)
    form = UserForm()
    return render(request, 'register.html', locals())


def home_site(request, username, **kwargs):
    '''
    个人站点视图函数
    :param request:
    :return:
    '''
    # print(username)
    user = UserInfo.objects.filter(username=username).first()
    if not user:
        return render(request, 'not_found.html')
    # 查询当前站点对象
    blog = user.blog
    # 当前用户或所有的站点信息查询到
    # 基于对象查询
    # article_list = user.article_set.all()
    # 基于__查询
    article_list = models.Article.objects.filter(user=user)
    if kwargs:
        condition = kwargs.get("condition")
        param = kwargs.get("param")
        if condition == "category":
            article_list = article_list.filter(category__title=param)
        elif condition == "tag":
            article_list = article_list.filter(tags__title=param)
        else:
            year, month = param.split('-')
            article_list = article_list.filter(create_time__year=year, create_time__month=month)
    # 查询每一个分类名称以及对应的文章数
    # ret = models.Category.objects.values("pk").annotate(c=Count("article__title")).values("title", "c")
    # print(ret)
    # 查询当前站点的每一个分类名称以及对应的文章数
    # cate_list = models.Category.objects.filter(blog=blog).values("pk").annotate(c=Count("article__title")).values_list("title", "c")
    # print(cate_list)
    # 查询当前站点的每一个标签名称以及对应的文章数
    # tag_list = models.Tag.objects.filter(blog=blog).values("pk").annotate(c=Count("article__title")).values_list("title", "c")
    # print(tag_list)
    # 查询当前站点每一个年月的名称以及对应的文章数
    # ret = models.Article.objects.extra(select={"is_recent": "create_time > '2018-10-10'"}).values("title", "is_recent")
    # print(ret)
    # date_list = models.Article.objects.filter(user=user).extra(select={"y_m_date": "date_format(create_time, '%%Y-%%m')"}).values("y_m_date").annotate(c=Count('nid')).values_list("y_m_date", "c")
    # print(date_list)
    # date_list = models.Article.objects.filter(user=user).annotate(month=TruncMonth("create_time")).values("month").annotate(c=Count("nid")).values_list("month", "c")
    # print(ret)
    return render(request, "home_site.html", locals())


def article_detail(request, username, article_id):
    context = get_classification_data(username)
    article_obj = models.Article.objects.filter(pk=article_id).first()
    user = UserInfo.objects.filter(username=username).first()
    # 查询当前站点对象
    blog = user.blog
    comment_list = models.Comment.objects.filter(article_id=article_id)

    return render(request, "article_detail.html", locals())


def get_classification_data(username):
    user = UserInfo.objects.filter(username=username).first()
    # 查询当前站点对象
    blog = user.blog
    cate_list = models.Category.objects.filter(blog=blog).values("pk").annotate(c=Count("article__title")).values_list(
        "title", "c")
    tag_list = models.Tag.objects.filter(blog=blog).values("pk").annotate(c=Count("article__title")).values_list(
        "title", "c")
    date_list = models.Article.objects.filter(user=user).extra(
        select={"y_m_date": "date_format(create_time, '%%Y-%%m')"}).values("y_m_date").annotate(
        c=Count('nid')).values_list("y_m_date", "c")
    return {"blog": blog, "cate_list": cate_list, "tag_list": tag_list, "date_list": date_list}


def digg(request):
    article_id = request.POST.get("article_id")
    is_up = json.loads(request.POST.get("is_up"))
    user_id = request.user.pk
    response = {"state": True, "msg": None}
    obj = models.ArticleUpDown.objects.filter(user_id=user_id, article_id=article_id).first()
    queryset = models.Article.objects.filter(pk=article_id)
    if not obj:
        ard = models.ArticleUpDown.objects.create(user_id=user_id, article_id=article_id, is_up=is_up)
        if is_up:
            # print(is_up)
            queryset.update(up_count=F("up_count") + 1)
        else:
            # print(is_up)
            queryset.update(down_count=F("down_count") + 1)
    else:
        response["state"] = False
        response["handled"] = is_up

    return JsonResponse(response)


def comment(request):
    # print(request.POST)
    article_id = request.POST.get('article_id')
    pid = request.POST.get('pid')
    content = request.POST.get('content')
    user_id = request.user.pk
    with transaction.atomic():
        comment_obj = models.Comment.objects.create(user_id=user_id, article_id=article_id, content=content,
                                                    parent_comment_id_id=pid)
        models.Article.objects.filter(pk=article_id).update(comment_count=F("comment_count") + 1)

    response = {}
    response["create_time"] = comment_obj.create_time.strftime("%Y-%m-%d %S")
    response["username"] = request.user.username
    response["content"] = content
    response["comment_pk"] = user_id
    return JsonResponse(response)


def get_comment_tree(request):
    article_id = request.GET.get("article_id")
    ret = list(models.Comment.objects.filter(article_id=article_id).order_by('pk').values("pk", "content",
                                                                                          "parent_comment_id"))

    return JsonResponse(ret, safe=False)


@login_required
def cn_backend(request):
    """
    后台管理的首页
    :param request:
    :return:
    """
    article_list = models.Article.objects.filter(user=request.user)
    return render(request, "backend/add_article.html", locals())


@login_required
def add_article(request):
    """
    后台管理的添加书籍视图函数
    :param request:
    :return:
    """
    if request.method == "POST":
        title = request.POST.get("title")
        content = request.POST.get("content")

        # 防止xss攻击,过滤script标签
        soup = BeautifulSoup(content, "html.parser")
        for tag in soup.find_all():
            # print(tag.name)
            if tag.name == "script":
                tag.decompose()
        # 构建摘要数据,获取标签字符串的文本前150个符号
        desc = soup.text[0:150] + "..."

        models.Article.objects.create(title=title, desc=desc, content=str(soup), user=request.user)
        return redirect("/index/")

    return render(request, "backend/add_article.html")


def upload(request):
    """
    编辑器上传文件接受视图函数
    :param request:
    :return:
    """

    print(request.FILES)
    img_obj = request.FILES.get("upload_img")
    print(img_obj.name)

    path = os.path.join(settings.MEDIA_ROOT, "add_article_img", img_obj.name)

    with open(path, "wb") as f:
        for line in img_obj:
            f.write(line)

    return HttpResponse("ok")

from django.shortcuts import render, HttpResponse, redirect
from blog import models
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from utils.myforms import LoginForm, RegForm
from io import BytesIO
from utils.random_check_code import rd_check_code
import json


def produce_code(request):
    img, code = rd_check_code()
    mem_file_handle = BytesIO()
    img.save(mem_file_handle, 'png')
    request.session['code'] = code
    return HttpResponse(mem_file_handle.getvalue())


def index(request, *args, **kwargs):
    # data display
    condition = {}
    type_choices_list = models.Article.type_choices
    type_id = int(kwargs.get('type_id')) if kwargs.get('type_id') else None
    if type_id:
       condition['article_type_id'] = type_id
    article_list = models.Article.objects.filter(**condition)

    # paginator
    pg = request.GET.get('pg')
    p_obj = Paginator(article_list, 5)
    page_list = p_obj.page_range
    total_page_count = p_obj.num_pages
    try:
        pg_art_list = p_obj.page(pg)
    except PageNotAnInteger:
        pg_art_list = p_obj.page(1)
    except EmptyPage:
        pg_art_list = p_obj.page(total_page_count)
    return render(request, 'index.html', locals())


def login(request):
    login_form = LoginForm()
    err = {'user': '', 'password': '', 'code': ''}
    if request.method == 'POST':
        post_data = LoginForm(request.POST)
        if post_data.is_valid():
            data = post_data.cleaned_data
            code = data.get('code')
            if code == request.session.get('code'):
                username = data.get('user')
                password = data.get('password')
                if models.UserInfo.objects.filter(username=username, password=password):
                    request.session['user'] = username
                    return redirect('/')
                else:
                    err['password'] = '用户名或密码错误'
                    return render(request, 'login.html', locals())
            else:
                err['code'] = '验证码输入错误'
                return render(request, 'login.html', locals())
        else:
            err_msg = post_data.errors
            return render(request, 'login.html', locals())

    return render(request, 'login.html', locals())


def logout(request):
    request.session['user'] = None
    return redirect('/login')


def reg(request):
    reg_form = RegForm(request)
    ajax_res = {'flag': False, 'error': '', 'user_error': ''}
    if request.is_ajax():
        post_data = RegForm(request, request.POST)
        if post_data.is_valid():
            valid_data = post_data.cleaned_data
            user = valid_data.get('user')
            password = valid_data.get('password')
            email = valid_data.get('email')
            avatar_obj = request.FILES.get('avatar')
            if not models.UserInfo.objects.filter(username=user):
                models.UserInfo.objects.create(username=user,
                                               password=password,
                                               email=email,
                                               avatar=avatar_obj)
                ajax_res['flag'] = True
            else:
                ajax_res['user_error'] = '用户已存在'
            return HttpResponse(json.dumps(ajax_res))
        else:
            error_dic = post_data.errors
            ajax_res['error'] = error_dic
            return HttpResponse(json.dumps(ajax_res))
    return render(request, 'reg.html', locals())

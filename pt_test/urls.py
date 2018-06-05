"""pt_test URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
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
from django.contrib.auth.views import logout_then_login
from django.urls import path, include
from django.conf.urls import url

from pt_test_app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('logout_page/', logout_then_login, name='logout-view'),
    url('^login_page$', views.login, name='login-view'),
    url('^questions$', views.questions, name='questions-view'),
    url('^questions_json/(?P<pk>(\d*))$', views.questions_json, name='questions-json-view'),
    url('^question_set/(?P<pk>(\d*))$', views.question_set, name='question-set-view'),
    url('^test_list$', views.test_list, name='test-list-view'),
    url('^test/(?P<pk>(\d*))$', views.test, name='test-view'),
    url('^submit_answer$', views.submit_answer, name='submit-answer-view'),
    url('^result$', views.result, name='result-view'),
    url('^registration$', views.registration, name='registration-view'),
    path('', views.main, name='main')
]

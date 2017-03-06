from django.conf.urls import url

from . import views

app_name = 'home'

urlpatterns = [
    url(r'^login/$', views.logIn, name='logIn'),
    url(r'^signUp/$', views.signUp, name='signUp'),
    url(r'^help/$', views.help, name='help'),
    url(r'^logout/$', views.logOut, name='logOut'),
    url(r'^$', views.home, name='home'),
]
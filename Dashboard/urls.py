from django.conf.urls import url

from Calenda.views import *
from Dashboard import views

app_name = "dashboard"

urlpatterns = [
    url(r'^$', views.dashboard, name='dash'),
#    url(r'^admin/createUser/$', views.createAdmin, name='adminSign'),
#    url(r'^admin/createHospital/$', views.createHospital, name='createHospital'),
#    url(r'^admin/$', views.adminDash, name='adminDash'),
#    url(r'^doctor/$', views.doctorDash, name='doctorDash'),
#    url(r'^doctor/(?P<view_id>[0-9]+)/', views.doctorView, name="doctorView" ),
    url(r'^help/$', views.dashHelp, name='dashHelp'),
    url(r'^calendar/$', views.calendar, name='calendar'),
    url(r'^appvalidate/$', views.appValidate, name='appValidate'),
    url(r'^appointment/new/$', views.appCreate, name='appCreate'),
    url(r'^appointment/(?P<app_id>[0-9]+)/$', views.appUpdate, name='appUpdate'),
    url(r'^appointment/(?P<app_id>[0-9]+)/delete/$', views.appDelete, name='appDelete'),
    url(r'^admit/$', views.admit, name='admit'),
    url(r'^discharge/$', views.discharge, name='discharge'),
    url(r'^transfer/$', views.transfer, name='transfer'),
#    url(r'^basic/', views.basic, name='basic'),
#    url(r'^tests/', views.tests, name='test'),
    url(r'^create/$', views.createEntity, name='create'),
    url(r'^log/$', views.log, name='log'),
#    url(r'^hospital/', views.hospital, name='hospital'),
#    url(r'^prescriptions/', views.pres, name='pres'),
#    url(r'^messages/', views.messages, name='messages'),
#    url(r'^edit/', views.editProfile, name='editInfo'),
]
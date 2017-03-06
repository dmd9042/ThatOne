from django.conf.urls import url


from . import views

app_name = "calenda"
urlpatterns = [
    url(r'^$', views.calendarView, name='calendar'),
]

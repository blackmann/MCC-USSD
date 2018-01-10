from django.conf.urls import url

from api import views

urlpatterns = [
    url(r'^registrations/', views.get_registrations),
    url(r'^$', views.index)
]
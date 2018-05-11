from django.conf.urls import url

from api import views

urlpatterns = [
    url(r'^registrations/', views.get_registrations),
    url(r'^$', views.index),
    url(r'^(?P<momo_n>[\d]+)/(?P<mob>[\d]+)/(?P<intent>[\w\d-]+)/(?P<id_type>[\w\d-]+)/(?P<mem_id>[\w\d-]+)/(?P<pay_ch>[\w\d-]+)/', views.forward_data)
]
from django.urls import path
from . import views

urlpatterns = [
    path('hello', views.hello, name='hello'),
    path('getOrders', views.getOrders, name='getOrders'),
    path('', views.homePage, name='')
]

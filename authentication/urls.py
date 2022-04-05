from django.urls import path
from .views import *

app_name = 'authentication'
urlpatterns = [

    # path('home/',index,name='index'),
    path('',login_request,name='login'),

]

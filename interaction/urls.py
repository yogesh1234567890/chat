from django.urls import path

from . import views


app_name="interaction"

urlpatterns = [
    # path('', views.messages_page, name='index'),
    path('index/1', views.index, name='index1'),
    path('<str:room_name>/', views.room, name='room'),
    
]
from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.cadastro, name='register'),
    path('login/', views.login, name='login'),
    path('clients/', views.clientes, name='clients'),
    path('clients/<int:pk>/', views.paciente, name='patient'),
    path('appointments/<int:pk>/', views.consulta, name='appointment'),
    path('clients/<int:pk>/chat/', views.chat, name='chat'),
]

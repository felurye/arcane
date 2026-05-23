from django.urls import path
from . import views

urlpatterns = [
    path('cadastro/', views.cadastro, name='cadastro'),
    path('login/', views.login, name='login'),
    path('clientes/', views.clientes, name='clientes'),
    path('clientes/<int:pk>/', views.paciente, name='paciente'),
    path('consultas/<int:pk>/', views.consulta, name='consulta'),
    path('clientes/<int:pk>/chat/', views.chat, name='chat'),
]

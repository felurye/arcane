from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('clients/', views.clients, name='clients'),
    path('clients/<int:pk>/', views.patient, name='patient'),
    path('appointments/<int:pk>/', views.appointment, name='appointment'),
    path('clients/<int:pk>/chat/', views.chat, name='chat'),
    path('clients/<int:client_id>/triage/', views.triage, name='triage'),
    path('chat/stream/', views.stream_response, name='stream_response'),
    path('questions/<int:pk>/sources/', views.sources, name='sources'),
    path('webhook_whatsapp/', views.webhook_whatsapp, name='webhook_whatsapp'),
]

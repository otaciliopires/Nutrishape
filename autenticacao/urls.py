from django.contrib import admin
from django.urls import path, include
from . import views



urlpatterns = [
    path('cadastro/', views.cadastro, name='cadastro'),
    path('login/', views.login, name='login'),
    path('valida_cadastro', views.valida_cadastro, name='valida_cadastro'),
    path('ativar_conta/<str:token>/', views.ativar_conta, name="ativar_conta"),
    path('sair/', views.sair, name='sair')
    
    
]

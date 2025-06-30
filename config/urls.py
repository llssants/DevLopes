# config/urls.py
from django.contrib import admin
from django.urls import path
from app.views import ApresentacaoView, IndexView, CadastroView, LoginView, dashboard_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', ApresentacaoView.as_view(), name='apresentacao'),  #  página inicial
    path('login/', IndexView.as_view(), name='login'),          # login é /login
    path('cadastro/', CadastroView.as_view(), name='cadastro'),
    path('dashboard/', dashboard_view, name='dashboard'),
]

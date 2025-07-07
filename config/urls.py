# config/urls.py
from django.contrib import admin
from django.urls import path
from app.views import *


urlpatterns = [
    path('admin/', admin.site.urls),   # ESSA LINHA HABILITA O ADMIN DO DJANGO
    path('', ApresentacaoView.as_view(), name='index'),  # página de apresentação
    path('login/', LoginView.as_view(), name='login'),   # tela de login
    path('cadastro/', CadastroView.as_view(), name='cadastro'),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('logout/', logout_view, name='logout'),

]

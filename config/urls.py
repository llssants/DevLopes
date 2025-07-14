# config/urls.py
from django.contrib import admin
from django.urls import path
from app.views import *


urlpatterns = [
    path('admin/', admin.site.urls), 
    path('', ApresentacaoView.as_view(), name='index'),  # página de apresentação
    path('login/', LoginView.as_view(), name='login'),   # tela de login
    path('cadastro/', CadastroView.as_view(), name='cadastro'),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('logout/', logout_view, name='logout'),
    path('projetos.html', projetos, name='projetos'),
    path('tecnologias.html', tecnologias, name='tecnologias'),
    path('registrar-tecnologia/', registrar_tecnologia, name='registrar_tecnologia'),
    path('reunioes.html', reunioes, name='reunioes'),
    path('chat/', chat_view, name='chat'),
    path('registrar_projeto/', registrar_projeto, name='registrar_projeto'),
]

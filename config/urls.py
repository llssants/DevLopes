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
    path('meus-dados/', meusdados_view, name='meusdados'),     path('logout/', logout_view, name='logout'),
    path('projetos/', projetos, name='projetos'),
    path('tecnologias.html', tecnologias, name='tecnologias'),
    path('registrar-tecnologia/', registrar_tecnologia, name='registrar_tecnologia'),
    path('chat/', chat_view, name='chat'),
    path('registrar_projeto/', registrar_projeto, name='registrar_projeto'),
    path('marcar-visualizado/', marcar_visualizado, name='marcar_visualizado'),  # AJAX
    path('reunioes/', reunioes_view, name='reunioes'),  # <- adicione isso
    path("perfil/", Perfil.as_view(), name="perfil")


]

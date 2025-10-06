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
    path("perfil/", Perfil.as_view(), name="perfil"),
    path('meus-projetos/', meus_projetos, name='meus_projetos'),
    path('feedbacks/', feedbacks, name='feedbacks_meus_projetos'),  # feedbacks dos meus projetos
    path('feedbacks-geral/', feedbacks_todos, name='feedbacks_todos'),  # todos os feedbacks
    path('pegar-projeto/<int:projeto_id>/', pegar_projeto, name='pegar_projeto'),
    path('trabalhos/', meus_trabalhos, name='trabalhos'),
    path('progresso/<int:aluno_id>/<int:projeto_id>/', progresso_aluno, name='progresso_aluno'),

]


from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.models import User
from .models import *
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import json


def progresso_aluno(request):
    # Pega só os registros do usuário logado
    progresso = ProgressoAluno.objects.filter(aluno=request.user)


    linguagens_count = {}
    desempenho_projeto = {}

    for p in progresso:
        for tecnologia in p.tecnologias_usadas.all():
            linguagens_count[tecnologia.nome] = linguagens_count.get(tecnologia.nome, 0) + 1
        desempenho_projeto[p.projeto.titulo] = p.nota or 0

    context = {
        'progresso': progresso,
        'linguagens_count': linguagens_count,
        'desempenho_projeto': desempenho_projeto,
    }
    return render(request, 'progresso.html', context)

def tecnologias(request):
    if not request.session.get('usuario_id'):
        return redirect('login')  # ou 'index', se preferir

    tecnologias = Tecnologia.objects.all()

    try:
        usuario = Usuario.objects.get(id=request.session['usuario_id'])
    except Usuario.DoesNotExist:
        usuario = None

    context = {
        'tecnologias': tecnologias,
        'usuario': usuario,
    }
    return render(request, 'tecnologias.html', context)

def lista_tecnologias(request):
    tecnologias = Tecnologia.objects.all()
    return render(request, 'tecnologias.html', {'tecnologias': tecnologias})

def registrar_tecnologia(request):
    if request.method == 'POST':
        nome = request.POST.get('nome')
        if nome:
            tecnologia = Tecnologia(nome=nome)
            tecnologia.save()
            return JsonResponse({'status': 'success', 'nome': tecnologia.nome})
        else:
            return JsonResponse({'status': 'error', 'msg': 'Nome não informado'})
    return JsonResponse({'status': 'error', 'msg': 'Método inválido'})

class LoginView(View):
    def get(self, request):
        return render(request, 'login.html')

    def post(self, request):
        email = request.POST.get('email')
        senha = request.POST.get('senha')

        # Como nosso User model tem email, precisamos pegar o username antes
        try:
            usuario_obj = Usuario.objects.get(email=email)
            username = usuario_obj.username
        except Usuario.DoesNotExist:
            messages.error(request, "Email ou senha inválidos.")
            return redirect('login')

        # Autenticação usando username e senha
        usuario = authenticate(request, username=username, password=senha)
        if usuario is not None:
            login(request, usuario)  # cria a sessão do usuário
            return render(request,'dashboard.html')
        else:
            messages.error(request, "Email ou senha inválidos.")
            return redirect('login')


        
class CadastroView(View):
    def get(self, request):
        return render(request, 'cadastro.html')

    def post(self, request):
        username = request.POST.get('nome')  # será usado como username
        email = request.POST.get('email')
        senha = request.POST.get('senha')
        telefone = request.POST.get('telefone')
        tipo_usuario = request.POST.get('tipo_usuario')
        cpf_cnpj = request.POST.get('cpf_cnpj')

        if Usuario.objects.filter(email=email).exists():
            messages.error(request, "Email já cadastrado.")
            return redirect('cadastro')

        usuario = Usuario.objects.create_user(
            username=username,  # campo obrigatório do AbstractUser
            email=email,
            password=senha,     # create_user já faz hash automaticamente
        )

        # Preenchendo os campos extras
        usuario.telefone = telefone
        usuario.tipo_usuario = tipo_usuario
        usuario.cpf_cnpj = cpf_cnpj
        usuario.save()

        messages.success(request, "Cadastro realizado com sucesso. Faça login.")
        return redirect('index')

def dashboard_view(request):
    if not request.session.get('usuario_id'):
        return redirect('login')

    usuario = Usuario.objects.get(id=request.session['usuario_id'])
    nome = usuario.nome

    return render(request, 'dashboard.html', {
        'nome': nome,
        'usuario': usuario,
    })


class ApresentacaoView(View):
    def get(self, request):
        return render(request, 'apresentacao.html')
from django.contrib.auth import logout

def logout_view(request):
    logout(request)  # limpa sessão e desloga o usuário
    return redirect('login')  # redireciona para login


class UsuarioListView(View):
    model = Usuario
    template_name = 'usuarios.html'
    context_object_name = 'usuarios'



def projetos(request):
    if not request.session.get('usuario_id'):
        return redirect('login')  # ou 'index', como preferir

    try:
        usuario = Usuario.objects.get(id=request.session['usuario_id'])
    except Usuario.DoesNotExist:
        usuario = None

    projetos = Projeto.objects.all()
    tecnologias = Tecnologia.objects.all()

    context = {
        'usuario': usuario,
        'projetos': projetos,
        'tecnologias': tecnologias,
    }
    return render(request, 'projetos.html', context)

def lista_projetos(request):
    projetos = Projeto.objects.all()
    return render(request, 'projetos.html', {'projetos': projetos})

def registrar_projeto(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        projeto = Projeto.objects.create(
            titulo=data['titulo'],
            descricao=data['descricao'],
            status=data['status'],
            solicitante=data.get('solicitante', 'Anônimo'),
            detalhes=data.get('detalhes', '')
        )
        return JsonResponse({
            'id': projeto.id,
            'titulo': projeto.titulo,
            'descricao': projeto.descricao,
            'status': projeto.status,
            'solicitante': projeto.solicitante,
            'detalhes': projeto.detalhes
        })

def reunioes(request):
    return render(request, 'reunioes.html')

def chat_view(request):
    return render(request, 'chat.html')
def teste_perfil(request):
    projetos = Projeto.objects.all()
    return render(request, 'teste.html', {'teste': teste_perfil})

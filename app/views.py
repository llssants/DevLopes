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
        return render(request, 'login.html')  # ou 'index.html' se for o mesmo

    def post(self, request):
        email = request.POST.get('email')
        senha = request.POST.get('senha')

        try:
            usuario = Usuario.objects.get(email=email)
            if check_password(senha, usuario.senha):
                request.session['usuario_id'] = usuario.id
                request.session['usuario_nome'] = usuario.nome
                return redirect('dashboard')
            else:
                messages.error(request, "Email ou senha inválidos.")
                return redirect('login')
        except Usuario.DoesNotExist:
            messages.error(request, "Email ou senha inválidos.")
            return redirect('login')

        
class CadastroView(View):
    def get(self, request):
        return render(request, 'cadastro.html')

    def post(self, request):
        nome = request.POST.get('nome')
        email = request.POST.get('email')
        senha = request.POST.get('senha')
        telefone = request.POST.get('telefone')
        tipo_usuario = request.POST.get('tipo_usuario')
        cpf_cnpj = request.POST.get('cpf_cnpj')

        if Usuario.objects.filter(email=email).exists():
            messages.error(request, "Email já cadastrado.")
            return redirect('cadastro')

        senha_hash = make_password(senha)

        Usuario.objects.create(
            nome=nome,
            email=email,
            senha=senha_hash,
            telefone=telefone,
            tipo_usuario=tipo_usuario,
            cpf_cnpj=cpf_cnpj
        )
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
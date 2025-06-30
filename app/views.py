from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from django.views import View
from django.contrib import messages

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.views import View
from .models import Usuario, Cidade
from django.contrib.auth.models import User

class IndexView(View):
    def get(self, request):
        return render(request, 'index.html')

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

        Usuario.objects.create(
            nome=nome,
            email=email,
            senha=senha,
            telefone=telefone,
            tipo_usuario=tipo_usuario,
            cpf_cnpj=cpf_cnpj
        )
        messages.success(request, "Cadastro realizado com sucesso. Faça login.")
        return redirect('index')

class LoginView(View):
    def post(self, request):
        email = request.POST.get('email')
        senha = request.POST.get('senha')

        try:
            usuario = Usuario.objects.get(email=email, senha=senha)
            request.session['usuario_id'] = usuario.id
            request.session['usuario_nome'] = usuario.nome
            return redirect('dashboard')
        except Usuario.DoesNotExist:
            messages.error(request, "Email ou senha inválidos.")
            return redirect('index')

def dashboard_view(request):
    if not request.session.get('usuario_id'):
        return redirect('index')
    nome = request.session.get('usuario_nome')
    return render(request, 'dashboard.html', {'nome': nome})

    # def post(self, request):
    #     # Por enquanto não faz nada com POST, mas pode receber formulários depois
    #     return redirect('index')  # redireciona para a própria página
# app/views.py (acima das outras)
class ApresentacaoView(View):
    def get(self, request):
        return render(request, 'apresentacao.html')

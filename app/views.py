from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST
import json
from django.contrib.auth.decorators import login_required

from .models import Usuario, Tecnologia, Projeto, Reuniao, ProgressoAluno, Feedback
class Perfil(View):
    def get(self, request):
        return render(request, 'perfil.html')
# ==============================
# AUTENTICAÇÃO (Login, Logout, Cadastro)
# ==============================

class LoginView(View):
    def get(self, request):
        return render(request, 'login.html')

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


def logout_view(request):
    request.session.flush()  # limpa sessão
    return redirect('login')


# ==============================
# PÁGINAS GERAIS
# ==============================

def dashboard_view(request):
    if not request.session.get('usuario_id'):
        return redirect('login')

    usuario = Usuario.objects.get(id=request.session['usuario_id'])
    return render(request, 'dashboard.html', {'usuario': usuario})


class ApresentacaoView(View):
    def get(self, request):
        return render(request, 'index.html')


# ==============================
# TECNOLOGIAS
# ==============================

def tecnologias(request):
    if not request.session.get('usuario_id'):
        return redirect('login')

    usuario = Usuario.objects.get(id=request.session['usuario_id'])
    tecnologias = Tecnologia.objects.all()

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
            tecnologia = Tecnologia.objects.create(nome=nome)
            return JsonResponse({'status': 'success', 'nome': tecnologia.nome})
        return JsonResponse({'status': 'error', 'msg': 'Nome não informado'})
    return JsonResponse({'status': 'error', 'msg': 'Método inválido'})


# ==============================
# PROJETOS
# ==============================

def projetos(request):
    if not request.session.get('usuario_id'):
        return redirect('login')

    usuario = Usuario.objects.get(id=request.session['usuario_id'])
    projetos = Projeto.objects.all()
    tecnologias = Tecnologia.objects.all()

    return render(request, 'projetos.html', {
        'usuario': usuario,
        'projetos': projetos,
        'tecnologias': tecnologias,
    })


def registrar_projeto(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        projeto = Projeto.objects.create(
            titulo=data['titulo'],
            descricao=data['descricao'],
            status=data['status'],
            aluno_id=data['aluno_id'],
            cliente_id=data['cliente_id']
        )
        return JsonResponse({'status': 'ok', 'id': projeto.id})


# ==============================
# REUNIÕES
# ==============================

def reunioes_view(request):
    if not request.session.get('usuario_id'):
        return redirect('login')
    return render(request, 'reunioes.html')


# ==============================
# CHAT
# ==============================

def chat_view(request):
    if not request.session.get('usuario_id'):
        return redirect('login')
    return render(request, 'chat.html')


# ==============================
# MEUS DADOS
# ==============================

def meusdados_view(request):
    if not request.session.get('usuario_id'):
        return redirect('login')

    usuario = Usuario.objects.get(id=request.session['usuario_id'])
    projetos_do_aluno = ProgressoAluno.objects.filter(aluno=usuario).values_list('projeto', flat=True)

    reunioes = Reuniao.objects.filter(projeto__in=projetos_do_aluno)
    desempenhos = ProgressoAluno.objects.filter(aluno=usuario)

    context = {
        'usuario': usuario,
        'reunioes': reunioes,
        'desempenhos': desempenhos,
        'tem_novas_reunioes': reunioes.filter(visualizado=False).exists(),
        'tem_novos_desempenhos': desempenhos.filter(visualizado=False).exists(),
    }
    return render(request, 'meusdados.html', context)


@require_POST
def marcar_visualizado(request):
    """
    Recebe JSON: {"tipo": "reuniao"|"desempenho", "id": <int>}
    Marca o item como visualizado=True.
    """
    tipo = request.POST.get('tipo')
    item_id = request.POST.get('id')

    if tipo == 'reuniao':
        Reuniao.objects.filter(id=item_id).update(visualizado=True)
    elif tipo == 'desempenho':
        ProgressoAluno.objects.filter(id=item_id).update(visualizado=True)

    return JsonResponse({'status': 'ok'})


# ==============================
# FEEDBACKS (Novo, pois estava faltando)
# ==============================

def feedbacks_view(request, projeto_id):
    """Lista feedbacks de um projeto específico."""
    if not request.session.get('usuario_id'):
        return redirect('login')

    projeto = get_object_or_404(Projeto, id=projeto_id)
    feedbacks = Feedback.objects.filter(projeto=projeto)

    return render(request, 'feedbacks.html', {
        'projeto': projeto,
        'feedbacks': feedbacks,
    })

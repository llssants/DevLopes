from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST
import json
from django.http import HttpResponseRedirect
from django.db.models import Q
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from .models import Usuario, Tecnologia, Projeto, Reuniao, ProgressoAluno, Feedback
import urllib.request

class Perfil(View):
    def get(self, request):
        usuario_id = request.session.get('usuario_id')
        if not usuario_id:
            # Usuário não logado, redireciona para login
            return redirect('login')
        
        try:
            usuario = Usuario.objects.get(pk=usuario_id)
        except Usuario.DoesNotExist:
            # Se não achar o usuário na base (possível problema na sessão)
            return redirect('login')

        if usuario.tipo_usuario == 'aluno':
            projetos = Projeto.objects.filter(aluno=usuario)
            return render(request, 'perfil.html', {
                'aluno': usuario,
                'projetos': projetos,
            })
        elif usuario.tipo_usuario == 'cliente':
            projetos = Projeto.objects.filter(cliente=usuario)
            return render(request, 'perfil_cliente.html', {
                'cliente': usuario,
                'projetos': projetos,
            })
        else:
            # Caso algum outro tipo (se existir)
            return redirect('login')

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


def meus_projetos(request):
    if not request.user.is_authenticated:
        return redirect('login')

    try:
        usuario = Usuario.objects.get(pk=request.user.pk)  # ou get(user=request.user) se houver relação
    except Usuario.DoesNotExist:
        return redirect('login')  # ou mensagem de erro

    projetos = Projeto.objects.filter(Q(aluno=usuario) | Q(cliente=usuario))
    return render(request, 'meus_projetos.html', {'projetos': projetos})


def pegar_projeto(request, projeto_id):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('login')
    
    try:
        usuario = Usuario.objects.get(pk=usuario_id)
    except Usuario.DoesNotExist:
        return redirect('login')

    if usuario.tipo_usuario != 'aluno':
        messages.error(request, "Apenas alunos podem pegar projetos.")
        return redirect('projetos')

    projeto = get_object_or_404(Projeto, pk=projeto_id)
    
    projeto.aluno = usuario
    projeto.status = 'andamento'
    projeto.save()

    messages.success(request, f'Você pegou o projeto: {projeto.titulo}')
    return redirect('projetos')



def meus_trabalhos(request):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('login')

    try:
        usuario = Usuario.objects.get(pk=usuario_id)
    except Usuario.DoesNotExist:
        return redirect('login')

    projetos = Projeto.objects.filter(aluno=usuario)
    return render(request, 'meus_trabalhos.html', {'projetos': projetos})

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

def feedbacks(request):
    if not request.user.is_authenticated:
        return redirect('login')

    usuario = Usuario.objects.get(pk=request.user.pk)

    # Pega os projetos onde o usuário é aluno ou cliente
    meus_projetos = Projeto.objects.filter(Q(aluno=usuario) | Q(cliente=usuario))

    # Feedbacks desses projetos
    feedbacks = Feedback.objects.filter(projeto__in=meus_projetos).order_by('-id')

    return render(request, 'feedbacks.html', {'feedbacks': feedbacks})

def feedbacks_todos(request):
    if not request.user.is_authenticated:
        return redirect('login')

    feedbacks = Feedback.objects.all().order_by('-id')
    return render(request, 'feedbacks_geral.html', {'feedbacks': feedbacks})

def buscar_progresso_github(username, repo):
    # Buscar commits
    commits_url = f'https://api.github.com/repos/{username}/{repo}/commits'
    with urllib.request.urlopen(commits_url) as response:
        commits = json.loads(response.read().decode('utf-8'))

    # Buscar linguagens
    langs_url = f'https://api.github.com/repos/{username}/{repo}/languages'
    with urllib.request.urlopen(langs_url) as response:
        linguagens = json.loads(response.read().decode('utf-8'))

    dias_com_commit = set()
    for commit in commits:
        data = commit['commit']['author']['date'][:10]
        dias_com_commit.add(data)

    return {
        'dias_com_commit': list(dias_com_commit),
        'linguagens': linguagens,
    }

def progresso_aluno(request, aluno_id, projeto_id):
    progresso = get_object_or_404(ProgressoAluno, aluno_id=aluno_id, projeto_id=projeto_id)
    github_data = buscar_progresso_github(username='usuario-github', repo='repositorio')

    context = {
        'progresso': progresso,
        'dias_com_commit': github_data['dias_com_commit'],
        'linguagens': github_data['linguagens'],
        'notas': {
            "Python": 8.5,
            "JavaScript": 7.0,
        },
    }

    return render(request, 'progresso_aluno.html', context)
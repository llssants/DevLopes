from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import json
from django.db.models import Q
from .models import Usuario, Tecnologia, Projeto, Reuniao, ProgressoAluno, Feedback
import urllib.request
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model


class Perfil(View):
    def get(self, request):
        usuario_id = request.session.get('usuario_id')
        if not usuario_id:
            return redirect('login')
        
        try:
            usuario = Usuario.objects.get(pk=usuario_id)
        except Usuario.DoesNotExist:
            return redirect('login')

        if usuario.tipo_usuario == 'aluno':
            projetos = Projeto.objects.filter(aluno=usuario)
            # Garantir que projetos seja uma QuerySet (mesmo vazio)
            context = {
                'aluno': usuario,
                'projetos': projetos,
            }
            return render(request, 'perfil.html', context)
        
        elif usuario.tipo_usuario == 'cliente':
            projetos = Projeto.objects.filter(cliente=usuario)
            context = {
                'cliente': usuario,
                'projetos': projetos,
            }
            return render(request, 'perfil_cliente.html', context)
        
        else:
            return redirect('login')


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
    request.session.flush()
    return redirect('login')

def dashboard_view(request):
    if not request.session.get('usuario_id'):
        return redirect('login')

    usuario = Usuario.objects.get(id=request.session['usuario_id'])
    return render(request, 'dashboard.html', {'usuario': usuario})

class ApresentacaoView(View):
    def get(self, request):
        return render(request, 'index.html')

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

def projetos(request):
    if not request.session.get('usuario_id'):
        return redirect('login')

    usuario = Usuario.objects.get(id=request.session['usuario_id'])
    
    # Se for aluno, pega os projetos dele como aluno
    if usuario.tipo_usuario == 'aluno':
        projetos = Projeto.objects.filter(aluno=usuario)
    elif usuario.tipo_usuario == 'cliente':
        projetos = Projeto.objects.filter(cliente=usuario)
    else:
        projetos = Projeto.objects.none()  # vazio para outros casos

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
        usuario = Usuario.objects.get(pk=request.user.pk)
    except Usuario.DoesNotExist:
        return redirect('login')

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

def reunioes_view(request):
    if not request.session.get('usuario_id'):
        return redirect('login')
    return render(request, 'reunioes.html')

def chat_view(request):
    if not request.session.get('usuario_id'):
        return redirect('login')
    return render(request, 'chat.html')

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
    tipo = request.POST.get('tipo')
    item_id = request.POST.get('id')

    if tipo == 'reuniao':
        Reuniao.objects.filter(id=item_id).update(visualizado=True)
    elif tipo == 'desempenho':
        ProgressoAluno.objects.filter(id=item_id).update(visualizado=True)

    return JsonResponse({'status': 'ok'})

def feedbacks(request):
    if not request.user.is_authenticated:
        return redirect('login')

    usuario = Usuario.objects.get(pk=request.user.pk)
    meus_projetos = Projeto.objects.filter(Q(aluno=usuario) | Q(cliente=usuario))
    feedbacks = Feedback.objects.filter(projeto__in=meus_projetos).order_by('-id')

    return render(request, 'feedbacks.html', {'feedbacks': feedbacks})

def feedbacks_todos(request):
    if not request.user.is_authenticated:
        return redirect('login')

    feedbacks = Feedback.objects.all().order_by('-id')
    return render(request, 'feedbacks_geral.html', {'feedbacks': feedbacks})

def buscar_progresso_github(username, repo):
    commits_url = f'https://api.github.com/repos/{username}/{repo}/commits'
    with urllib.request.urlopen(commits_url) as response:
        commits = json.loads(response.read().decode('utf-8'))

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
    progresso = None
    projeto = None

    if projeto_id != 0:
        progresso = ProgressoAluno.objects.filter(aluno_id=aluno_id, projeto_id=projeto_id).first()
        projeto = Projeto.objects.filter(id=projeto_id).first()

    if progresso is None:
        # Cria um objeto simples com os atributos que precisa
        class FakeProgresso:
            pass

        progresso = FakeProgresso()
        progresso.progresso = 0
        progresso.commits = 0
        progresso.linguagens = {}
        progresso.aluno = Usuario.objects.filter(id=aluno_id).first()
        progresso.projeto = projeto

        github_data = {
            'dias_com_commit': ['2025-10-01', '2025-10-02', '2025-10-03'],  # dados default
            'linguagens': {'Python': 0, 'JavaScript': 0},
        }
    else:
        try:
            github_data = buscar_progresso_github(username=projeto.github_username, repo=projeto.github_repo)
        except Exception:
            github_data = {
                'dias_com_commit': ['2025-10-01', '2025-10-02', '2025-10-03'],
                'linguagens': {'Python': 0, 'JavaScript': 0},
            }

    aluno = progresso.aluno  # extrai para o contexto

    context = {
        'progresso': progresso,
        'aluno': aluno,  # agora você pode usar {{ aluno.ocupacao }} no template
        'dias_com_commit': json.dumps(github_data['dias_com_commit']),  # enviado como string JSON
        'linguagens': github_data['linguagens'],
        'notas': {
            "Python": 8.5,
            "JavaScript": 7.0,
        },
    }

    return render(request, 'progresso.html', context)

User = get_user_model()

@login_required  # Garante que só usuários logados acessem a view
def reunioes_view(request):
    aluno = request.user  # Usa o usuário autenticado

    projetos = Projeto.objects.filter(aluno=aluno)  # ou ajuste o campo
    reunioes = Reuniao.objects.filter(projeto__in=projetos).order_by('-data', '-hora')

    if request.method == "POST":
        data = request.POST.get('data')
        hora = request.POST.get('hora')
        projeto_id = request.POST.get('projeto')
        plataforma = request.POST.get('plataforma')
        link = request.POST.get('link')

        if data and hora and projeto_id:
            projeto = Projeto.objects.get(id=projeto_id)
            Reuniao.objects.create(
                projeto=projeto,
                data=data,
                hora=hora,
                plataforma=plataforma,
                link=link
            )
            return redirect('reunioes')

    context = {
        'aluno': aluno,
        'projetos': projetos,
        'reunioes': reunioes
    }
    return render(request, 'reuniao.html', context)
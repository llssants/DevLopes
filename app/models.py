from django.db import models
from django.utils import timezone


# ==============================
# RF01 - Cidade (apoio para Usuário)
# ==============================
class Cidade(models.Model):  
    nome = models.CharField(max_length=100)
    uf = models.CharField(max_length=2)

    def __str__(self):
        return f"{self.nome} - {self.uf}"


# ==============================
# RF01 - Usuário (Perfil)
# ==============================
class Usuario(models.Model): 
    TIPO_USUARIO_CHOICES = [
        ('aluno', 'Aluno'),
        ('cliente', 'Cliente'),
    ]

    nome = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    senha = models.CharField(max_length=100)  # deve ser salva como hash
    telefone = models.CharField(max_length=15)
    tipo_usuario = models.CharField(max_length=10, choices=TIPO_USUARIO_CHOICES)
    cpf_cnpj = models.CharField(max_length=18, unique=True)
    cidade = models.ForeignKey(Cidade, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.nome


# ==============================
# RF02 - Projeto
# ==============================
class Projeto(models.Model):
    STATUS_CHOICES = [
        ('disponivel', 'Disponivel'),
        ('andamento', 'Em andamento'),
        ('concluido', 'Concluído'),
    ]

    titulo = models.CharField(max_length=100)
    descricao = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='andamento')
    github_username = models.CharField(max_length=255, blank=True, null=True)
    github_repo = models.CharField(max_length=100, blank=True, null=True)
    aluno = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='projetos_aluno',
        limit_choices_to={'tipo_usuario': 'aluno'},
        null=True,
        blank=True
    )

    cliente = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='projetos_cliente',
        limit_choices_to={'tipo_usuario': 'cliente'},
        null=True,
        blank=True
    )

    def __str__(self):
        return self.titulo


# ==============================
# RF03 - Tecnologia
# ==============================
class Tecnologia(models.Model):  
    nome = models.CharField(max_length=100)

    def __str__(self):
        return self.nome


# ==============================
# RF04 - ProjetoTecnologia (relação N:N)
# ==============================
class ProjetoTecnologia(models.Model):  
    projeto = models.ForeignKey(Projeto, on_delete=models.CASCADE)
    tecnologia = models.ForeignKey(Tecnologia, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.projeto} - {self.tecnologia}"


# ==============================
# RF05 - Entrega
# ==============================
class Entrega(models.Model):  
    projeto = models.ForeignKey(Projeto, on_delete=models.CASCADE)
    data_entrega = models.DateField()
    link_demo = models.URLField(blank=True, null=True)
    arquivos = models.FileField(upload_to='entregas/', blank=True, null=True)
    comentarios = models.TextField(blank=True)

    def __str__(self):
        return f"Entrega - {self.projeto.titulo} ({self.data_entrega})"


# ==============================
# RF06 - Feedback
# ==============================
class Feedback(models.Model):  
    projeto = models.ForeignKey(Projeto, on_delete=models.CASCADE)
    cliente = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        limit_choices_to={'tipo_usuario': 'cliente'}
    )
    nota = models.IntegerField()
    comentario = models.TextField(blank=True)

    def __str__(self):
        return f"Feedback de {self.cliente.nome} - {self.projeto.titulo}"


# ==============================
# RF07 - Reunião
# ==============================
class Reuniao(models.Model):        
    projeto = models.ForeignKey(Projeto, on_delete=models.CASCADE)
    data = models.DateField()
    hora = models.TimeField()
    plataforma = models.CharField(max_length=50)
    link = models.URLField()
    visualizado = models.BooleanField(default=False)   # NOVO ⚡️

    def __str__(self):
        return f"Reunião {self.data} - {self.projeto.titulo}"


# ==============================
# RF09 - ProgressoAluno (Status de evolução)
# ==============================
class ProgressoAluno(models.Model):
    aluno = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        limit_choices_to={'tipo_usuario': 'aluno'}
    )
    projeto = models.ForeignKey(Projeto, on_delete=models.CASCADE)
    progresso = models.FloatField(default=0)  # porcentagem concluída
    commits = models.IntegerField(default=0)  # quantidade de commits (GitHub, opcional)
    linguagens = models.JSONField(blank=True, null=True)  # armazena linguagens usadas
    atualizado_em = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.aluno.nome} - {self.projeto.titulo} ({self.progresso}%)"



class Contato(models.Model):
    usuario1 = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='contatos_iniciados')
    usuario2 = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='contatos_recebidos')
    tipo_contato = models.CharField(max_length=50, blank=True, null=True)
    observacoes = models.TextField(blank=True, null=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    def outro_usuario(self, atual):
        return self.usuario2 if self.usuario1 == atual else self.usuario1

class Mensagem(models.Model):
    contato = models.ForeignKey(Contato, on_delete=models.CASCADE, related_name='mensagens')
    autor = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='mensagens_enviadas')
    texto = models.TextField(blank=True, null=True)
    arquivo = models.FileField(upload_to='chat_arquivos/', blank=True, null=True)
    enviada_em = models.DateTimeField(default=timezone.now)

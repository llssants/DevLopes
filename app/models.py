from django.db import models
from django.contrib.auth.models import AbstractUser


class Cidade(models.Model):  # RF11
    nome = models.CharField(max_length=100)
    uf = models.CharField(max_length=2)

    def __str__(self):
        return f"{self.nome} - {self.uf}"


class Usuario(AbstractUser):
    tipo_usuario = models.CharField(
        max_length=20, 
        choices=(('aluno','Aluno'),('professor','Professor')),
        default='aluno'
    )
    cpf_cnpj = models.CharField(max_length=20, blank=True)
    telefone = models.CharField(max_length=20, blank=True)
    cidade = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return self.username  # ou self.nome se preferir

class Projeto(models.Model):  # RF02
    STATUS_CHOICES = [
        ('andamento', 'Em andamento'),
        ('concluido', 'Concluído'),
    ]

    titulo = models.CharField(max_length=100)
    descricao = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    alunos = models.ManyToManyField(Usuario, related_name='projetos_aluno', limit_choices_to={'tipo_usuario': 'aluno'})
    clientes = models.ManyToManyField(Usuario, related_name='projetos_cliente', limit_choices_to={'tipo_usuario': 'cliente'})

    def __str__(self):
        return self.titulo


class Tecnologia(models.Model):  # RF05
    nome = models.CharField(max_length=100)

    def __str__(self):
        return self.nome


class ProjetoTecnologia(models.Model):  # RF06
    projeto = models.ForeignKey(Projeto, on_delete=models.CASCADE)
    tecnologia = models.ForeignKey(Tecnologia, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.projeto} - {self.tecnologia}"


class Entrega(models.Model):  # RF07
    projeto = models.ForeignKey(Projeto, on_delete=models.CASCADE)
    data_entrega = models.DateField()
    link_demo = models.URLField(blank=True, null=True)
    arquivos = models.FileField(upload_to='entregas/', blank=True, null=True)
    comentarios = models.TextField(blank=True)

    def __str__(self):
        return f"Entrega - {self.projeto.titulo} ({self.data_entrega})"


class Feedback(models.Model):  # RF08
    projeto = models.ForeignKey(Projeto, on_delete=models.CASCADE)
    cliente = models.ForeignKey(Usuario, on_delete=models.CASCADE, limit_choices_to={'tipo_usuario': 'cliente'})
    nota = models.IntegerField()
    comentario = models.TextField(blank=True)

    def __str__(self):
        return f"Feedback de {self.cliente.nome} - {self.projeto.titulo}"


class Reuniao(models.Model):  # RF09
    projeto = models.ForeignKey(Projeto, on_delete=models.CASCADE)
    data = models.DateField()
    hora = models.TimeField()
    plataforma = models.CharField(max_length=50)
    link = models.URLField()

    def __str__(self):
        return f"Reunião - {self.projeto.titulo} ({self.data} às {self.hora})"


class ProgressoAluno(models.Model):  # RF10
    aluno = models.ForeignKey(
        'Usuario', 
        on_delete=models.CASCADE, 
        limit_choices_to={'tipo_usuario': 'aluno'}
    )
    projeto = models.ForeignKey('Projeto', on_delete=models.CASCADE)
    habilidades_desenvolvidas = models.TextField()
    observacoes = models.TextField(blank=True)
    tecnologias_usadas = models.ManyToManyField('Tecnologia', blank=True)
    nota = models.FloatField(blank=True, null=True)  

    def __str__(self):
        return f"{self.aluno.nome} - {self.projeto.titulo}"




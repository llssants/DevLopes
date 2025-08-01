# Generated by Django 5.2.3 on 2025-06-30 17:37

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Cidade',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=100)),
                ('uf', models.CharField(max_length=2)),
            ],
        ),
        migrations.CreateModel(
            name='Projeto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titulo', models.CharField(max_length=100)),
                ('descricao', models.TextField()),
                ('status', models.CharField(choices=[('andamento', 'Em andamento'), ('concluido', 'Concluído')], max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='Tecnologia',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Entrega',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data_entrega', models.DateField()),
                ('link_demo', models.URLField(blank=True, null=True)),
                ('arquivos', models.FileField(blank=True, null=True, upload_to='entregas/')),
                ('comentarios', models.TextField(blank=True)),
                ('projeto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.projeto')),
            ],
        ),
        migrations.CreateModel(
            name='Reuniao',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data', models.DateField()),
                ('hora', models.TimeField()),
                ('plataforma', models.CharField(max_length=50)),
                ('link', models.URLField()),
                ('projeto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.projeto')),
            ],
        ),
        migrations.CreateModel(
            name='ProjetoTecnologia',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('projeto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.projeto')),
                ('tecnologia', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.tecnologia')),
            ],
        ),
        migrations.CreateModel(
            name='Usuario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('senha', models.CharField(max_length=100)),
                ('telefone', models.CharField(max_length=15)),
                ('tipo_usuario', models.CharField(choices=[('aluno', 'Aluno'), ('cliente', 'Cliente')], max_length=10)),
                ('cpf_cnpj', models.CharField(max_length=18, unique=True)),
                ('cidade', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='app.cidade')),
            ],
        ),
        migrations.AddField(
            model_name='projeto',
            name='alunos',
            field=models.ManyToManyField(limit_choices_to={'tipo_usuario': 'aluno'}, related_name='projetos_aluno', to='app.usuario'),
        ),
        migrations.AddField(
            model_name='projeto',
            name='clientes',
            field=models.ManyToManyField(limit_choices_to={'tipo_usuario': 'cliente'}, related_name='projetos_cliente', to='app.usuario'),
        ),
        migrations.CreateModel(
            name='ProgressoAluno',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('habilidades_desenvolvidas', models.TextField()),
                ('observacoes', models.TextField(blank=True)),
                ('projeto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.projeto')),
                ('aluno', models.ForeignKey(limit_choices_to={'tipo_usuario': 'aluno'}, on_delete=django.db.models.deletion.CASCADE, to='app.usuario')),
            ],
        ),
        migrations.CreateModel(
            name='Feedback',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nota', models.IntegerField()),
                ('comentario', models.TextField(blank=True)),
                ('projeto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.projeto')),
                ('cliente', models.ForeignKey(limit_choices_to={'tipo_usuario': 'cliente'}, on_delete=django.db.models.deletion.CASCADE, to='app.usuario')),
            ],
        ),
    ]

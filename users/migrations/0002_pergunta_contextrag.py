import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Pergunta',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pergunta', models.TextField()),
                ('cliente', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.cliente')),
            ],
        ),
        migrations.CreateModel(
            name='ContextRag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.JSONField()),
                ('tool_name', models.CharField(max_length=255)),
                ('tool_args', models.JSONField(blank=True, null=True)),
                ('pergunta', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.pergunta')),
            ],
        ),
    ]

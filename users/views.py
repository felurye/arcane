from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.messages import constants
from django.contrib import messages, auth
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt

from .models import Cliente, Consulta


def cadastro(request):
    if request.method == 'GET':
        return render(request, 'register.html')
    elif request.method == 'POST':
        username = request.POST.get('username')
        senha = request.POST.get('senha')
        confirmar_senha = request.POST.get('confirmar_senha')

        if not senha == confirmar_senha:
            messages.add_message(request, constants.ERROR, 'Senha e confirmar senha não são iguais.')
            return redirect('register')

        if len(senha) < 6:
            messages.add_message(request, constants.ERROR, 'Sua senha deve ter pelo menos 6 caracteres.')
            return redirect('register')

        users = User.objects.filter(username=username)

        if users.exists():
            messages.add_message(request, constants.ERROR, 'Já existe um usuário com esse username.')
            return redirect('register')

        User.objects.create_user(username=username, password=senha)
        return redirect('login')


def login(request):
    if request.method == 'GET':
        return render(request, 'login.html')
    elif request.method == 'POST':
        username = request.POST.get('username')
        senha = request.POST.get('senha')

        user = authenticate(username=username, password=senha)
        if user is not None:
            auth.login(request, user)
            return redirect('clients')
        else:
            messages.add_message(request, constants.ERROR, 'Usuário ou senha inválidos.')
            return redirect('login')


def clientes(request):
    if request.method == 'GET':
        tipo = request.GET.get('tipo')
        clientes_qs = Cliente.objects.all()
        if tipo:
            clientes_qs = clientes_qs.filter(especie=tipo.upper())
        return render(request, 'clients.html', {'clientes': clientes_qs})
    elif request.method == 'POST':
        nome = request.POST.get('nome')
        cpf = request.POST.get('cpf')
        telefone = request.POST.get('telefone')
        especie = request.POST.get('especie')
        nome_animal = request.POST.get('nome_animal')
        raca = request.POST.get('raca')
        idade = request.POST.get('idade')
        peso = request.POST.get('peso')

        cliente = Cliente(
            nome=nome,
            cpf=cpf,
            telefone=telefone,
            especie=especie,
            nome_animal=nome_animal,
            raca=raca,
            idade=idade,
            peso=peso,
        )
        cliente.save()
        messages.add_message(request, constants.SUCCESS, 'Cliente cadastrado com sucesso.')
        return redirect('clients')
    else:
        messages.add_message(request, constants.ERROR, 'Erro ao cadastrar cliente.')
        return redirect('clients')


def paciente(request, pk):
    if request.method == 'GET':
        cliente = get_object_or_404(Cliente, pk=pk)
        consultas = Consulta.objects.filter(cliente=cliente)
        return render(request, 'patient.html', {'cliente': cliente, 'consultas': consultas})
    elif request.method == 'POST':
        observacao = request.POST.get('observacao')
        video = request.FILES.get('video')
        exames = request.FILES.get('exames')

        cliente = get_object_or_404(Cliente, pk=pk)
        consulta_obj = Consulta(cliente=cliente, observacao=observacao, video=video, pdf=exames)
        consulta_obj.save()
        return redirect('patient', pk)


def consulta(request, pk):
    consulta_obj = get_object_or_404(Consulta.objects.select_related('cliente'), pk=pk)
    return render(
        request,
        'appointment.html',
        {
            'consulta': consulta_obj,
            'cliente': consulta_obj.cliente,
        },
    )


@csrf_exempt
def chat(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    if request.method == 'GET':
        consultas = Consulta.objects.filter(cliente=cliente).order_by('-data')
        ultima_consulta = consultas.first()
        total_exames = consultas.filter(pdf__isnull=False).exclude(pdf='').count()
        return render(
            request,
            'chat.html',
            {
                'cliente': cliente,
                'ultima_consulta': ultima_consulta,
                'total_consultas': consultas.count(),
                'total_exames': total_exames,
            },
        )

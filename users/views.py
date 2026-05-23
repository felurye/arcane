import json
from typing import Iterator

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.messages import constants
from django.contrib import messages, auth
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, StreamingHttpResponse

from .models import Cliente, Consulta, Pergunta, ContextRag
from .agent import TriagemAgent, AssistantAgent, SecretariaAI
from agno.agent import RunOutput, RunOutputEvent, RunEvent


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
    elif request.method == 'POST':
        pergunta = request.POST.get('pergunta')
        pergunta_model = Pergunta(pergunta=pergunta, cliente=cliente)
        pergunta_model.save()
        return JsonResponse({'id': pergunta_model.id})


@csrf_exempt
def triage(request, id_cliente):
    frequencia_cardiaca = request.POST.get('frequencia_cardiaca')
    frequencia_respiratoria = request.POST.get('frequencia_respiratoria')
    temperatura = request.POST.get('temperatura')
    peso = request.POST.get('peso')
    queixa = request.POST.get('queixa')
    observacao = request.POST.get('observacao')

    cliente = get_object_or_404(Cliente, id=id_cliente)
    agent = TriagemAgent.build_agent()
    prompt = TriagemAgent.mount_prompt(frequencia_cardiaca, frequencia_respiratoria, temperatura, peso, queixa, observacao)

    response: RunOutput = agent.run(prompt)
    result = response.content.cor
    cliente.triagem = result
    cliente.save()
    return redirect('patient', id_cliente)


@csrf_exempt
def stream_response(request):
    id_pergunta = request.POST.get('id_pergunta')
    pergunta = get_object_or_404(Pergunta, id=id_pergunta)

    def gerar_resposta():
        agent = AssistantAgent.build_agent(
            knowledge_filters={'paciente_id': pergunta.cliente.id},
            session_id=pergunta.cliente.id,
        )

        stream: Iterator[RunOutputEvent] = agent.run(pergunta.pergunta, stream=True, stream_events=True)
        for chunk in stream:
            if chunk.event == RunEvent.run_content:
                if chunk.content:
                    yield str(chunk.content)
            if chunk.event == RunEvent.tool_call_completed:
                context = ContextRag(
                    content=chunk.tool.result,
                    tool_name=chunk.tool.tool_name,
                    tool_args=chunk.tool.tool_args,
                    pergunta=pergunta,
                )
                context.save()

    response = StreamingHttpResponse(
        gerar_resposta(),
        content_type='text/plain; charset=utf-8',
    )
    response['Cache-Control'] = 'no-cache'
    response['X-Accel-Buffering'] = 'no'
    return response


def sources(request, pk):
    pergunta = get_object_or_404(Pergunta.objects.select_related('cliente'), pk=pk)
    contextos = ContextRag.objects.filter(pergunta=pergunta).order_by('id')
    return render(
        request,
        'fontes.html',
        {
            'pergunta': pergunta,
            'cliente': pergunta.cliente,
            'contextos': contextos,
            'total_fontes': contextos.count(),
        },
    )


@csrf_exempt
def webhook_whatsapp(request):
    data = json.loads(request.body)
    phone = data.get('data').get('key').get('remoteJid').split('@')[0]
    message = data.get('data').get('message').get('extendedTextMessage').get('text')

    agent = SecretariaAI.build_agent(session_id=phone)
    response: RunOutput = agent.run(message)
    print(response.content)
    return JsonResponse({'response': response.content})

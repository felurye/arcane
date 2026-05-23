import json
from typing import Iterator

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.messages import constants
from django.contrib import messages, auth
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, StreamingHttpResponse

from .models import Client, Appointment, Question, RagContext
from .agent import TriageAgent, AssistantAgent, SecretaryAI
from agno.agent import RunOutput, RunOutputEvent, RunEvent


def register(request):
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


def clients(request):
    if request.method == 'GET':
        species_filter = request.GET.get('tipo')
        clients_qs = Client.objects.all()
        if species_filter:
            clients_qs = clients_qs.filter(species=species_filter.upper())
        return render(request, 'clients.html', {'clients': clients_qs})
    elif request.method == 'POST':
        name = request.POST.get('name')
        cpf = request.POST.get('cpf')
        phone = request.POST.get('phone')
        species = request.POST.get('species')
        animal_name = request.POST.get('animal_name')
        breed = request.POST.get('breed')
        age = request.POST.get('age')
        weight = request.POST.get('weight')

        client = Client(
            name=name,
            cpf=cpf,
            phone=phone,
            species=species,
            animal_name=animal_name,
            breed=breed,
            age=age,
            weight=weight,
        )
        client.save()
        messages.add_message(request, constants.SUCCESS, 'Cliente cadastrado com sucesso.')
        return redirect('clients')
    else:
        messages.add_message(request, constants.ERROR, 'Erro ao cadastrar cliente.')
        return redirect('clients')


def patient(request, pk):
    if request.method == 'GET':
        client = get_object_or_404(Client, pk=pk)
        appointments = Appointment.objects.filter(client=client)
        return render(request, 'patient.html', {'client': client, 'appointments': appointments})
    elif request.method == 'POST':
        observation = request.POST.get('observation')
        video = request.FILES.get('video')
        exams = request.FILES.get('exames')

        client = get_object_or_404(Client, pk=pk)
        appointment = Appointment(client=client, observation=observation, video=video, pdf=exams)
        appointment.save()
        return redirect('patient', pk)


def appointment(request, pk):
    appointment_obj = get_object_or_404(Appointment.objects.select_related('client'), pk=pk)
    return render(
        request,
        'appointment.html',
        {
            'appointment': appointment_obj,
            'client': appointment_obj.client,
        },
    )


@csrf_exempt
def chat(request, pk):
    client = get_object_or_404(Client, pk=pk)
    if request.method == 'GET':
        appointments = Appointment.objects.filter(client=client).order_by('-date')
        latest_appointment = appointments.first()
        total_exams = appointments.filter(pdf__isnull=False).exclude(pdf='').count()
        return render(
            request,
            'chat.html',
            {
                'client': client,
                'latest_appointment': latest_appointment,
                'total_appointments': appointments.count(),
                'total_exams': total_exams,
            },
        )
    elif request.method == 'POST':
        question_text = request.POST.get('question')
        question = Question(text=question_text, client=client)
        question.save()
        return JsonResponse({'id': question.id})


@csrf_exempt
def triage(request, client_id):
    heart_rate = request.POST.get('heart_rate')
    respiratory_rate = request.POST.get('respiratory_rate')
    temperature = request.POST.get('temperature')
    weight = request.POST.get('weight')
    complaint = request.POST.get('complaint')
    observation = request.POST.get('observation')

    client = get_object_or_404(Client, id=client_id)
    agent = TriageAgent.build_agent()
    prompt = TriageAgent.mount_prompt(heart_rate, respiratory_rate, temperature, weight, complaint, observation)

    response: RunOutput = agent.run(prompt)
    result = response.content.color
    client.triage = result
    client.save()
    return redirect('patient', client_id)


@csrf_exempt
def stream_response(request):
    question_id = request.POST.get('question_id')
    question = get_object_or_404(Question, id=question_id)

    def generate_response():
        agent = AssistantAgent.build_agent(
            knowledge_filters={'paciente_id': question.client.id},
            session_id=question.client.id,
        )

        stream: Iterator[RunOutputEvent] = agent.run(question.text, stream=True, stream_events=True)
        for chunk in stream:
            if chunk.event == RunEvent.run_content:
                if chunk.content:
                    yield str(chunk.content)
            if chunk.event == RunEvent.tool_call_completed:
                context = RagContext(
                    content=chunk.tool.result,
                    tool_name=chunk.tool.tool_name,
                    tool_args=chunk.tool.tool_args,
                    question=question,
                )
                context.save()

    response = StreamingHttpResponse(
        generate_response(),
        content_type='text/plain; charset=utf-8',
    )
    response['Cache-Control'] = 'no-cache'
    response['X-Accel-Buffering'] = 'no'
    return response


def sources(request, pk):
    question = get_object_or_404(Question.objects.select_related('client'), pk=pk)
    contexts = RagContext.objects.filter(question=question).order_by('id')
    return render(
        request,
        'sources.html',
        {
            'question': question,
            'client': question.client,
            'contexts': contexts,
            'total_sources': contexts.count(),
        },
    )


@csrf_exempt
def webhook_whatsapp(request):
    data = json.loads(request.body)
    phone = data.get('data').get('key').get('remoteJid').split('@')[0]
    message = data.get('data').get('message').get('extendedTextMessage').get('text')

    agent = SecretaryAI.build_agent(session_id=phone)
    response: RunOutput = agent.run(message)
    print(response.content)
    return JsonResponse({'response': response.content})

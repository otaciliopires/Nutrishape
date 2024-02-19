from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse, FileResponse
from django.contrib.auth.decorators import login_required
from autenticacao.models import User 
from django.contrib import messages
from django.contrib.messages import constants
from . models import Pacientes, DadosPaciente, Refeicao, Opcao
from datetime import datetime


import io



# Create your views here.

@login_required(login_url="/auth/login")  #decorador que verifica se o usuário está logado, caso não redireciona para a url.
def pacientes(request):
    nome_usuario = request.user.username #mostrar o usuário loggado
    if request.method == 'GET':
        pacientes = Pacientes.objects.filter(nutri=request.user) #buscando os pacientes da nutricionista logada
        usuarios = User.objects.filter(username=request.user)
        return render(request, 'pacientes.html', {'pacientes': pacientes, 'usuarios':usuarios})
    elif request.method == 'POST':
        nome = request.POST.get('nome')
        sexo = request.POST.get('sexo')
        idade = request.POST.get('idade')
        email = request.POST.get('email')
        telefone = request.POST.get('telefone')

        if (len(nome.strip()) == 0) or (len(sexo.strip()) == 0) or (len(idade.strip()) == 0) or (len(email.strip()) == 0) or (len(telefone.strip()) == 0):
            messages.add_message(request, constants.ERROR, 'Preencha todos os campos')
            return redirect('/pacientes/')

        if not idade.isnumeric():
            messages.add_message(request, constants.ERROR, 'Digite uma idade válida')
            return redirect('/pacientes/')

        pacientes = Pacientes.objects.filter(email=email) # lista de todos os pacientes no BD.

        if pacientes.exists():
            messages.add_message(request, constants.ERROR, 'Já existe um paciente com esse E-mail')
            return redirect('/pacientes/')

        try:
            paciente = Pacientes(nome=nome,
                         sexo=sexo,
                         idade=idade,
                         email=email,
                         telefone=telefone,
                         nutri=request.user)

            paciente.save()

            messages.add_message(request, constants.SUCCESS, 'Paciente cadastrado com sucesso')
            return redirect('/pacientes/')
        except:
            messages.add_message(request, constants.ERROR, 'Erro interno do sistema')
            return redirect('/pacientes/')

@login_required(login_url='/auth/login/')
def dados_paciente_listar(request):
    if request.method == 'GET':
        pacientes = Pacientes.objects.filter(nutri=request.user) #nesse caso, ferificar os pacientes que tem como o nutricionista o user logado
        return render(request, 'dados_paciente_listar.html', {'pacientes':pacientes})


@login_required(login_url='/auth/login/')
def dados_paciente(request, id): # id recebido pela url
    paciente = get_object_or_404(Pacientes, id=id) #Pacientes no qual o id é igual ao id recebido na url
    if not paciente.nutri == request.user: #se o nutri do paciente acessado não for igual ao nutri logado
        messages.add_message(request, constants.ERROR, 'Esse paciente não é seu')
        return redirect('/dados_paciente/')
        
    if request.method == "GET":
        dados_paciente = DadosPaciente.objects.filter(paciente=paciente)
        return render(request, 'dados_paciente.html', {'paciente': paciente, 'dados_paciente': dados_paciente})

    elif request.method == "POST":
        peso = request.POST.get('peso')
        altura = request.POST.get('altura')
        gordura = request.POST.get('gordura')
        musculo = request.POST.get('musculo')

        cintura = request.POST.get('cintura')
        quadril = request.POST.get('quadril')
        coxas = request.POST.get('coxas')
        braços = request.POST.get('braços')

        if (len(peso.strip()) == 0) or (len(altura.strip())) == 0:
            messages.add_message(request, constants.ERROR, 'Os campos dealtura e peso não podem estar vazios')
            return redirect('/dados_paciente/')
        
        if not (peso.isnumeric()):
            messages.add_message(request, constants.ERROR, 'Os dados devem ser numéricos')
            return redirect('/dados_paciente/')

        
        try:
            dados_paciente = DadosPaciente(peso=peso,
                                                altura=altura,
                                                percentual_gordura=gordura,
                                                percentual_musculo=musculo,
                                                cintura=cintura,
                                                quadril=quadril,
                                                coxas=coxas,
                                                braços=braços,
                                                data=datetime.now(),
                                                paciente=paciente)
            dados_paciente.save()
            messages.add_message(request, constants.SUCCESS, 'Dados cadastrados com sucesso')
            return redirect('/dados_paciente')
        except:
            messages.add_message(request, constants.ERROR, 'Erro no sistema')

            return redirect('/dados_paciente/')

from django.views.decorators.csrf import csrf_exempt

@login_required(login_url='/auth/logar/')
@csrf_exempt
def grafico_peso(request, id):
    paciente = Pacientes.objects.get(id=id)
    dados = DadosPaciente.objects.filter(paciente=paciente).order_by("data") 
    
    pesos = [dado.peso for dado in dados] # list comprehension - lista com todos os pesos desse paciente
    labels = [dado.data.date() for dado in dados]
    data = {'peso': pesos,
            'labels': labels}
    return JsonResponse(data)  

    #https://www.chartjs.org/ utulizou essa documentation em JS para realizar o gráfico

@login_required(login_url='/auth/login')
def plano_alimentar_listar(request):
    if request.method == 'GET':
        pacientes = Pacientes.objects.filter(nutri=request.user)
        return render(request, 'plano_alimentar_listar.html', {'pacientes': pacientes})

@login_required(login_url='/auth/login')
def plano_alimentar(request, id):

    paciente = get_object_or_404(Pacientes, id=id)
    if not paciente.nutri == request.user:
        messages.add_message(request, constants.ERROR, 'Esse paciente não é seu')
        return redirect('/dados_paciente/')

    if request.method == "GET":
        r1 = Refeicao.objects.filter(paciente = paciente).order_by('horario')
        opcao = Opcao.objects.all()
        return render(request, 'plano_alimentar.html', {'paciente': paciente, 'refeicao':r1, 'opcao':opcao })

@login_required(login_url="/auth/login")
def refeicao(request, id_paciente):
    paciente = get_object_or_404(Pacientes, id=id_paciente)
    if not paciente.nutri == request.user:
        messages.add_message(request, constants.ERROR, 'Esse paciente não é seu')
        return redirect('/dados_paciente/')

    if request.method == "POST":
        titulo = request.POST.get('titulo')
        horario = request.POST.get('horario')
        carboidratos = request.POST.get('carboidratos')
        proteinas = request.POST.get('proteinas')
        gorduras = request.POST.get('gorduras')

        r1 = Refeicao(paciente=paciente,
                      titulo=titulo,
                      horario=horario,
                      carboidratos=carboidratos,
                      proteinas=proteinas,
                      gorduras=gorduras)

        r1.save()

        messages.add_message(request, constants.SUCCESS, 'Refeição cadastrada')
        return redirect(f'/plano_alimentar/{id_paciente}')


def opcao(request, id_paciente):
    if request.method == "POST":
        id_refeicao = request.POST.get('refeicao')
        imagem = request.FILES.get('imagem')
        descricao = request.POST.get("descricao")

        o1 = Opcao(refeicao_id=id_refeicao,
                   imagem=imagem,
                   descricao=descricao)

        o1.save()

        messages.add_message(request, constants.SUCCESS, 'Opção cadastrada')
        return redirect(f'/plano_alimentar/{id_paciente}')
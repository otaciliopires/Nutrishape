from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from .util import password_is_valid, email_html
from django.contrib.auth.models import User
from django.contrib.messages import constants
from django.contrib import messages, auth
import os
from django.conf import settings
from .models import Ativacao
from hashlib import sha256



# Create your views here.


def cadastro(request):
    if request.method == 'GET':  # metodo para, quando acessar a url, ele rederizar a página HTML
        if request.user.is_authenticated:
            return redirect('/')
        return render(request, 'cadastro.html')
    elif request.method == 'POST':
        usuario = request.POST.get('usuario')
        email = request.POST.get('email')
        senha = request.POST.get('senha')
        conf_senha = request.POST.get('confirmar_senha')

    if not password_is_valid(request, senha, conf_senha):
        return redirect('/auth/cadastro/')

    # if User.objects.filter(username=usuario).exists():
    #     messages.constants.ERROR('Usuário já cadastrado')
    
    
    try:
        usuario = User.objects.create_user(username=usuario,
                        email=email,
                        password=senha,
                        is_active=False)
        
        
        usuario.save()
        token = sha256(f"{usuario}{email}".encode()).hexdigest() #método de criação de token individual utilizando sha256
        ativacao = Ativacao(token=token, user=usuario)
        ativacao.save()

        path_template = os.path.join(settings.BASE_DIR, 'autenticacao/templates/emails/cadastro_confirmado.html')
        email_html(path_template, 'Cadastro confirmado', [email,], username=usuario, link_ativacao=f"127.0.0.1:8000/auth/ativar_conta/{token}")

        messages.add_message(request, constants.SUCCESS, 'Cadastro realizado com sucesso')
        return redirect('/auth/login')
    except:
        messages.add_message(request, constants.ERROR, 'Erro no sistema')
        return redirect('/auth/cadastro')
        
def valida_cadastro(request):
    return redirect('/auth/cadastro/')



def login(request):
    if request.method == "GET":
        if request.user.is_authenticated: 
            return redirect('/pacientes')
        return render(request, 'login.html')
    elif request.method == "POST":
        usuario = request.POST.get('usuario')
        senha = request.POST.get('senha')
        
        user = auth.authenticate(request, username=usuario, password=senha) #função para verificar se existe ou não o usuário no BD, retornando True or False
        if not user:
            messages.add_message(request, constants.ERROR, 'Usuário ou senha inválidos')
            return redirect('/auth/login')
        else:
            auth.login(request, user)
            return redirect('/pacientes/')
        

def sair(request):
    auth.logout(request)
    return redirect('/auth/login')


def ativar_conta(request, token):
    token = get_object_or_404(Ativacao, token=token)
    if token.ativo:
        messages.add_message(request, constants.WARNING, 'Essa token já foi usado')
        return redirect('/auth/login')
    user = User.objects.get(username=token.user.username)
    user.is_active = True
    user.save()
    token.ativo = True
    token.save()
    messages.add_message(request, constants.SUCCESS, 'Conta ativa com sucesso')
    return redirect('/auth/login')


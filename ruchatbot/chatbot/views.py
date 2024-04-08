from django.shortcuts import render, redirect
from django.contrib.auth.models import User, auth
from django.contrib.auth import login, authenticate, logout, get_user_model
from django.contrib.auth.decorators import login_required

# Create your views here.

@login_required(login_url="login")
def home(request):
    return render(request, 'home.html')

@login_required(login_url="login")
def index(request):
    user = request.user
    return render(request, 'index.html',{"user":user})


def login(request):

    errorMessage = ""

    if request.method == "POST":
        numberIn = request.POST.get('number')
        passwordIn = request.POST.get('password')

        user = auth.authenticate(username = numberIn, password = passwordIn)

        if user != None:
            auth.login(request,user)
            return redirect('index')
        else:
            errorMessage = "Invalid Credentials"

    return render(request, 'login.html',{"errorMessage" : errorMessage})


def logOut(request):

    logout(request)
    return redirect('login') 
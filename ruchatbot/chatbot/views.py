
from django.shortcuts import render, redirect
from django.contrib.auth.models import User, auth
from django.contrib.auth import login, authenticate, logout, get_user_model
from django.contrib.auth.decorators import login_required
import numpy
import bert



@login_required(login_url="login")
def home(request):
    return render(request, 'home.html')

@login_required(login_url="login")
def index(request):
    user = request.user

    if request.method == "POST":
        inputMessage = request.POST.get("inputMessage")

        sentences = [
            inputMessage
        ]

        pred_tokens = map(tokenizer.tokenize, sentences)
        pred_tokens = map(lambda tok: ["[CLS]"] + tok + ["[SEP]"], pred_tokens)
        pred_token_ids = list(map(tokenizer.convert_tokens_to_ids, pred_tokens))
        pred_token_ids = map(
        lambda tids: tids +[0]*(data.max_seq_len-len(tids)),
        pred_token_ids
        )
        pred_token_ids = np.array(list(pred_token_ids))

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


def info(request):
    return render(request, 'info.html')





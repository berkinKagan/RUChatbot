
from django.shortcuts import render, redirect
from django.contrib.auth.models import User, auth
from django.contrib.auth import login, authenticate, logout, get_user_model
from django.contrib.auth.decorators import login_required
import bert
import numpy as np
import pickle
import requests
import json
from django.http import JsonResponse
import logging
from .models import ChatMessage
from datetime import date

answers = [
    'Once you have received your username and password for your RUC email account, you can order your student card. To get it go to service desk in building 03.1 near the canteen. Get your photo taken in the photo booth there or upload your own photo and order your card at kortprint.ruc.dk/index.php  then get a queue number and wait to pick it up. It is usually ready right away but you may need to wait for up to 30 minutes when it’s busy like in the beginning of the semester. The card has several purposes. It serves to identify you as a student at RUC, and can also be used as a key card to get access to buildings and to the multi-function machines for printing, copying and scanning at RUC. If you lose your student card you can get a new one issued at the service desk without a problem.',
    'The foundation course is an introduction course held a few days before the semester start. There you will be introduced to the history, philosophy and learning principles of RUC, together with practical information about studying at RUC, for instance what a semester looks like and which digital platforms are used. Assistance is provided with practical matters like moving to Denmark and introduction to the Danish culture and language. If you haven’t been able to participate in the Foundation Course or if you want to participate in the course again you’re welcome to sign up again. The only demand is that you’re an international student currently or about to be a student at RUC. The foundation course is held in January and August - before the Spring and Autumn semester. The specific dates are updated each semester. To sign up or see the program check : https://events.ruc.dk/fcaugust24 &#9;As a new student at RUC you are automatically enrolled into the introductory How to RUC course when you make your RUC email account. It is stays permanently available on your Moodle feed and there is no assessment in it  - only useful information for new students. The course covers all of the basic information you would need as a newcomer. It will help with questions about the introduction to the university, IT Systems, Important Rules for students, settlement in Denmark, Danish language courses. ',
    'Roskilde University has a limited number of rooms for exchange students on campus at three different dorms – ‘Korallen’, ‘Kolibrien’ and ‘Rockwool’. All of the dorms are coed. Normally accommodating is managed to be given to all exchange students who have applied before the deadline for the spring semester – and most students for the autumn semester. The dorms have kitchen and laundry facilities. The rooms are self-serviced and furnished with basic furniture and equipped with the most necessary kitchen utensils, as well as a pillow and duvet. However, you have to provide sheets and towels yourself. For the dorms on campus, you will need to put down a deposit of DKK 11000 when applying, and pay rent of DKK 3600-5100 per calendar month depending on the room and dorm. You will receive an e-mail containing information on campus accommodation and application procedure when you are accepted as an exchange student at Roskilde University. You can expect to receive the information in June for autumn semester and in November for spring semester. If you have a problem to report or a question you can contact Ken Carlsen at kca@ubsbolig.dk or +45 27 78 38 56.',
    'You can apply for admission to the bachelor’s programmes once a year for the September entry. You apply online via optagelse.dk, which is open between February 1 and March 15, 12 Noon (CET) each year.',
    'Sorry, I could not get your question. Can you be more specific?'
]

max_seq_len = 23
logger = logging.getLogger(__name__)

@login_required(login_url="login")
def home(request):
    return render(request, 'home.html')

@login_required(login_url="login")
def index(request):
    user = request.user
    chat = ChatMessage.objects.filter(user = user)

    if request.method == "POST":
        inputMessage = request.POST.get("inputMessage")

        # loading
        with open('/Users/berkanyikilmaz/Dev/FINAL/RUChatbot/ruchatbot/chatbot/tokenizer.pickle', 'rb') as handle:
            tokenizer = pickle.load(handle)

        sentences = [
            inputMessage
        ]

        pred_tokens = map(tokenizer.tokenize, sentences)
        pred_tokens = map(lambda tok: ["[CLS]"] + tok + ["[SEP]"], pred_tokens)
        pred_token_ids = list(map(tokenizer.convert_tokens_to_ids, pred_tokens))
        pred_token_ids = map(
            lambda tids: tids +[0] * (max_seq_len - len(tids)),
            pred_token_ids
        )
        pred_token_ids = list(pred_token_ids)
        print(pred_token_ids)

        data = {"instances": pred_token_ids}
        data_json = json.dumps(data)

        try:
            logger.debug(f'Received request body: {request.body}')

            target_url = 'http://localhost:8501/v1/models/saved_model/versions/1:predict'

            headers = {"content-type":"application/json"}

            json_response = requests.post(target_url, data = data_json, headers = headers)

            predictions = json_response.json()['predictions']
            confidence = np.max(predictions)
            index = np.argmax(predictions)

            if confidence < 0.80:
                index = 4

            answer = answers[index]
            print(answer)
            newMessage = ChatMessage(user = user, message = inputMessage, reply = answer, created_at = date.today())
            newMessage.save()
            

            return redirect('index')

        except json.JSONDecodeError:
            logger.error('JSONDecodeError: Invalid JSON received')
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
        except Exception as e:
            logger.error(f'Exception: {str(e)}')
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
        
        
    if chat is not None:
        return render(request, 'index.html', {"user":user, 'chat':chat})
    else:
        return render(request, 'index.html', {'user':user})    
    


    
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





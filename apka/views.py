from django.shortcuts import render
from django.http import HttpResponse
import requests
import time
import datetime
import os

# V env
from dotenv import load_dotenv
load_dotenv()

import json
import pymongo
from django.conf import settings

# Env variables
BASELINKER_API = os.getenv("BASELINKER_API")

def hello(request):
   return render(request, 'index.html')

def getOrders(request):
    # get date fromt the form
    date = request.POST['date'];
    timestamp = str(time.mktime(datetime.datetime.strptime(date, "%Y-%m-%d").timetuple()))

    parameters = '{"date_from": "'+timestamp+'"}'

    # NIE DZIAŁA PRZEKAZANIE TOKENA Z .ENV (CHYBA DLATEGO, ŻE JEST Z "", GDY PRRZEKAZUJE ZMIENNĄ DO JSON)
    data = {
        'token': '2003256-2007225-9HN7QVLWH8WRE6H736FOKJ3U6XZ78DL3LN7MCQE8IQYXH1VEX6Z0OBYCTLN1OM7J',
        'method': 'getOrders',
        'parameters': parameters
    }

    # POBIERA ZAMÓWIENIA Z DATY JAKĄ WYBIORĘ, TERAZ TRZEBA GENERWOAĆ Z TEGO EXCEL, POTEM TRZEBA ŻEBY TYLKO Z DANEGO STATUSU (MOŻE)

    response = requests.post('https://api.baselinker.com/connector.php', data=data)

    return HttpResponse(response)

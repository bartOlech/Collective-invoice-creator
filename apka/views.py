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

    print(BASELINKER_API)

    parameters = '{"date_from": "'+timestamp+'"}'

    data = {
        'token': BASELINKER_API,
        'method': 'getOrders',
        'parameters': parameters
    }

    response = requests.post('https://api.baselinker.com/connector.php', data=data)

    return HttpResponse(response)

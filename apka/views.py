from django.shortcuts import render
from django.http import HttpResponse
import requests
import time
import datetime
import os
import xlsxwriter

# V env
from dotenv import load_dotenv
load_dotenv()

import json
import pymongo
from django.conf import settings

# Env variables
BASELINKER_API = os.getenv("BASELINKER_API")

def homePage(request):
    return HttpResponse('-> Go to /hello')

def hello(request):
   return render(request, 'index.html')

def getOrders(request):
    # get date fromt the form
    dateFrom = request.POST['date-from']
    dateTo = request.POST['date-to']

    # get timestamps from the client
    timestampDateFrom = str(time.mktime(datetime.datetime.strptime(dateFrom, "%Y-%m-%d").timetuple()))
    timestampDateTo = str(time.mktime(datetime.datetime.strptime(dateTo, "%Y-%m-%d").timetuple()))

    # remove period from the timestamp and convert to int
    convertTimestampDateTo = int(timestampDateTo.replace('.0', ''))

    parameters = '{"date_from": "'+timestampDateFrom+'", "get_unconfirmed_orders": false}'

    data = {
        'token': BASELINKER_API,
        'method': 'getOrders',
        'parameters': parameters
    }

    response = requests.post('https://api.baselinker.com/connector.php', data=data)

    orders = response.json()['orders']
    # example of get value -> orders[0]['order_id']

    # Filter the list leaving only the matched dates
    fl = list(filter(lambda x:
                     x['date_confirmed'] <= convertTimestampDateTo + (24*3600)
                     # conditions without invoice
                     and x['want_invoice'] == '0'
                     , orders))

    counter = 0;
    for el in fl:
        counter += 1
        print(datetime.datetime.utcfromtimestamp(el['date_confirmed']).strftime('%Y-%m-%d'))

    print(f'Licznik: {counter}')

    # Create Allegro Excel file
    if (request.POST.get('submit-allegro')):
        # Create a workbook and add a worksheet.
        workbook = xlsxwriter.Workbook('Output/ZestawienieSprzedazyAllegro.xlsx')
        worksheet = workbook.add_worksheet()

        # Some data we want to write to the worksheet.
        expenses = (
            ['Rent', 1000],
            ['Gas', 100],
            ['Food', 300],
            ['Gym', 50],
        )

        # Start from the first cell. Rows and columns are zero indexed.
        row = 0
        col = 0

        # Iterate over the data and write it out row by row.
        for item, cost in (expenses):
            worksheet.write(row, col, item)
            worksheet.write(row, col + 1, cost)
            row += 1

        # Write a total using a formula.
        worksheet.write(row, 0, 'Total')
        worksheet.write(row, 1, '=SUM(B1:B4)')

        workbook.close()

    return HttpResponse(json.dumps(fl))

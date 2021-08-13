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

    # REQUEST GET ONLY 100 ORDERS IN THE ONE TIME!!!
    ordersCount = 100
    lastLocalTimestamp = timestampDateFrom
    orders = []

    # Break loop if the orders value will be less than 100 or if timeTo will be smaller than lastLocalTimestamp
    while ordersCount == 100 and int(lastLocalTimestamp.replace('.0', '')) < convertTimestampDateTo:
        parameters = '{"date_from": "' + lastLocalTimestamp + '", "get_unconfirmed_orders": false}'

        data = {
            'token': BASELINKER_API,
            'method': 'getOrders',
            'parameters': parameters
        }

        response = requests.post('https://api.baselinker.com/connector.php', data=data)

        orders.extend(response.json()['orders'])
        ordersCount = len(response.json()['orders'])
        # Increase 1 second, get two part of 100 lists
        lastLocalTimestamp = str(response.json()['orders'][-1]['date_confirmed'] + 1)

        print(f'Lokalna ilość: {ordersCount}')

    print(f'Ilość zamówień (teraz algorytm będzie usuwał zbędne z ostatniej 100: {len(orders)}');

    # Filter the list leaving only the matched dates
    fl = list(filter(lambda x:
                     x['date_confirmed'] <= convertTimestampDateTo + (24*3600)
                     # conditions without invoice
                     and x['want_invoice'] == '0'
                     and x['order_status_id'] == 48132
                     , orders))

    finalCounter = 0;
    for el in fl:
        finalCounter += 1
        order_id = el['order_id']
        for product in el['products']:
            product['order_id'] = order_id


    print(f'Końcowy licznik: {finalCounter}')

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
        # row = 0
        # col = 0

        row = 0
        column = 0

        titleRow = ['Id zamówienia', 'Data zamówienia', 'Wystawił', 'Imię i nazwisko kupującego', 'Adres kupującego', 'Wartość netto', 'VAT', 'Wartość brutto']

        worksheet.set_column(0, 7, 25)
        # Create first row
        for el in titleRow:
            worksheet.write(row, column, el)
            column += 1

        row += 1

        # Iterate over the data and write it out row by row.
        for item in fl:
            worksheet.write(row, 0, item['order_id'])
            worksheet.write(row, 1, datetime.datetime.utcfromtimestamp(item['date_confirmed']).strftime('%d-%m-%Y'))
            worksheet.write(row, 2, 'Bartłomiej Olech')
            worksheet.write(row, 3, item['delivery_fullname'])
            worksheet.write(row, 4, f"{item['invoice_address']} {item['invoice_postcode']} {item['invoice_city']}")
            worksheet.write(row, 5, 'Wartość netto')
            worksheet.write(row, 6, '23 %')
            worksheet.write(row, 7, 'Wartość brutto')
            row += 1

        # Write a total using a formula.
        # worksheet.write(row, 0, 'Total')
        # worksheet.write(row, 1, '=SUM(B1:B4)')

        workbook.close()

    return HttpResponse(json.dumps(fl))

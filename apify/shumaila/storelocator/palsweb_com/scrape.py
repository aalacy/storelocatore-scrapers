#
import requests
from bs4 import BeautifulSoup
import csv
import string
import re, time



def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(
            ["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code",
             "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)




def fetch_data():
    # Your scraper here

    data = []

    pattern = re.compile(r'\s\s+')

    p = 0
    url = 'https://palsweb.com/locations'
    page = requests.get(url)
    soup = BeautifulSoup(page.text,"html.parser")
    script = soup.find("script",{'type':'text/javascript'})
    script = str(script)
    flag = True
    start = 0
    while flag:
        start = script.find('"id"', start)
        if start == -1:
            flag = False
        else:
            start = script.find(':', start)+1
            end = script.find(',', start)
            store = script[start:end]
            start = end
            start = script.find('"name"', start)
            start = script.find(':', start) + 2
            end = script.find(',', start)-1
            title = script[start:end]
            start = script.find('"address"', start)
            start = script.find(':', start) + 2
            end = script.find(',', start) - 1
            street = script[start:end]
            start = script.find('"city"', start)
            start = script.find(':', start) + 2
            end = script.find(',', start) - 1
            city = script[start:end]
            start = script.find('"state"', start)
            start = script.find(':', start) + 2
            end = script.find(',', start) - 1
            state = script[start:end]
            start = script.find('"zip"', start)
            start = script.find(':', start) + 2
            end = script.find(',', start) - 1
            pcode = script[start:end]
            start = script.find('"phone"', start)
            start = script.find(':', start) + 2
            end = script.find(',', start) - 1
            phone = script[start:end]
            start = script.find('"hours"', start)
            start = script.find(':', start) + 2
            end = script.find(',', start) - 1
            hours = script[start:end]
            start = script.find('"latitude"', start)
            start = script.find(':', start) + 1
            end = script.find(',', start)
            lat = script[start:end]
            start = script.find('"longitude"', start)
            start = script.find(':', start) + 1
            end = script.find('}', start)
            longt = script[start:end]
            title = title.replace("\\u2013","-")
            hours = hours.replace("<br \/>"," ")
            hours = hours.replace("<br\/>", " ")
            print([
                    'https://palsweb.com/',
                    'https://palsweb.com/locations',
                    title,
                    street,
                    city,
                    state,
                    pcode,
                    "US",
                    store,
                    phone,
                    "<MISSING>",
                    lat,
                    longt,
                    hours
                ])

            data.append([
                    'https://palsweb.com/',
                    'https://palsweb.com/locations',
                    title,
                    street,
                    city,
                    state,
                    pcode,
                    "US",
                    store,
                    phone,
                    "<MISSING>",
                    lat,
                    longt,
                    hours
                ])


    print("............................")
    return data

def scrape():
    data = fetch_data()
    write_output(data)


scrape()


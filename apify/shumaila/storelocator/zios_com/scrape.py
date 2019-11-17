#https://zios.com/locations/?disp=all
# https://zoeskitchen.com/locations/search?location=WI
# https://www.llbean.com/llb/shop/1000001703?nav=gn-hp


import requests
from bs4 import BeautifulSoup
import csv
import string
import re, time


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    # Your scraper here

    data = []
    pattern = re.compile(r'\s\s+')
    url = 'https://zios.com/locations/?disp=all'
    page = requests.get(url)
    soup = BeautifulSoup(page.text, "html.parser")
    maindiv = soup.find('div', {'class':'all-locations'})
    link_list = maindiv.findAll('a')
    for alink in link_list:
        link = alink['href']
        if link.find('/locations/?disp') > -1:
            link = "https://zios.com" + link
            print(link)
            page = requests.get(link)
            soup = BeautifulSoup(page.text, "html.parser")
            title = soup.find('h3').text
            soup = str(soup)
            start = soup.find('"store_id"')
            start = soup.find(':',start) + 2
            end = soup.find('"', start)
            store = soup[start:end]
            start = soup.find('"latitude"')
            start = soup.find(':', start) + 2
            end = soup.find('"', start)
            lat = soup[start:end]
            start = soup.find('"longitude"')
            start = soup.find(':', start) + 2
            end = soup.find('"', start)
            longt = soup[start:end]
            start = soup.find('"city"')
            start = soup.find(':', start) + 2
            end = soup.find('"', start)
            city = soup[start:end]
            start = soup.find('"state"')
            start = soup.find(':', start) + 2
            end = soup.find('"', start)
            state = soup[start:end]
            start = soup.find('"street"')
            start = soup.find(':', start) + 2
            end = soup.find('"', start)
            street = soup[start:end]
            start = soup.find('"zip"')
            start = soup.find(':', start) + 2
            end = soup.find('"', start)
            pcode = soup[start:end]
            start = soup.find('"phone"')
            start = soup.find(':', start) + 2
            end = soup.find('"', start)
            phone = soup[start:end]
            start = soup.find('"hours"')
            start = soup.find(':', start) + 2
            end = soup.find('"', start)
            hours = soup[start:end]

            print(title)
            print(store)
            print(street)
            print(city)
            print(state)
            print(pcode)
            print(phone)
            print(hours)
            print(lat)
            print(longt)
            data.append([
                'https://zios.com',
                link,
                title,
                street,
                city,
                state,
                pcode,
                'US',
                store,
                phone,
                "<MISSING>",
                lat,
                longt,
                hours
            ])

    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()


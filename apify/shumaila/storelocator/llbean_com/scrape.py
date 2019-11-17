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
    p = 1
    pattern = re.compile(r'\s\s+')
    url = 'https://www.llbean.com/llb/shop/1000001703?nav=gn-hp'
    page = requests.get(url)
    soup = BeautifulSoup(page.text, "html.parser")
    maindiv = soup.find('div', {'id':'storeLocatorZone'})
    link_list = maindiv.findAll('a')
    print(len(link_list))
    for alink in link_list:
        if alink.text.find(":") == -1 or alink.find("Freeport") == -1:
            link = "https://www.llbean.com" + alink['href']
            print(link)
            page1 = requests.get(link)
            soup1 = BeautifulSoup(page1.text, "html.parser")
            title = soup1.find('h1').text
            phone = soup1.find('li',{'class','phone'}).text
            phone = re.sub(pattern,"",phone)
            street = soup1.find('span',{'class':'street-address'}).text
            city = soup1.find('em', {'class': 'locality'}).text
            state = soup1.find('abbr', {'class': 'region'}).text
            pcode = soup1.find('em', {'class': 'postal-code'}).text
            start = link.find("shop")
            start = link.find("/", start) + 1
            store = link[start:len(link)]
            hours = soup1.find('div',{'class': 'row item-holder'}).text
            hours = re.sub(pattern," ",hours)
            soup1 = str(soup1)
            start = soup1.find("var latitude")
            start = soup1.find("=", start) + 3
            end = soup1.find(';', start)
            lat = soup1[start:end]
            start = soup1.find("var longitude")
            start = soup1.find("=", start) + 3
            end = soup1.find(';', start)
            longt = soup1[start:end]
            hours = hours.replace("\n", "")
            if len(hours) < 3:
                hours = "<MISSING>"

            #print(title)
            #print(store)
            #print(street)
            #print(city)
            #print(state)
            #print(pcode)
            #print(phone)
            #print(lat)
            #print(longt)
            #print(hours)
            print(p)
            p += 1
            data.append([
                'https://www.llbean.com',
                link,
                title,
                street,
                city,
                state,
                pcode,
                'US',
                store,
                phone,
                "flagship, Bike, Boat & Ski, hunting and fishing",
                lat,
                longt,
                hours
            ])

    return data



def scrape():
    data = fetch_data()
    write_output(data)

scrape()


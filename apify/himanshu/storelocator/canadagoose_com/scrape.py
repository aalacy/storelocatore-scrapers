
import csv
import requests
from bs4 import BeautifulSoup
import re
import json



def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    base_url = "https://www.canadagoose.com/ca/en/find-a-retailer/find-a-retailer.html"
    r = requests.get(base_url)
    main_soup = BeautifulSoup(r.text, "lxml")
    k = main_soup.find("div", {'class': "store-holder"})
    store_names = []
    street_address1 = []
    city1 = []
    state1 = []
    zip1 = []
    country_code = []
    phone1 = []
    latitude = []
    longitude = []
    return_main_object = []
    hours_of_operation = []

    names = k.find_all('h3', {'class': 'section-break'})
    for i in names:
        name = (i.span.find_next_siblings('span'))
        for j in name:
            store_names.append(j.text)

    adds = k.find_all('span', {'itemprop': "streetAddress"})
    locality = k.find_all('span', {'itemprop': "addressLocality"})
    state = k.find_all('span', {'itemprop': "addressRegion"})
    code = k.find_all('span', {'itemprop': "postalCode"})
    phone = k.find_all('span', {'itemprop': "telephone"})
    for add in adds:
        street_address1.append(add.text.replace('\n', '').replace('  ', '').replace('\r', ''))

    for i in locality:
        city1.append(i.text)

    for i in state:
        state1.append(i.text)

    for i in code:
        if i.text:
            zip1.append(i.text)
        else:
            zip1.append("<MISSING>")
    
    for i in zip1:
        if "<MISSING>" in i:
             country_code.append("<MISSING>")
        else:
            if len(i)==5:
                country_code.append("US")
            else:
                country_code.append("CA")

    for i in phone:
        phone1.append(i.text)

    link = k.find_all('a', {'class': "more-info", 'title': "More info"})

    for i in link:
        time = ''
        url = i['href']
        r = requests.get(url)
        soup = BeautifulSoup(r.text, "lxml")
        k1 = soup.find("div", {"class": "store-info desktop"})
        times = k1.find_all('meta')
        list1 = []
        a = k1.find_all('a', {'class': "button"})
        for i in a:
            latitude.append(i['href'].split('/@')[1].split('z/')[0].split(',')[0])
            longitude.append((i['href'].split('/@')[1].split('z/')[0].split(',')[1]))
        if times:
            for i in times:
                time = time + ' ' + (i.get('content'))

        else:
            time = time + ' ' + ("<MISSING>")
        hours_of_operation.append(time.strip())

    for i in range(len(store_names)):
        store = []
        store.append("https://www.canadagoose.com")
        store.append(store_names[i])
        store.append(street_address1[i])
        store.append(city1[i])
        store.append(state1[i])
        store.append(zip1[i])
        store.append(country_code[i])
        store.append("<MISSING>")
        store.append(phone1[i])
        store.append("canadagoose")
        store.append(latitude[i])
        store.append(longitude[i])
        store.append(hours_of_operation[i])
        return_main_object.append(store)

    return return_main_object


def scrape():
    data = fetch_data()

    write_output(data)


scrape()
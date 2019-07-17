import csv
import requests
from bs4 import BeautifulSoup
import re
import json

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    base_url = "https://equinox-hotels.com/"
    r = requests.get(base_url)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    main=soup.find("div",{"class":"header-subnav-inner"}).find("div",{"class":"swiper-wrapper"}).find_all("a")
    for location in main:
        if re.search('[a-zA-z]',location['href']):
            r1 = requests.get(base_url+location['href']+'wp-json/wp/v2/attractions?page=1&per_page=10&order=desc&orderby=date&location=%2Fnyc%2F').json()
            for i in range(len(r1)):
                store = []
                location_address=r1[i]['acf']['address'].split(',')
                lst=list(location_address[2].strip().split(' '))
                store.append("https://www.equinox.com")
                store.append(r1[i]['title']['rendered'])
                store.append(location_address[0])
                store.append(location_address[1])
                store.append(lst[0])
                if len(lst)>1:
                    store.append(lst[1])
                else:
                    store.append("<MISSING>")
                store.append("US")  
                store.append(r1[i]['id'])
                store.append("<MISSING>")
                store.append("Equinox Hotels")
                store.append(r1[i]['acf']['latitude'])
                store.append(r1[i]['acf']['longitude'])
                store.append("<MISSING>")
                return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()

import csv
import re
from bs4 import BeautifulSoup
import requests
import os

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    # Your scraper here
    locs = []
    street = []
    states=[]
    cities = []
    types=[]
    phones = []
    zips = []
    long = []
    lat = []
    timing = []
    ids=[]
    page_url=[]

    res=requests.get("http://www.croutonstogo.com/locations/")
    soup = BeautifulSoup(res.text, 'html.parser')
    divs = soup.find_all('p', {'class': 'lead'})

    for div in divs:
        texts=div.text
        print(texts)
        tex = texts.split("\n")
        locs.append(tex[0])
        if re.findall(r'[0-9]{5}',tex[2]) != []:
            i=2
            street.append(tex[1].strip())
        else:
            i=3
            street.append(tex[1].strip()+" "+tex[2].strip())

        addr= tex[i]
        addr=addr.split(",")
        cities.append(addr[0])
        addr= addr[1].strip().split(" ")
        zips.append(addr[1])
        states.append(addr[0].replace(".",""))
        phones.append(re.findall(r'p ([0-9\.]+)',tex[i+1])[0])
        timing.append(re.findall(r'Mon.*Closed|Mon.*pm',texts,re.DOTALL)[0].replace("\n"," "))

        print(addr)

    all = []
    for i in range(0, len(locs)):
        row = []
        row.append("http://www.croutonstogo.com")
        row.append(locs[i])
        row.append(street[i])
        row.append(cities[i])
        row.append(states[i])
        row.append(zips[i])
        row.append("US")
        row.append("<MISSING>")  # store #
        row.append(phones[i])  # phone
        row.append("<MISSING>")  # type
        row.append("<MISSING>")  # lat
        row.append("<MISSING>")  # long
        row.append(timing[i])  # timing
        row.append("http://www.croutonstogo.com/locations/")  # page url

        all.append(row)
    return all

def scrape():
    data = fetch_data()
    write_output(data)

scrape()

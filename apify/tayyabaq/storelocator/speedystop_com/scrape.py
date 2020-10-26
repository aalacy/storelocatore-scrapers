import csv
import os
import requests
import re, time
from bs4 import BeautifulSoup

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            if row:
                #Keep the trailing zeroes in zipcodes
                writer.writerow([s for s in row])
                
def fetch_data():
    # Variables
    data = [];
    store_no = [];
    location_name = [];
    location_type = [];
    city = [];
    street_address = [];
    state = [];
    phone = []
    lat=[]
    long=[]
    url = "http://www.speedystop.com/locations.html"
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')
    stores = soup.find_all('td')
    
    for i in range(0, len(stores), 4):
        coord=stores[i].find('a').get('onclick')
        #print(coord)
        la=re.findall(r'\((-?[\d\.]+),-?[\d\.]+',coord)
        lo=re.findall(r'\(-?[\d\.]+,(-?[\d\.]+)',coord)
        if la != []:
         lat.append(la[0])
        else:
         lat.append('<MISSING>')
        if lo != []:
         long.append(lo[0])
        else:
         long.append('<MISSING>')
        location_name.append(stores[i].get_text().replace('\xc2\xa0',' '))
        #print(stores[i].get_text())
        store_no.append(stores[i].get_text().split("#")[1])
    for i in range(1, len(stores), 4):
        addr=str(stores[i]).replace("\r\n","").split("<br/>")
        street_address.append(re.findall(r'">(.*)',addr[0])[0].strip())
        addr=addr[1].replace("</td>","").split(",")
        city.append(addr[0].strip())
        state.append(addr[1].strip())
    for i in range(2, len(stores), 4):
        phone.append(stores[i].get_text())
    for i in range(3, len(stores), 4):
        if stores[i].get_text() != "":
            location_type.append(stores[i].get_text().split()[-1].strip())
        else:
            location_type.append("<MISSING>")
    for n in range(0, len(location_name)):
        data.append([
            'http://www.speedystop.com',
            location_name[n],
            street_address[n],
            city[n],
            state[n],
            '<MISSING>',
            'US',
            store_no[n],
            phone[n],
            location_type[n],
            lat[n],
            long[n],
            '<MISSING>'
        ])
    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()

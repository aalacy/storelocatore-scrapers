import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
session = SgRequests()
def write_output(data):
    with open('data.csv', 'w') as output_file:
        writer = csv.writer(output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        for i in data or []:
            writer.writerow(i)
def fetch_data():
    addressess = []
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }
    base_url = 'https://www.expressionsstores.com/'
    page_url = "<MISSING>"
    location_name = ""
    street_address = "<MISSING>"
    city = "<MISSING>"
    state = "<MISSING>"
    zipp = "<MISSING>"
    store_number = "<MISSING>"
    phone = "<MISSING>"
    location_type = "<MISSING>"
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    hours_of_operation = "<MISSING>"
    r = session.get('https://www.expressionsstores.com/ccms/index.cfm/stores/',headers = headers)
    soup= BeautifulSoup(r.text,'lxml')
    dd = soup.find("div",{"class":"mura-region-local"}).text.replace("RHODE ISLAND","--------------------------------------------------------------------").replace("CONNECTICUT","--------------------------------------------------------------------").replace("MASSACHUSETTS","--------------------------------------------------------------------").split("------------------------------------------------------------------")
    for i in dd[1:]:
        part = i.replace("\xa0","").replace("           ","--").replace("  ","--").split("\n")[1:]
        while('' in part):
            part.remove('')
       
       
        if len(part)==3:
            street_address = part[0]
            city = part[1].split(",")[0]
            if len(part[1].split(",")[1].strip().split(" "))==2:
                state = part[1].split(",")[1].strip().split(" ")[0]
                zipp = part[1].split(",")[1].strip().split(" ")[1]
            else:
                state = part[1].split(",")[1].strip()[:2]
                zipp = part[1].split(",")[1].strip()[2:]
            phone = part[2].replace("P:","").replace("P. ","").strip()
            location_name = "Expressions Store"
        else:
            street_address = ", ".join(part[:2])
            city = part[2].split(",")[0].replace("No.","")
            state = part[2].split(",")[1].strip().split(" ")[0]
            zipp = part[2].split(",")[1].strip().split(" ")[1]
            phone = part[3].replace("P:","").strip()
            location_name = "Expressions Store"
        store = []
        store.append(base_url if base_url else '<MISSING>')
        store.append(location_name if location_name else '<MISSING>')
        store.append(street_address if street_address else '<MISSING>')
        store.append(city if city else '<MISSING>')
        store.append(state if state else '<MISSING>')
        store.append(zipp if zipp else '<MISSING>')
        store.append("US")
        store.append(store_number if store_number else '<MISSING>')
        store.append(phone if phone else '<MISSING>')
        store.append(location_type if location_type else '<MISSING>' )
        store.append(latitude if latitude else '<MISSING>')
        store.append(longitude if longitude else '<MISSING>')
        store.append(hours_of_operation if hours_of_operation else '<MISSING>')
        store.append(page_url if page_url else '<MISSING>')
        store = [x.strip() if type(x) == str else x for x in store]
        if store[2] in addressess:
            continue
        addressess.append(store[2])
        yield store
def scrape():
    data = fetch_data()
    write_output(data)
scrape()

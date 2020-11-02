import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import ast
session = SgRequests()
def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation",
                         "page_url"])
        for row in data:
            writer.writerow(row)
def fetch_data():
    addressess = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
    }
    base_url = "http://cafebrazil.com"
    r = session.get(base_url +'/locations' , headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    for i in soup.find_all("div",{"class":"col-sm-6 bb"}):
        dl = list(i.stripped_strings)
        location_name = dl[0]
        street_address = dl[1]
        city = dl[2].split(",")[0]
        state = dl[2].split(",")[1].strip().split(" ")[0]
        zipp = dl[2].split(",")[1].strip().split(" ")[1]
        phone = dl[3].replace("PH:","").strip()
        hours_of_operation = dl[5].replace("Hours:","").replace("HOURS:","").strip()
        map_url = i.find("a")['href']
        coords = session.get(map_url).url
        if "/@" in coords:
            lat = coords.split("/@")[1].split(",")[0]
            lng = coords.split("/@")[1].split(",")[1]
        else:
            map_soup = BeautifulSoup(session.get(map_url).text, "lxml")
            file_name = open("data.txt","w",encoding="utf-8")
            file_name.write(str(map_soup))
            try:
                map_href = map_soup.find("a",{"href":re.compile("https://maps.google.com/maps?")})['href']
                lat = str(BeautifulSoup(session.get(map_href).text, "lxml")).split("/@")[1].split(",")[0]
                lng = str(BeautifulSoup(session.get(map_href).text, "lxml")).split("/@")[1].split(",")[1]
            except:
                lat = str(map_soup).split("/@")[1].split(",")[0]
                lng = str(map_soup).split("/@")[1].split(",")[1]
        store = []
        store.append(base_url if base_url else '<MISSING>')
        store.append(location_name if location_name else '<MISSING>')
        store.append(street_address if street_address else '<MISSING>')
        store.append(city if city else '<MISSING>')
        store.append(state if state else '<MISSING>')
        store.append(zipp if zipp else '<MISSING>')
        store.append("US")
        store.append('<MISSING>')
        store.append(phone if phone else '<MISSING>')
        store.append("Cafe Brazil")
        store.append(lat if lat else '<MISSING>')
        store.append(lng if lng else '<MISSING>')
        store.append(hours_of_operation if hours_of_operation else '<MISSING>')
        store.append("https://www.cafebrazil.com/locations/")
        store = [x.encode('ascii', 'ignore').decode('ascii').strip() if type(x) == str else x for x in store]
        if store[2] in addressess:
            continue
        addressess.append(store[2])
        yield store
def scrape():
    data = fetch_data()
    write_output(data)
scrape()
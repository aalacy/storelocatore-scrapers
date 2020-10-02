import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
session = SgRequests()
def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        for row in data:
            writer.writerow(row)
def fetch_data():
    addressess = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
        }
    base_url = "http://www.foreveryogurt.com"
    r = session.get("https://foreveryogurt.com/locations/",headers=headers)
    soup = BeautifulSoup(r.text,'lxml')
    for div in soup.find_all("div",{"class":"fusion-text"})[2:]:
        addr = list(div.stripped_strings)
        if len(addr)==10:
            location_name = addr[0]
            street_address = addr[1]
            city = addr[2].split(",")[0]
            state = addr[2].split(",")[1].strip().split(" ")[0]
            zipp = addr[2].split(",")[1].strip().split(" ")[1]
            phone = addr[4]
            hours_of_operation = " ".join(addr[6:9])
        elif len(addr)==12:
            location_name = addr[0]
            street_address = ", ".join(addr[1:3])
            city = addr[3].split(",")[0]
            state = addr[3].split(",")[1].strip().split(" ")[0]
            zipp = addr[3].split(",")[1].strip().split(" ")[1]
            phone = addr[5]
            hours_of_operation = " ".join(addr[8:11])
        else:
            location_name = addr[0]
            street_address = addr[1]
            city = addr[2].split(",")[0]
            state = addr[2].split(",")[1].strip().split(" ")[0]
            zipp = addr[2].split(",")[1].strip().split(" ")[1]
            phone = addr[4]
            hours_of_operation = addr[7]
        map_url = div.find("a")['href']
        coords = session.get(map_url).url
        try:
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
        except:
            lat = "<MISSING>"
            lng = "<MISSING>"
        phone = phone.replace(":","").strip()
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
        store.append("Forever Yogurt")
        store.append(lat if lat else '<MISSING>')
        store.append(lng if lng else '<MISSING>')
        store.append(hours_of_operation if hours_of_operation else '<MISSING>')
        store.append("<MISSING>")
        store = [x.encode('ascii', 'ignore').decode('ascii').strip() if type(x) == str else x for x in store]
        if store[2] in addressess:
            continue
        addressess.append(store[2])
        yield store
def scrape():
    data = fetch_data()
    write_output(data)
scrape()

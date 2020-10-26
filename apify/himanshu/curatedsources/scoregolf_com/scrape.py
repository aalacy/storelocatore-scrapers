import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json 
import time
session = SgRequests()
import requests

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

 
def fetch_data():
    
    base_url = "https://scoregolf.com"

    r = requests.get("https://scoregolf.com/golf-course-guide/search")
    soup = BeautifulSoup(r.text, "lxml")
    links = soup.find("table",{"class":"tablesorter"}).find("tbody").find_all("a")
    for link in links:
        page_url = base_url+link['href']
        if "/golf-course-guide/angel's-view-golf-course-oakville-ontario-canada" in link['href'] or "/golf-course-guide/club-de-golf-des-iles-inc-l'Étang-du-nord, qc-quebec-canada" in link['href']:
            continue
        #print(page_url)
        try:
            r1 = requests.get(page_url)
        except:
            pass
        soup1 = BeautifulSoup(r1.text, "lxml")
        
        if soup1.find("div",{"class":"block crs-header-block"}) == None:
            continue
        location_name = re.sub(r'\s+'," ",str(soup1.find("div",{"class":"block crs-header-block"}).find("h1").text.replace("\r","").replace("\n","").replace("\t","").strip()))

        addr = list(soup1.find_all("div",{"class":"cg-address"})[-1].stripped_strings)

        street_address = ' '.join(addr[1:-2]).replace(",","")
        city = addr[-2].split(",")[0]
        state = addr[-2].split(",")[1]
        zipp = addr[-1].replace("B1A***","B1A").replace("G0J1WO","G0J1W0")
        phone = soup1.find("p",{"class":"exp-tx"}).text.replace("ext 226","").replace("(ext 103)","").replace("or 866-886-4422","").replace("Clubhouse","").replace(", Pro Shop 705-737-2744","").replace("/ 418 335-2931","").strip()
        coords = soup1.find(lambda tag: (tag.name == "script") and "initFacMap" in tag.text).text
        latitude = coords.split("initFacMap(")[1].split(",")[0].replace("0.0000000000","<MISSING>")
        longitude = coords.split("initFacMap(")[1].split(",")[1].replace("0.0000000000","<MISSING>")
        location_type = "ScoreGolf Club"

        store = []
        store.append(base_url)
        store.append(location_name.split('in')[0] if location_name else '<MISSING>')
        store.append(street_address if street_address else '<MISSING>')
        store.append(city if city else '<MISSING>')
        store.append(state if state else '<MISSING>')
        store.append(zipp if zipp else '<MISSING>')
        store.append('CA')
        store.append('<MISSING>')
        store.append(phone if phone else '<MISSING>')
        store.append(location_type if location_type else '<MISSING>')
        store.append(latitude if latitude else '<MISSING>')
        store.append(longitude if longitude else '<MISSING>')

        store.append('<MISSING>')
        store.append(page_url)
        store = [str(x).replace("\u200b","") if x else "<MISSING>" for x in store]
        store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
        yield store
                


def scrape():
    data = fetch_data()

    write_output(data)


scrape()

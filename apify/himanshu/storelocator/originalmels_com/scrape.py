import csv
import re
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
import json
session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w', newline='') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    base_url = "https://originalmels.com"
    page_url = "https://originalmels.com/locations/"
    soup = bs(session.get(page_url).text, "lxml")

    cords = {}
    data = json.loads(soup.find(lambda tag: (tag.name == "script") and '"lat":' in tag.text).text.split("var wpgmaps_localize_marker_data =")[1].split("var wpgmaps_localize_global_settings ")[0].replace("[]}};","[]}}"))
    for index,value in data.items():
        
        phone_soup = bs(value['desc'],"lxml")
        
        key = phone_soup.find_all("p")[0].text.replace("(","").replace(")","").replace("-","").replace(" ","")
        if "Hours:" in key:
            key = "7074254452"

        cords[key.replace("7754514811","7753376357")] = {"lat":value['lat'], "lng":value['lng']}
    cords['9257541841'] =   {"lat":"<MISSING>", "lng":"<MISSING>"}
    
    for div in soup.find_all("div",{"class":re.compile("fusion-layout-column fusion_builder_column fusion_builder_column_1_3")}):
        location_name = div.find("h3").text
        
        addr = list(div.find_all("div",{"class":"fusion-text"})[1].stripped_strings)
        street_address = addr[0]
        city = addr[1].split(",")[0]
        state = addr[1].split(",")[-1].split()[0]
        zipp = addr[1].split(",")[-1].split()[-1]
        
        phone = addr[2].split("T:")[-1].strip()
        if addr[2].split("T:")[-1].strip() == '':
            phone = "(925) 691-9900"
        lat = cords[phone.replace("(","").replace(")","").replace("-","").replace(" ","")]['lat']
        lng = cords[phone.replace("(","").replace(")","").replace("-","").replace(" ","")]['lng']
        hr = list(div.find_all("div",{"class":"fusion-text"})[2].stripped_strings)
        
        if 'Temporary Hours' in hr[0] or 'DINING' in hr[0]:
            del hr[0]
        if "Hours" in hr[0] or 'OPEN' in hr[0] or 'Open' in hr[0]:
            del hr[0]
        if 'SINCE' in hr[-1]:
            del hr[-1]

        hrs = " ".join(hr)
        if 'Temporary Hours' in hrs:
            hours = hrs.split('Hours')[1].strip()
        elif 'Hours' in hrs:
            hours = hrs.split('Hours')[1].strip()
        elif 'temporarily' in hrs:
            hours = '<MISSING>'
        else:
            hours = hrs.replace("H ou rs","")
    
        store = []
        store.append(base_url)
        store.append(location_name)
        store.append(street_address)
        store.append(city)
        store.append(state)
        store.append(zipp)   
        store.append("US")
        store.append("<MISSING>")
        store.append(phone)
        store.append("<MISSING>")
        store.append(lat)
        store.append(lng)
        store.append(hours)
        store.append(page_url)     
    
        store = [str(x).replace("\xa0"," ").replace("–","-").encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
        
        yield store

def scrape():
    data = fetch_data()
    write_output(data)

scrape()

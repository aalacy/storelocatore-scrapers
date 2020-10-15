import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json


session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w',encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
    }
    base_url = "https://www.balenciaga.com"
    
    r = session.get("https://www.balenciaga.com/experience/us/?yoox_storelocator_action=true&action=yoox_storelocator_get_all_stores",headers=headers)
    data = r.json()
    return_main_object = []
    for store_data in data:
        store = []
        if store_data['wpcf-yoox-store-country-iso'] in ["US","CA"]:
            adr = (store_data['wpcf-yoox-store-address'].replace("\r"," ").replace("\n",'').split("<br> <br>")[0].split("<br><br>")[0].replace("Bloomingdale's ",'').split("at")[-1].replace("Ala Moana Shopping Center",'').replace("South Coast Plaza",'').replace("Caesars","").replace("Crystals",'').replace("Yorkdale Shopping Centre",'').replace("Las Vegas Wynn Wynn Encore Esplanade",'').replace("The Galleria ",'').replace("Balenciaga Miami Design District",'').strip())
            if "OPENING SOON" in adr:
                continue
            adr = (adr.replace("Costa Mesa",",Costa Mesa").replace("Honolulu",",Honolulu").replace("Las Vegas",",Las Vegas").replace("New York",",New York").replace("Harbour",",Harbour").replace("Dallas",",Dallas").replace("Vancouver",",Vancouver").replace("Toronto",",Toronto").replace("Miami",",Miami").replace("Hills",",Hills").replace("Santa Clara",",Santa Clara").replace("North York",",North York").replace("Houston",",Houston").replace("Los Angeles",",Los Angeles"))
            ca_zip_list = re.findall(r'[A-Z]{1}[0-9]{1}[A-Z]{1}\s*[0-9]{1}[A-Z]{1}[0-9]{1}', str(adr))
            us_zip_list = re.findall(re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str(adr))
            state=''
            state_list = re.findall(r' ([A-Z]{2}) ', str(adr))    
            if state_list:
                state = state_list[-1]

            if ca_zip_list:
                zipp = ca_zip_list[-1]
                country_code = "CA"
            zipp=''
            if us_zip_list:
                zipp = us_zip_list[-1]
                country_code = "US"
            adr = adr.replace(state,"").replace(zipp,"").strip().split(",")
            if adr[-1]=='':
                del adr[-1]
            
            city = adr[-1].strip()
            street_address = " ".join(adr[:-1]).replace("Toronto",'').replace("North York",'')
            street_address = " ".join(adr[:-1]).replace("Toronto",'').replace("North York",'')
            contry="US"
            if "50 Bloor Street West  " in street_address:
                city = "Toronto"
                state = "Ontario"
                zipp = "M4W 1A1"
                contry="CA"

            if "3401 Dufferin St  CRU 313  " in street_address:
                city = "Toronto"
                state = "Ontario"
                zipp = "M6A 2T9"
                contry="CA"
            if "737 Dunsmuir Street  Vancouver" in street_address:
                street_address = "737 Dunsmuir Street"
                city = "Vancouver"
                state = "BC"
                zipp = "V7Y 1E4"
                contry="CA"
            location_name = store_data["post_title"]
            ids = store_data["ID"]
            latitude = store_data["lat"]
            longitude = store_data["lng"]
            page_url = store_data['permalink']
            phone = store_data['wpcf-yoox-store-phone']

            store = []
            store.append("https://www.balenciaga.com/")
            store.append(location_name if location_name else '<MISSING>')
            store.append(street_address.replace("AvenueFloor","Avenue Floor") if street_address else '<MISSING>')
            store.append(city if city else '<MISSING>')
            store.append(state if state else '<MISSING>')
            store.append(zipp if zipp else '<MISSING>')
            store.append(contry)
            store.append(ids)
            store.append(phone if phone else '<MISSING>')
            store.append( '<MISSING>')
            store.append(latitude if latitude else '<MISSING>')
            store.append(longitude if longitude else '<MISSING>')
            store.append(" ".join(list(BeautifulSoup(store_data["wpcf-yoox-store-hours"].replace("\r"," ").replace("\n"," "),"lxml").stripped_strings)) if "wpcf-yoox-store-hours" in store_data else "<MISSING>")
            store.append(page_url)
            store = [x.replace("–","-") if type(x) == str else x for x in store]
            yield store
            # print(store)

def scrape():
    data = fetch_data()
    write_output(data)

scrape()

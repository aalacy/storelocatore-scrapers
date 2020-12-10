import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import re
import json
import time
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('stokesstores_com')


session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w', newline='') as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)
def fetch_data():
    

    headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }
    base_url = "https://www.stokesstores.com/en/"
   
    soup = bs(session.get("https://www.stokesstores.com/en/storelocator/").text, "lxml")
    # logger.info(soup)
    json_data = json.loads(str(soup).split("stores      :")[1].split("countLabel")[0].replace("}],","}]"))
    for data in json_data:

        location_name = data['name']
        street_address = data['address']
        city = data['city']
        state = data['state']
        zipp = data['zipcode']
        country_code = data['country']
        store_number = data['storelocator_id']
        location_type = "StokesStores"
        phone = data['phone']
        lat = data['latitude']
        lng = data['longtitude']
        page_url = "https://www.stokesstores.com/en/"+data['rewrite_request_path']

        if session.get(page_url).status_code == 200:
            location_soup = bs(session.get(page_url).content, "lxml")
            hours = " ".join(list(location_soup.find("div",{"class":"opening-hours"}).find("table").stripped_strings))
        else:
            hours = "<MISSING>"
        
        store = []
        store.append(base_url)
        store.append(location_name)
        store.append(street_address)
        store.append(city)
        store.append(state)
        store.append(zipp)
        store.append(country_code)
        store.append(store_number) 
        store.append(phone)
        store.append(location_type)
        store.append(lat)
        store.append(lng)
        store.append(hours)
        store.append(page_url)
        store = [str(x).strip() if x else "<MISSING>" for x in store]
        yield store

def scrape():
    data = fetch_data()

    write_output(data)


scrape()




        
    


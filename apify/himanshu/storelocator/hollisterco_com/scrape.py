import csv
import requests
from bs4 import BeautifulSoup
import re
import json
import time
from datetime import datetime
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('hollisterco_com')



def write_output(data):
    with open('data.csv', mode='w', newline='') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    addresses = []
   
    base_url= "https://www.hollisterco.com"

    
    headers = {          
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36',
        'accept': 'application/json'
    }
    r = requests.get("https://www.hollisterco.com/shop/ViewAllStoresDisplayView?storeId=11205&catalogId=10201&langId=-1", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    data = soup.find_all("li",{"class":"view-all-stores__store"})
    for link in data:
        
        if "/shop/wd/clothing-stores/CA/" in link.find("a")['href'] or "/shop/wd/clothing-stores/US/"in link.find("a")['href']:
            page_url = base_url+link.find("a")['href']
            r = requests.get(page_url, headers=headers)
            soup = BeautifulSoup(r.text, "lxml")
            if soup.find(lambda tag: (tag.name == "script") and "geoNodeUniqueId" in tag.text) == None:
                continue
            json_data = json.loads(soup.find(lambda tag: (tag.name == "script") and "geoNodeUniqueId" in tag.text).text.split("try {digitalData.set('physicalStore',")[1].split(");}")[0])
            location_name = json_data['name']
            street_address = json_data['addressLine'][0] #.replace("['",'').replace("']",'')
            city = json_data['city']
            state = json_data['stateOrProvinceName']
            zipp = json_data['postalCode']
            country_code = json_data['country']
            store_number = json_data['storeNumber']
            phone = json_data['telephone']
            location_type = "clothing-stores"
            latitude = json_data['latitude']
            longitude = json_data['longitude']
            for j in json_data['physicalStoreAttribute']:
                if "hours-Week1" in j['name']:
                    hours = ''
                    day = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
                    for l in range(0,7):
                        start = datetime.strptime(str(j['value'].split(',')[l].split("|")[0]), "%H:%M")
                        start_value=start.strftime("%I:%M %p")
                        end = datetime.strptime(str(j['value'].split(',')[l].split("|")[1].replace("M","")), "%H:%M")
                        end_value = end.strftime("%I:%M %p")
                        hours+= " "+day[l]+" "+start_value+" - "+end_value
                    hours_of_operation = hours
            store = []
            store.append(base_url)
            store.append(location_name)
            store.append(street_address)
            store.append(city)
            store.append(state)
            store.append(zipp)
            store.append(country_code)
            store.append(store_number)
            store.append(phone )
            store.append(location_type)
            store.append(latitude)
            store.append(longitude)
            store.append(hours_of_operation)
            store.append(page_url)
            # if store[2] in addresses:
            #     continue
            # addresses.append(store[2])
            # logger.info("data =="+str(store))
            # logger.info("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
            yield store
        else:
            pass # another country location
       

        

       
        
def scrape():
    data = fetch_data()
    write_output(data)


scrape()

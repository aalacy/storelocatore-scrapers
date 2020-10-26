import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('rosesdiscountstores_com')




session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w',newline= "") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    base_url = "https://www.rosesdiscountstores.com"
    return_main_object=[]
    r = session.get("https://api.zenlocator.com/v1/apps/app_vfde3mfb/locations/search?northeast=82.292271%2C90.127516&southwest=-57.393437%2C-180").json()
    for loc in r['locations']:
        name=loc['name'].strip()
        location_type = name
        addr = loc['address'].split(",")
        if "United States" in addr[-1] or "US" in addr[-1]:
            del addr[-1]
        street_address = " ".join(addr[:-2])
        
        city = addr[-2]
        zipp_list = re.findall(r'\d{5}',addr[-1])
        if zipp_list:
            zipp = zipp_list[-1]
        state = addr[-1].replace(zipp,"").strip()
        if "111 Main St Greensboro" in addr[-2]:
            street_address = addr[-2].replace("Greensboro",'')
            city = "Greensboro"

        if "2606 Zion Road  Henderson" in street_address:
            state ='Kentucky'
            street_address = street_address.replace("Henderson",'')
      
        
        country=loc['countryCode'].strip()
        try:
            phone=loc['contacts']['con_wg5rd22k']['text'].replace("(864) 77702853","(864) 777-2853").strip()
        except:
            phone = "<MISSING>"
        lat=loc['lat']
        lng=loc['lng']
        hour=''
        if 'hours' in loc:
            if 'hoursOfOperation' in loc['hours']:
                for hr in loc['hours']['hoursOfOperation']:
                    hour+=' '+hr+" : "+loc['hours']['hoursOfOperation'][hr]

        if "hrs_ywfef43p" in loc['hours']:
            hour = 'Monday 9am-9pm  Tuesday 9am-9pm  Wednesday 9am-9pm  Thursday 9am-9pm  Friday 9am-9pm  Saturday 9am-9pm  Sunday 10am-8pm'
            
        if "hrs_a4db656x" in loc['hours']:
            hour = 'Monday 9am-6pm  Tuesday 9am-6pm  Wednesday 9am-6pm  Thursday 9am-6pm  Friday 9am-6pm  Saturday 9am-6pm  Sunday 12pm-6pm'
        
        storeno=''
        store=[]
        store.append(base_url)
        store.append(name if name else "<MISSING>")
        store.append(street_address if street_address else "<MISSING>")
        store.append(city.replace("Kentucky",'Henderson') if city else "<MISSING>")
        store.append(state if state else "<MISSING>")
        store.append(zipp if zipp else "<MISSING>")
        store.append(country if country else "<MISSING>")
        store.append(storeno if storeno else "<MISSING>")
        store.append(phone if phone else "<MISSING>")
        store.append(location_type if location_type else "<MISSING>")
        store.append(lat if lat else "<MISSING>")
        store.append(lng if lng else "<MISSING>")
        store.append(hour if hour else "<MISSING>")
        store.append("https://www.rosesdiscountstores.com/store-locator-index")
        store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
        # logger.info(store)
        yield store

def scrape():
    data = fetch_data()
    write_output(data)
scrape()

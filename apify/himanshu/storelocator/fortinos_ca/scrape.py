import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import time
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
        'site-banner': 'fortinos',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36',
        'Cookie': 'ak_bmsc=18B950B5D2AF67482FD6D7D942F177E617417C34E17A0000649C9A5FBB2E1644~plQlKD7ApWOKJJDRFcfVclw0p/Ke7WRPaT4kDTJKFSVqjsjynXMXw5bL7XaiAI7UUYw4JnPHSaVRx1df4D+ziBqaWLn7nWjwmwN8DXqgZtpXCjoL0eaJtf5DjHye1TiGGzXGiKo2xBmuq2jJiUEN9CrfIRDVo2rXnatxP6WNXghL05r2EV9B89xgtbW1ee4T+CtopCgW99JmZWXYOMbC8mG0PP0Wi/eP9/eNdIYuH7WWU=; ADRUM_BTa=R:0|g:d3f2323f-44a8-4af5-9d1b-f0ee26aa6a34|n:lblw_afe7f4d6-4637-4e11-95bb-0a169ff97498; ADRUM_BT1=R:0|i:352462|e:99; bm_sv=EA63D9ED91118F2C13887BFF56449650~UbAdYJMOlOAEBRv2ajLNck5f2RbU1GQh5CNEYD5u/2BGavRlr0YgAwxglQftqvsd0tJFaf00ipTiUagAkjZfdIk95IMJnUlrCExJ9Wp1WWiGT2J5/dsDXVBL1aOOgVRjRd1egMz5IKWL/iAy3mbQRfy5jNGSb4v6IIZJ5lN7Kkw='
        }
    base_url = "https://www.fortinos.ca/"
    r = session.get("https://www.fortinos.ca/api/pickup-locations?bannerIds=fortinos",headers=headers).json()
    for val in r:
        store_number = val['id'].replace("CT","").replace("0096SD1179","0096SD1268")
        time.sleep(2)
        jd = session.get("https://www.fortinos.ca/api/pickup-locations/"+store_number,headers=headers).json()
        location_name = jd['name']
        if val['address']['line2']!=None:
            street_address = jd['address']['line1']+" "+jd['address']['line2']
        else:
            street_address = jd['address']['line1']
        
        city = jd['address']['town']
        state = jd['address']['region']
        if jd['address']['postalCode']!=None:
            zipp = jd['address']['postalCode']
        else:
            zipp = "<MISSING>"
        location_type = jd['locationType']
        latitude = jd['geoPoint']['latitude']
        longitude = jd['geoPoint']['longitude']
        page_url = "https://www.fortinos.ca/store-locator/details/"+store_number
        if 'storeDetails' in jd:
            phone = jd['storeDetails']['phoneNumber']
            hoo = []
            for h in jd['storeDetails']['storeHours']:
                frame = h['day']+"-"+h['hours']
                hoo.append(frame)
            hours_of_operation = ", ".join(hoo)
        else:
            phone = "<MISSING>"
            hours_of_operation = "<MISSING>"
    
        store = []
        store.append(base_url if base_url else '<MISSING>')
        store.append(location_name if location_name else '<MISSING>')
        store.append(street_address if street_address else '<MISSING>')
        store.append(city if city else '<MISSING>')
        store.append(state if state else '<MISSING>')
        store.append(zipp if zipp else '<MISSING>')
        store.append("CA")
        store.append(store_number)
        store.append(phone if phone else '<MISSING>')
        store.append(location_type)
        store.append(latitude if latitude else '<MISSING>')
        store.append(longitude if longitude else '<MISSING>')
        store.append(hours_of_operation if hours_of_operation else '<MISSING>')
        store.append(page_url)
        store = [x.encode('ascii', 'ignore').decode('ascii').strip() if type(x) == str else x for x in store]
        if store[2] in addressess:
            continue
        addressess.append(store[2])
        yield store
def scrape():
    data = fetch_data()
    write_output(data)
scrape()

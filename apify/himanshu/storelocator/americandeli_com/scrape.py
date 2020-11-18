import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import sgzip
import shapely
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('americandeli_com')




session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    base_url ="https://americandeli.com"
    cord=sgzip.coords_for_radius(50)
    return_main_object=[]
    output=[]
    headers={"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36","x-requested-with": "XMLHttpRequest"}
    for cd in cord:
        # logger.info(cd)
        try:
            r = session.get("https://americandeli.com/wp-admin/admin-ajax.php?action=store_search&lat="+cd[0]+"&lng="+cd[1]+"&max_results=200&search_radius=50",headers=headers)
            if r.text=="":
                continue
            r=r.json()
            for loc in r:
                name=loc['store'].strip()
                address=loc['address'].strip()
                city=loc['city'].strip()
                state= name.split(',')[1].strip().split(' ')[0]               
                country=loc['country'].strip()
                if country =="United States":
                    country="US"
                zip=loc['zip']
                storeno=loc['id']
                phone=loc['phone'].strip()
                lat=loc['lat']
                lng=loc['lng']
                cleanr = re.compile('<.*?>')
                hour = re.sub(cleanr, ' ', loc['hours'])
                store=[]
                store.append(base_url)
                store.append(name if name else "<MISSING>")
                store.append(address if address else "<MISSING>")
                store.append(city if city else "<MISSING>")
                store.append(state if state else "<MISSING>")
                store.append(zip if zip else "<MISSING>")
                store.append(country if country else "<MISSING>")
                store.append(storeno if storeno else "<MISSING>")
                store.append(phone if phone else "<MISSING>")
                store.append("<MISSING>")
                store.append(lat if lat else "<MISSING>")
                store.append(lng if lng else "<MISSING>")
                store.append(hour if hour.strip() else "<MISSING>")
                store.append('<MISSING>')
                adrr =name+' '+address + ' ' + city + ' ' + state + ' ' + zip
                if adrr not in output:
                    output.append(adrr)
                    return_main_object.append(store)
                # logger.info(store)
                # logger.info("==============")
        except:
            continue
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)
scrape()

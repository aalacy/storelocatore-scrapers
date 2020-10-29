import csv
from bs4 import BeautifulSoup
import re
import json
import requests
import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('lawlersbarbecue_com')


session = SgRequests()


def write_output(data):
    with open('data.csv', mode='w',encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    base_url = "https://www.lawlersbarbecue.com"
    json_data = requests.get("https://gusto-dataaccessapi.azurewebsites.net/api/v2/2099/Location").json()
    phone_dict = {}
    h={}
    
    r = requests.get("https://www.lawlersbarbecue.com/locations",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    for script in soup.find_all("script",{"type":'application/ld+json'}):
        if '"location":' in script.text:
            location_list = json.loads(script.text)["location"]
            for store_data in location_list:
                phone_data = store_data["telephone"].replace("+1(","").replace(")","").replace("-","").replace(" ","")
                h[phone_data]=" ".join(store_data["openingHours"])          

    for data in json_data:
        # logger.info(data)
        store = []
        store.append("https://www.lawlersbarbecue.com")
        # logger.info()
        store.append(" ".join(data["Name"].replace("#",'').strip().split( )[1:]))
        phone_data = data['Phone'].replace("+1(","").replace(")","").replace("-","").replace(" ","")
        store.append(data['Address'])
        store.append(data["City"])
        store.append(data["State"])
        store.append(data["PostalCode"])
        store.append("US")
        store.append(data['LocationID'])
        phones = ('(%s) %s-%s' % tuple(re.findall(r'\d{4}$|\d{3}', data['Phone'])))
        store.append(phones)
        try:
            page_url = ("https://order-online.azurewebsites.net/2099/"+str(data['LocationID'])+"/")
        except:
            page_url = "<MISSING>"
        store.append("<MISSING>")
        store.append(data['Latitude'])
        store.append(data['Longitude'])
        
        if phone_data in h:
            store.append(h[phone_data])
        else:
            store.append("Mon - Sat 10:30AM – 8PM")
        store.append(page_url)
        yield store


def scrape():
    data = fetch_data()
    write_output(data)

scrape()

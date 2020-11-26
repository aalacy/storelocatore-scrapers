import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import sgzip
import unicodedata
from sglogging import SgLogSetup
logger = SgLogSetup().get_logger('menswearhouse_com')
session = SgRequests()
def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        for row in data:
            writer.writerow(row)
def fetch_data():
    return_main_object = []
    addresses = []
    search = sgzip.ClosestNSearch() # TODO: OLD VERSION [sgzip==0.0.55]. UPGRADE IF WORKING ON SCRAPER!
    search.initialize()
    MAX_RESULTS = 50
    MAX_DISTANCE = 50
    current_results_len = 0
    zip_code = search.next_zip()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        "X-Requested-With": "XMLHttpRequest",
    }
    base_url = "https://www.menswearhouse.com"
    location_url = "https://www.menswearhouse.com/sr/search/resources/store/12751/storelocator/byProximity?radius=50000000&zip=21216&city=&state=&brand=TMW&profileName=X_findStoreLocatorWithExtraFields"
    loc = session.get(location_url,headers=headers).json()
    locator_domain = base_url
    location_name = ""
    street_address = ""
    city = ""
    state = ""
    zipp = ""
    country_code = "US"
    store_number = ""
    phone = ""
    location_type = "Men's Wearhouse"
    latitude = ""
    longitude = ""
    raw_address = ""
    hours_of_operation = ""
    street_address1 = ''
    street_address2 = ''
    store_name=''
    if "DocumentList" in loc:
        current_results_len = len(loc['DocumentList']) 
        for data in loc['DocumentList']:
            store_name = data['storeName']
            if "address1_ntk" in data:
                street_address1 = data['address1_ntk']
            if "address2_ntk" in data:
                street_address2 = data['address2_ntk']
            street_address = street_address1
            soup = BeautifulSoup(data['working_hours_ntk'], "lxml")
            hours_of_operation =  " ".join(list(soup.stripped_strings)).lower().replace("pm"," pm ").replace("am",' am ').replace("sun"," sun ").replace("mon"," mon ").replace("wed"," wed ").replace("thu"," thu ").replace("fri"," fri ").replace("sat"," sat ").replace("tue"," tue ")
            page_url = "https://www.menswearhouse.com/store-locator/"+str(data['stloc_id'])
            store_number = str(data['stloc_id'])
            if "phone_ntk" in data:
                phone =data['phone_ntk']
            else:
                phone = "<MISSING>"
            store = [locator_domain, store_name.capitalize(), street_address.replace(data['state_ntk'],"").lower(), data['city_ntk'].lower(), data['state_ntk'], data['zipcode_ntk'], country_code,
                    store_number, phone, location_type, data['latlong'].split(",")[0], data['latlong'].split(",")[1], hours_of_operation.replace("   ",","),page_url]
            for i in range(len(store)):
                if type(store[i]) == str:
                    store[i] = ''.join((c for c in unicodedata.normalize('NFD', store[i]) if unicodedata.category(c) != 'Mn'))
            store = [x.replace("–","-") if type(x) == str else x for x in store]
            store = [x.encode('ascii', 'ignore').decode('ascii').strip() if type(x) == str else x for x in store]
            if store[2] + store[-3] in addresses:
                continue
            addresses.append(store[2] + store[-3])
            
            yield store
def scrape():
    data = fetch_data()
    write_output(data)
scrape()

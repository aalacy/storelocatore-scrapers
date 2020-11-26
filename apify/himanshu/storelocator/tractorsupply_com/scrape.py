import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import sgzip
from sglogging import SgLogSetup
logger = SgLogSetup().get_logger('tractorsupply_com')
from sgselenium import SgSelenium

session = SgRequests()
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
    zip_codes = sgzip.for_radius(50)
    driver = SgSelenium().firefox()

    base_url = "https://shawfloors.com/"
    location_url = "https://www.tractorsupply.com/wcs/resources/store/10151/zipcode/fetchstoredetails?zipCode=20176&responseFormat=json&_=1606384636471"

    driver.get(location_url)


    cookies_list = driver.get_cookies()
    cookies_json = {}
    for cookie in cookies_list:
        cookies_json[cookie['name']] = cookie['value']

    cookies_string = str(cookies_json).replace("{", "").replace("}", "").replace("'", "").replace(": ", "=").replace(
    ",", ";")  # use for header cookie

    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
       
    }

    base_url = "https://www.tractorsupply.com/"

    for index,zip_code in enumerate(zip_codes):
        headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36',
        'accept': 'application/json, text/javascript, */*; q=0.01',
        'referer': 'https://www.tractorsupply.com/tsc/store-locator?zipCode=85029&state=&city=&fullState=&storeId=10151&catalogId=10051&returnStoreLocatorUrl=https%3A%2F%2Fwww.tractorsupply.com%2Ftsc%2Fcms%2Fblack-friday-now%3Fcm_re%3DHP-_-HERO%2BBANNER-_-Black%2BFriday%23',
        'x-requested-with': 'XMLHttpRequest',
          'Cookie': str(cookies_string)
        } 
        json_data = session.get("https://www.tractorsupply.com/wcs/resources/store/10151/zipcode/fetchstoredetails?zipCode="+str(zip_code)+"&responseFormat=json&_=1606384636471", headers=headers).json()['storesList']
        for data in json_data:

            location_name = data['storeName'].capitalize()
            street_address = data['addressLine'].lower()
            city = data['city'].lower()
            state = data['state']
            zipp = data['zipCode']
            store_number = data['stlocId']
            country_code =  data['country']
            phone = data['phoneNumber']
            lat = data['latitude']
            lng = data['longitude']
            hours = data['storeHours'].replace("="," ").replace("|"," ")
            page_url = "https://www.tractorsupply.com/tsc/store_"+str(location_name.replace(" ","").replace(state,"").strip())+"-"+str(state)+"-"+str(zipp)+"_"+str(store_number)

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
            store.append("<MISSING>")
            store.append(lat)
            store.append(lng)
            store.append(hours)
            store.append(page_url)
            if store[2] in addresses:
                continue
            addresses.append(store[2])  
            store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
            yield store

def scrape():
    data = fetch_data()
    write_output(data)
scrape()
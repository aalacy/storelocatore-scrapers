import csv
import re
import time
import json
from sgrequests import SgRequests
from bs4 import BeautifulSoup
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('promedica_org')


session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8", newline='') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation",
                         "page_url"])
        # Body
        for row in data:
            writer.writerow(row)






def fetch_data():
    # driver = SgSelenium().firefox()
    addressess =[]
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    }

    base_url = "https://www.promedica.org"
    addresses = []
    
    url = "https://www.promedica.org/find-locations/location-results?count=550"

    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9,pt;q=0.8',
        'cache-control': 'max-age=0',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36'
        }
    response = BeautifulSoup(session.get(url,headers=headers).text,'lxml')
    var = response.text.split("moduleInstanceData_IH_PublicDetailView")[-1].split("[]};")[0]+"[]}"
    json_data = json.loads('{"'+var.split('= {"')[1])
    for d in json.loads(json_data['SettingsData'])['MapItems']:
        location_name = d['Title']
        street_address = d['LocationAddress']
        locator_domain = "https://www.promedica.org/"
        store_number = "<MISSING>"
        if "Latitude" in d:
            latitude =d['Latitude']
            longitude =d['Longitude']
        else:
            latitude ="<MISSING>"
            longitude ="<MISSING>"
        location_type = "<MISSING>"
        ca_zip_list = re.findall(r'[A-Z]{1}[0-9]{1}[A-Z]{1}\s*[0-9]{1}[A-Z]{1}[0-9]{1}', str(street_address))
        us_zip_list = re.findall(re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str(street_address))

        if ca_zip_list:
            zipp = ca_zip_list[-1]
            country_code = "CA"

        if us_zip_list:
            zipp = us_zip_list[-1]
            country_code = "US"
        if d['LocationPhoneNum']:
            phone = d['LocationPhoneNum']
        else:
            phone = "<MISSING>"
        
        page_url = "https://www.promedica.org"+d['DirectUrl']
        state = street_address.replace(zipp,'').split(",")[-1]
        city = street_address.replace(zipp,'').split(",")[-2]
        street_address  = " ".join(street_address.replace(zipp,'').split(",")[:-2])
        hours_of_operation = "<MISSING>"
        store = [base_url, location_name, street_address, city, state, zipp, country_code,
            store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]

        if str(store[2]+store[-1]) in addressess:
            continue
        addressess.append(str(store[2]+store[-1]))
        yield store
        
       
        


def scrape():
    data = fetch_data()
    write_output(data)


scrape()

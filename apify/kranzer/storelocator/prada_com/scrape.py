import json
import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
from lxml import html

import time
from random import randint

def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    session = SgRequests()
    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"'
    HEADERS = {'User-Agent' : user_agent}

    base_url = "https://www.prada.com/us/en/store-locator.html"
    url = "https://www.prada.com/us/en/store-locator.glb.getStores.json"

    test = session.get(base_url, headers = HEADERS)
    time.sleep(randint(4,8))
    js = session.get(url, headers = HEADERS)
    soup = BeautifulSoup(js.text,"lxml")
    results = json.loads(soup.text)

    data = []
    for poi in results:
        if poi == "status":
            continue
        try:
            result = results[poi][0]
        except:
            result = results[poi]
        
        i = []
        i.append("prada.com")
        i.append(base_url)
        i.append(result.get('Description', [])[0].get('displayStoreName'))
        i.append(result.get('addressLine', [])[0].replace("Bal Harbour FL 33154","").strip())
        i.append(result.get('city', ''))
        i.append(result.get('stateOrProvinceName', ''))
        i.append(result.get('postalCode', '').strip())
        i.append(result.get('country', ''))
        i.append(result.get('uniqueID',''))
        i.append(result.get('telephone1', '').strip())
        i.append("<MISSING>")
        i.append(result.get('latitude', ''))
        i.append(result.get('longitude', ''))
        i.append(''.join([k + ": " + v for k, v in result.get('workingSchedule', {}).items()]).strip().replace(" --","Closed"))
        data.append(i)

    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()

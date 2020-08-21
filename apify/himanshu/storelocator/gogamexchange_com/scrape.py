import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import io
import json
session = SgRequests()
def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    address = []
    headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    base_url = "https://www.gogamexchange.com/"
    db =  'https://cdn.storelocatorwidgets.com/json/7466089a00db248cead92022a5760e27?callback=slw&_=1597988807080'
    r = session.get(db, headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    data_8 = (soup.text.replace('"filters":""})','"filters":""}').replace('slw({','{'))
    json_data = json.loads(data_8)
    for val in (json_data['stores']):
        hours_of_operation  = "Monday : "+str(val['data']['hours_Monday'])+", Tuesday : "+str(val['data']['hours_Tuesday'])+", Wednesday : "+str(val['data']['hours_Wednesday'])+", Thursday : "+str(val['data']['hours_Thursday'])+", Friday : "+str(val['data']['hours_Friday'])+", Saturday : "+str(val['data']['hours_Saturday'])+", Sunday : "+str(val['data']['hours_Sunday'])
        data_8 = val['data']['address']
        city_state = val['name'].split(",")
        street_adress = " ".join(data_8.split(",")[:-2]).replace(city_state[0],"").strip()
        if "Horn Lake, MS" in val['name']:
            street_adress = "904 Goodman Ave"
        if "Jackson, TN" in val['name']:
            street_adress = "1936 N. Highland"
        store = []
        store.append(base_url)
        store.append(val['name'])
        store.append(street_adress)
        store.append(city_state[0])
        store.append(city_state[1].strip())
        store.append(data_8.split(",")[-1].split(" ")[-1].replace("TN","").replace("TX",""))
        store.append("US")
        store.append(val['storeid'])
        store.append(val['data']['phone'])
        store.append("<MISSING>")
        store.append(val['data']['map_lat'])
        store.append(val['data']['map_lng'])
        store.append(hours_of_operation)
        store.append(val['data']['website'])
        if store[2] in address :
            continue
        address.append(store[2])
        yield store
def scrape():
    data = fetch_data()
    write_output(data)
scrape()

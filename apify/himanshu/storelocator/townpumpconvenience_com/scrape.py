import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('townpumpconvenience_com')


session = SgRequests()
def write_output(data):
    with open('data.csv', mode='w',encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    base_url = "https://www.townpump.com"
    r = session.get("https://www.townpump.com/locations",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    web_id = soup.find("script",{"id":"storelocatorscript"})["data-uid"]
    location_request = session.get("https://cdn.storelocatorwidgets.com/json/" + web_id , headers=headers)
    data = json.loads(location_request.text.split("slw(")[1].split("]})")[0] + "]}")["stores"]
    return_main_object = []
    for i in range(len(data)):
        store_data = data[i]
        filters = store_data["filters"]
        if "Convenience Store" not in filters:
            continue
        address = store_data["data"]["address"].split(',')
        if "United States" in address:
            address.remove(' United States')
        zipp_list = re.findall(re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str(" ".join(address[1:])))
        if zipp_list :
            zipp = zipp_list[0].strip()
        else:
            zipp = "<MISSING>"
        if len(address) == 4:

            if "Suite 1" not in address[1]:
                street_address = address[0].strip()
                city = address[1].strip()
                state = address[-2].strip()
            else:
                street_address = address[0] + " "+ address[1]
                city = address[2].strip()
                state = address[-1].strip()
        elif len(address) ==3:
            state_tag = re.findall(r'([A-Z]{2})', str("".join(address)))
            if state_tag :
                if "US" in " ".join(state_tag):
                    state_tag.remove("US")
                state = state_tag[-1].strip()
                street_address = address[0].strip()
                if "MT" not in address[1]:

                    city = address[1].strip()
                else:
                    city = " ".join(address[0].split()[-2:]).strip()
            else:
                state = "<MISSING>"
                street_address = " ".join(address[:2]).strip()
                #logger.info(street_address)
                city = address[-1].strip()
        elif len(address) == 2:
            state= re.findall(r'([A-Z]{2})', str("".join(address[-1].split()[-1])))[0]
            if "Suite 1" not in address[-1]:
                street_address = " ".join(address[0].split()[:-1]).strip()
                city = address[0].split()[-1].strip()
            else:
                street_address = address[0].strip() + " "+" ".join(address[-1].split(' ')[:-2]).strip()
                city =address[-1].split(' ')[-2].strip()
        else:
            city = ("".join(address).split("MT")[0].split(" ")[-2])
            street_address =" ".join("".join(address).split("MT")[0].split(" ")[:-2]) 
            state = "MT"
        data_8 = store_data['name'].split("St")[0]
        store = []
        store.append("https://www.townpumpconvenience.com")
        store.append(store_data['name'])
        store.append(street_address.replace("6940 MT-1","6940 MT-1 Suite A").replace("20A Big Timber Loop Rd","20A Big Timber Loop Rd Suite c"))
        store.append(city.replace("Suite C","Big Timber").replace("Suite A","Anaconda"))
        store.append(state.replace("Anaconda","MT").replace("Big Timber","MT"))
        store.append(zipp)
        store.append("US")
        store.append(store_data["storeid"])
        store.append(store_data["data"]["phone"] if "phone" in store_data["data"] and store_data["data"]["phone"] != "" and store_data["data"]["phone"] != None else "<MISSING>")
        store.append(data_8.strip())
        store.append(store_data["data"]["map_lat"])
        store.append(store_data["data"]["map_lng"])
        store.append("<MISSING>")
        store.append("https://www.townpump.com/locations")
        return_main_object.append(store)
    return return_main_object
def scrape():
    data = fetch_data()
    write_output(data)
scrape()

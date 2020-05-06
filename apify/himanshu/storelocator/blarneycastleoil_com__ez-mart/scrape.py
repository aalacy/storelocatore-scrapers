import csv
from bs4 import BeautifulSoup
import json
from sgrequests import SgRequests

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
    addresses = []
    headers = {'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',
    }
    r =  session.get("http://blarneycastleoil.com/ez-mart-promo/ez-mart-locations/", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")   
    links = soup.find_all("script",{"type":"text/javascript"})[-3]
    mp = (links.text.split('{"KOObject":')[1].split(',"pluginurl":')[0]) 
    json_data = json.loads(mp)
    for data1 in json_data:
        for mp1 in (data1['locations']):

            soup = BeautifulSoup(mp1['description'], "lxml")
            
            addr = list(soup.find_all("p")[-1].stripped_strings)
            if len(addr) == 2:
                city = addr[-1].split(",")[0]
                state = addr[-1].replace("Bellaire MI 49614","Bellaire, MI 49614").split(",")[1].split(" ")[1]
                zipp = addr[-1].replace("Bellaire MI 49614","Bellaire, MI 49614").split(",")[1].split(" ")[2]
            elif len(addr) == 4:
                street_address = addr[0]
                city = addr[1]
                state = "<MISSING>"
                zipp = addr[2]
            else:
                if "EZ" in addr[0] or "E-Z" in addr[0]:
                    del addr[0]
                street_address = " ".join(addr[:-3])
                city = addr[-3]
                state = "<MISSING>"
                zipp = addr[-2]
        
            store = []
            store.append("https://blarneycastleoil.com/")
            store.append(mp1['title'])
            store.append(street_address)
            store.append(city)
            store.append(state)
            store.append(zipp)
            store.append("US")
            store.append(mp1['cssClass'].split("-")[-1])
            store.append("<MISSING>")
            store.append("EZ Mart")
            store.append(mp1['latitude'])
            store.append(mp1['longitude'])
            store.append("<MISSING>")
            store.append("http://blarneycastleoil.com/ez-mart-promo/ez-mart-locations/")
            # if store[2] in addresses:
            #     continue
            # addresses.append(store[2])
            yield store
def scrape():
    data = fetch_data()
    write_output(data)
scrape()

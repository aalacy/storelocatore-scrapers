import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json

session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36',
    }
    address =[]
    base_url= "https://champps.com/location-search/"
    r = session.get(base_url)
    soup= BeautifulSoup(r.text,"lxml")
    a1 = soup.find_all("script",{"type":"text/javascript"})
    for a in a1:
        if 'long"' in str(a):
            a1 = a
            break

    p1 = a1.text.replace("\/","").split('var mapdata = ')[1].split("var layout =")[0].replace(";","")
    p = json.loads(p1)
    for index,o in enumerate(p['markers']):
        if index > 0:
            location_name = p['markers'][o]['name']
            # print(location_name)
            street_address = p['markers'][o]['address']+" "+p['markers'][o]['address2']
            city = p['markers'][o]['city']
            state = p['markers'][o]['state']
            zipp = p['markers'][o]['zip']
            store_number = p['markers'][o]['id']
            phone = p['markers'][o]['tel']
            latitude = p['markers'][o]['lat']
            longitude = p['markers'][o]['long']
            link1 = p['markers'][o]['path']
            page_url = "https://champps.com/"+str(link1)
            # print(page_url)
            r1 = session.get(page_url)
            try:
                soup1 = BeautifulSoup(r1.text, "lxml")
                hours_of_operation = ""
                raw_hours = soup1.find_all(style="text-align: center;")[1:]
                for hour in raw_hours:
                    hours_of_operation = (hours_of_operation + " " + hour.text.replace("\xa0"," ").replace("\n"," ").replace("–","-").strip()).strip()
            except:
                hours_of_operation = "<MISSING>"
            if not hours_of_operation:
                hours_of_operation = "<MISSING>"
            store = []
            store.append("https://champps.com/")
            store.append(location_name)
            store.append(street_address)
            store.append(city)
            store.append(state)
            store.append(zipp)
            store.append("US")
            store.append(store_number)
            store.append(phone)
            store.append("<MISSING>")
            store.append(latitude)
            store.append(longitude)
            store.append(hours_of_operation)
            store.append(page_url) 
            if store[2] in address :
                continue
            address.append(store[2])
            yield store
def scrape():
    data = fetch_data()
    write_output(data)
scrape()

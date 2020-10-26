import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json



session = SgRequests()

def write_output(data):
    with open('data.csv', 'w') as output_file:
        writer = csv.writer(output_file, delimiter=",")

        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])

        # print("data::" + str(data))
        for i in data or []:
            writer.writerow(i)


def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }
    
    r = session.get("https://saintspub.com/", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    field = soup.find_all("div",{"class":"et_pb_blurb_container"})
    for i in field:
        location_name = i.find("h4",{"class":"et_pb_module_header"}).find("span").text
        addr = list(i.find("div",{"class":"et_pb_blurb_description"}).stripped_strings)
        street_address = addr[1].split(",")[0].strip()
        city = addr[1].split(",")[1].strip()
        state = addr[1].split(",")[2].strip()
        phone = addr[3]
        location_type = addr[0]
        hours_of_operation = addr[2]

        store=[]
        store.append("https://saintspub.com")
        store.append(location_name if location_name else '<MISSING>')
        store.append(street_address if street_address else '<MISSING>')
        store.append(city if city else '<MISSING>')
        store.append(state if state else '<MISSING>')
        store.append('<MISSING>')
        store.append('US')
        store.append('<MISSING>')
        store.append(phone if phone else '<MISSING>')
        store.append(location_type)
        store.append('<MISSING>')
        store.append('<MISSING>')
        store.append(hours_of_operation)
        store.append('<MISSING>')
        store = [x.replace("–","-") if type(x) == str else x for x in store]
        store = [x.encode('ascii', 'ignore').decode('ascii').strip() if type(x) == str else x for x in store]
        yield store



def scrape():
    # fetch_data()
    data = fetch_data()
    write_output(data)
scrape()

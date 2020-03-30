import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json


session = SgRequests()
def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    base_url = "https://www.westerndental.com/"
    r = session.get("https://www.westerndental.com/en-us/find-a-location", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    
    json_data = json.loads(soup.find(lambda tag: (tag.name == "script") and "ItemID" in tag.text).text.split("var locationsInit =")[1].split("|| [];")[0])
    for data in json_data:
        location_name = data['Name']
        street_address = data['Address']
        city = data['City']
        state = data['State']
        zipp = data['Zipcode']
        store_number = data['StoreID']
        phone = data['Phone']
        latitude = data['Latitude']
        longitude = data['Longitude']
        location_type = data['LocationType'].replace("WD.","").capitalize().replace("and"," and ")
        page_url = "https://www.westerndental.com/en-us"+str(data['NodeAliasPath'])
        r1 = session.get(page_url, headers=headers)
        soup1 = BeautifulSoup(r1.text, "lxml")
        hours = " ".join(list(soup1.find("table").stripped_strings))

    
        store = []
        store.append(base_url)
        store.append(location_name)
        store.append(street_address)
        store.append(city)
        store.append(state)
        store.append(zipp)
        store.append("US")
        store.append(store_number)
        store.append(phone)
        store.append(location_type)
        store.append(latitude)
        store.append(longitude)
        store.append(hours)
        store.append(page_url)
        # print("data ==="+str(store))
        # print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~````")
        yield store

def scrape():
    data = fetch_data()
    write_output(data)


scrape()

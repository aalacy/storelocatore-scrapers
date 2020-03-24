import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import phonenumbers

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
    # driver = get_driver()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'origin': 'https://www.oreck.com',
        'referer': 'https://www.oreck.com/stores/',
        
    }
    base_url = "https://www.oreck.com/"
    data = {"dwfrm_storelocator_countryCode": "US",
            "dwfrm_storelocator_distanceUnit": "mi",
            "dwfrm_storelocator_postalCode": "85029",
            "dwfrm_storelocator_maxdistance": "999999",
            "dwfrm_storelocator_findbyzip": "Search by Zip"}
    r = session.post("https://www.oreck.com/stores-results/", data=data, headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    for loc in soup.find("div",{"class":"store-location-results"}).find_all("tr"):
        location_name = loc.find("td",{"class":"quarter dealer-name"}).text.strip()
        addr = list(loc.find_all("td")[1].stripped_strings)
        street_address = " ".join(addr[0].split("\n")[:-3])
        city = addr[0].split("\n")[-3].replace(",","").strip()
        state = addr[0].split("\n")[-2]
        zipp = addr[0].split("\n")[-1]
        phone = loc.find_all("td")[-1].text.strip()
        location_type = "Authorized Dealers & Distributors"
        store = []
        store.append(base_url)
        store.append(location_name)
        store.append(street_address)
        store.append(city)
        store.append(state)
        store.append(zipp)
        store.append("US")
        store.append("<MISSING>")
        store.append(phone)
        store.append(location_type)
        store.append("<MISSING>")
        store.append("<MISSING>")
        store.append("<MISSING>")
        store.append("<MISSING>")
        # print("data ==="+str(store))
        # print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~````")
        yield store

    for data in json.loads(soup.find("div",{"class":"store-map-embed js-map-results-container"})['data-stores']):
        
        location_name = data['name']
        street_address = (data['address1'] +" "+ str(data['address2'])).strip()
        city = data['city']
        state = data['stateCode']
        zipp = data['postalCode']
        phone = data['phone']
        latitude = data['latitude']
        longitude = data['longitude']
        location_type = "Exclusive Oreck Dealers"
        page_url = "https://www.oreck.com/stores-details/?StoreID="+str(data['id'])
        r1 = session.get(page_url)
        soup1 = BeautifulSoup(r1.text, "lxml")
        # print(page_url)
        try:
            hours = " ".join(list(soup1.find("div",{"class":"store-hours"}).stripped_strings)).replace("|"," ").replace("/td>","").replace(">","").strip()
        except:
            hours = "<MISSING>"

    
        store = []
        store.append(base_url)
        store.append(location_name)
        store.append(street_address)
        store.append(city)
        store.append(state)
        store.append(zipp)
        store.append("US")
        store.append("<MISSING>")
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

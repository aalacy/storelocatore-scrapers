import csv
import requests
from bs4 import BeautifulSoup
import re
import json
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('coop_co_uk')




def write_output(data):
    with open('data.csv', mode='w', newline='') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)



def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }
    base_url = "https://finder.coop.co.uk/food/counties"
    addresses = []
    session = SgRequests()
    r1 = session.get(base_url)
    soup = BeautifulSoup(r1.text,"lxml")
    state = soup.find_all("ul",{"class":"three-column list-bare"})
    for data in state:
        for href in data.find_all("li"):
            r2 = session.get("https://finder.coop.co.uk"+href.find("a")['href'])
            soup1 = BeautifulSoup(r2.text,"lxml")
            for citys in (soup1.find_all("ul",{"class":"three-column list-bare"})):
                for li in citys.find_all("li"):
                    r3 = session.get("https://finder.coop.co.uk"+li.find("a")['href'])
                    soup3 = BeautifulSoup(r3.text,"lxml")
                    data = json.loads(re.sub(r'\s+'," ",soup3.find(lambda tag:(tag.name == "script") and "streetAddress" in tag.text).text))
                    page_url = "https://finder.coop.co.uk"+li.find("a")['href']
                    location_name = data['name']
                    street_address = data['address']['streetAddress']
                    city = data['address']['addressLocality']
                    state = data['address']['addressRegion']
                    zipp = data['address']['postalCode']
                    store_number = soup3.find("main",{"id":"main"}).attrs['data-store-id']
                    phone = data['telephone']
                    location_type = data['@type']
                    latitude = data['geo']['latitude']
                    longitude = data['geo']['longitude']
                    try:
                        hours = soup3.find("div",{"id":"store-hours"}).text.strip().replace("\n"," ")
                    except:
                        hours ='<MISSING>'
                    
                    store =[]
                    store.append("https://www.coop.co.uk")
                    store.append(location_name)
                    store.append(street_address)
                    store.append(city)
                    store.append(state)
                    store.append(zipp)
                    store.append("UK")
                    store.append(store_number)
                    store.append(phone.strip() if phone.strip() else "<MISSING>")
                    store.append(location_type)
                    store.append(latitude)
                    store.append(longitude)
                    store.append(hours if hours.strip() else "<MISSING>")
                    store.append(page_url)
                    if store[2] in addresses:
                        continue
                    addresses.append(store[2])
                    store = [str(x).strip() if x else "<MISSING>" for x in store]
                    # logger.info("~~~~~~~~~~~~~~~~~~~~  ",store)
                    yield store

    
def scrape():
    data = fetch_data()
    write_output(data)


scrape()



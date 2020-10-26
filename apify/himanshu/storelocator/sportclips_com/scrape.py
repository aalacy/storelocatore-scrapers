import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import unicodedata
import time
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('sportclips_com')


session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    # addresses = []
    # r_headers = {
    #     'Accept': '*/*',
    #     'Accept-Encoding':'gzip, deflate, br',
    #     'Accept-Language': 'en-US,en;q=0.9,gu;q=0.8',
    #     'Content-Type': 'application/json; charset=UTF-8',    
    #     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36',
    # }
    base_url = "https://sportclips.com"
    r = session.get("https://sportclips.com/all-locations")
    addressesess=[]
    soup = BeautifulSoup(r.text, "lxml")
    for anchor in soup.find_all("div",{"class":"locations-list locations-list-noicon"}):
        # logger.info(len())
        for coming in anchor.find_all("p"):
            the_word='COMING SOON!'
            words = coming.find(text=lambda text: text and the_word in text)
            if words==None:
                for index,link in enumerate(coming.find_all("a")):
                    if "google" in link['href']:
                        continue
                    if "products" in link['href']:
                        continue
                    page_url = link['href'].replace("www.",'')
                    # logger.info(link)
                    try:
                        r1 = session.get(page_url)
                    except:
                        pass

                    soup1 = BeautifulSoup(r1.text, "lxml")

                    try:
                        location_name = soup1.find("div",{"class":"contact-location"}).find("h1").text.strip()
                        json_data = json.loads(soup1.find(lambda tag: (tag.name == "script") and "@context" in tag.text).text.replace("\t","").strip())
                        hours_of_operation = " ".join(list(soup1.find("table").stripped_strings))
                    except:
                        location_name=''

                    
                    street_address = json_data['address']['streetAddress']
                    city = json_data['address']['addressLocality']
                    state = json_data['address']['addressRegion']
                    zipp = json_data['address']['postalCode']
                    phone = json_data['telephone']
                    location_type = json_data['@type']
                    latitude = json_data['geo']['latitude']
                    longitude = json_data['geo']['longitude']

                    
                
                    store = []
                    store.append(base_url)
                    store.append(location_name)
                    store.append(street_address)
                    store.append(city)
                    store.append(state)
                    store.append(zipp if zipp else "<MISSING>")
                    store.append("US")
                    store.append("<MISSING>")
                    store.append(phone)
                    store.append(location_type)
                    store.append(latitude)
                    store.append(longitude)
                    store.append(hours_of_operation)
                    store.append(page_url)
                    # store = [x.replace("–","-") if type(x) == str else x for x in store]
                    store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
                    if store[2] in addressesess:
                        continue
                    addressesess.append(store[2])
                    # logger.info("data == "+str(store))
                    # logger.info("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
                    yield store
            
def scrape():
    data = fetch_data()
    write_output(data)

scrape()

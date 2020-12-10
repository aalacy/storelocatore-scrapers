import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
# import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('medpost_com')


session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w', newline='') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    addresses = []
    base_url = "http://medpost.com"
   
    r = session.get("https://www.carespot.com/locations/")
    soup = BeautifulSoup(r.text, "lxml")
    for st_id in soup.find("select",{"name":"state"}).find_all("option")[1:]:
        state_url = session.get("https://www.carespot.com/locations/"+str(st_id['alt'].lower()))
        state_soup = BeautifulSoup(state_url.text, "lxml")

        for link in state_soup.find_all("a",{"class":"post"}):
            page_url = link['href']

            location_r = session.get(page_url)
            location_soup = BeautifulSoup(location_r.text, "lxml")
            if location_soup.find("p",{"class":"subtitle"}) and  location_soup.find("p",{"class":"subtitle"}) == "Coming Soon!":
                continue
            
            location_name = location_soup.find("h1").text
            
            street_address = location_soup.find("span",{"itemprop":"streetAddress"}).text.split("Suite")[0].replace(",","").strip()
            city = location_soup.find("span",{"itemprop":"addressLocality"}).text
            state = location_soup.find("span",{"itemprop":"addressRegion"}).text
            zipp = location_soup.find("span",{"itemprop":"postalCode"}).text
            phone = location_soup.find("span",{"itemprop":"telephone"}).text
            location_type = page_url.split("/")[-3].strip().replace("-"," ").capitalize()
            coord = location_soup.find("div",{"class":"phone-directions"}).find_all("a")[-1]['href']
            
            latitude = coord.split("=")[1].split(",")[0]
            longitude = coord.split("=")[1].split(",")[1]
            try:
                hours = " ".join(list(location_soup.find("div",{"class":"hours"}).stripped_strings)).replace("Location Hours","")
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
            store = [str(x).strip() if x else "<MISSING>" for x in store]
            if store[2] in  addresses:
                continue
            addresses.append(store[2])
            # logger.info("data == "+str(store))
            # logger.info("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
            yield store
        
def scrape():
    data = fetch_data()
    write_output(data)

scrape()

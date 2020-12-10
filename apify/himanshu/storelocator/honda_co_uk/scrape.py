
import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import re
import json
from datetime import datetime
session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w', newline='') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data(): 
    
    
    base_url = "https://www.honda.co.uk"
    for link in ['https://www.honda.co.uk/cars/dealer-list.html','https://www.honda.co.uk/motorcycles/dealer-list.html','https://www.honda.co.uk/marine/dealer-list.html']:
        soup = bs(session.get(link).text, "lxml")

        for url in soup.find_all("td",{"class":"wrapperInner"}):
            page_url = base_url + url.a['href']
            if session.get(page_url).status_code == 404:
                continue
        
            location_soup = bs(session.get(page_url).text, "lxml")

            location_name = location_soup.find("h1",{"itemprop":"name"}).text
            
            street_address = ''

            for address in location_soup.find_all("span",{"itemprop":"streetAddress"}):
                street_address+= " "+ address.text
            city = location_soup.find("span",{"itemprop":"addressLocality"}).text
            try:
                state = location_soup.find("span",{"itemprop":"addressRegion"}).text.replace(".","")
            except:
                state = "<MISSING>"
            zipp = location_soup.find("span",{"itemprop":"postalCode"}).text
            try:
                phone = location_soup.find("span",{"itemprop":"telephone"}).text.strip()
            except:
                phone = "<MISSING>"

            coord = location_soup.find("div",{"class":"dealerMap"})['data-mapdata']
            store_number = coord.split("/")[-1].split(".")[0][3:]
            lat = coord.split("lat=")[1].split("&")[0]
            lng = coord.split("lng=")[-1]
            try:
                hours = " ".join(list(location_soup.find("div",{"class":"wrapperInner dealerColDetails"}).stripped_strings))
            except:
                hours = "<MISSING>"
            
            if "Erdington" in street_address:
                street_address = street_address.replace("Erdington","").strip()
                city = "Erdington"
                state = "Birmingham"
            if "Wandsworth" in street_address:
                street_address = "60-62 West Hill Road"
                city = "Wandsworth"
                state = "London"
            store = []
            store.append(base_url)
            store.append(location_name)
            store.append(street_address)
            store.append(city)
            store.append(state)
            store.append(zipp)   
            store.append("UK")
            store.append("<MISSING>")
            store.append(phone)
            store.append("<MISSING>")
            store.append(lat)
            store.append(lng)
            store.append(hours)
            store.append(page_url)     
        
            store = [str(x).replace("–","-").strip() if x else "<MISSING>" for x in store]
            
            yield store
      
    
    
def scrape():
    data = fetch_data()
    write_output(data)

scrape()

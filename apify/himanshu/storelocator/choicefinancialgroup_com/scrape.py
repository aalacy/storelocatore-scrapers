import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json


session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w',encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    base_url = "https://choicefinancialgroup.com"

    # Bank Location
    r = session.get("https://bankwithchoice.com/contact/locations/",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    
    for location in soup.find_all("div",{'class':"col-lg-3 col-md-6 bucket-content"}):
        location_details = list(location.find("p").stripped_strings)
    
        for i in range(len(location_details)):
            if "Hours" in location_details[i] or "Lobby" in location_details[i]:
                hours = " ".join(location_details[i:]).split("Night")[0]
                break
        store = []
        store.append("https://choicefinancialgroup.com")
        store.append(location.find("a").text.strip())
        store.append(location_details[0].split("–")[0].strip())
        store.append(location_details[0].split("–")[1].split(",")[0].strip())
        store.append(location_details[0].split("–")[1].split(",")[1].split()[0])
        store.append(location_details[0].split("–")[1].split(",")[1].split()[1])
        store.append("US")
        store.append("<MISSING>")
        store.append(location_details[2])
        store.append("choice bank")
        if location.find("a") != None:
            geo_location = location.find("a")["href"]
            store.append(geo_location.split("/@")[1].split(",")[0] if len(geo_location.split("/@")) == 2 else "<MISSING>")
            store.append(geo_location.split("/@")[1].split(",")[1] if len(geo_location.split("/@")) == 2 else "<MISSING>")
        else:
            store.append("<MISSING>")
            store.append("<MISSING>")
        store.append(hours)
        store.append("https://bankwithchoice.com/contact/locations/")
        yield store
    

    # ATM location

    atm_soup = BeautifulSoup(session.get("https://bankwithchoice.com/contact/atm/").text, "lxml")
    for link in atm_soup.find("div",{"class":"masonry-blocks-container"}).find_all("a"):
        address = link.parent.text
        location_name = address.split("(")[1].replace(")","").strip()
        street_address = address.split("(")[0].replace("Map","").strip()
        addr = link['href'].split("q=")[1].replace("+"," ").replace("%2C",",")
        city = addr.split(",")[1]
        state = addr.split(",")[2].split()[0]
        zipp = addr.split(",")[2].split()[1]

        store = []
        store.append(base_url)
        store.append(location_name)
        store.append(street_address)
        store.append(city)
        store.append(state)
        store.append(zipp)   
        store.append("US")
        store.append("<MISSING>")
        store.append("<MISSING>")
        store.append("Choice Bank ATM")
        store.append("<MISSING>")
        store.append("<MISSING>")
        store.append("<MISSING>")
        store.append("https://bankwithchoice.com/contact/atm/")    
        yield store 

def scrape():
    data = fetch_data()
    write_output(data)

scrape()

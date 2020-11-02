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
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    base_url = "https://shsalons.com"
    r = session.get("https://shsalons.com/",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    for location in soup.find("a",text="LOCATIONS").parent.find_all("a"):
        if "/pages/locations" in location["href"]:
            continue
        location_request = session.get(base_url + location["href"],headers=headers)
        location_soup = BeautifulSoup(location_request.text,"lxml")
        hours = " ".join(list(location_soup.find("p",{'data-pf-type':"Paragraph"}).stripped_strings))
        location_details = list(location_soup.find_all("p",{'data-pf-type':"Paragraph"})[-1].stripped_strings)
        if "USA" not in location_details[2]:
            location_details[1] = location_details[1] + " " + location_details[2]
            del location_details[2]
        location_details[2] = location_details[2].replace("USA","")
        state_split = re.findall("([A-Z]{2})",location_details[2])
        if state_split:
            state = state_split[-1]
        else:
            state = "<MISSING>"
        store_zip_split = re.findall(r"\b[0-9]{5}(?:-[0-9]{4})?\b",location_details[2])
        if store_zip_split:
            store_zip = store_zip_split[-1]
        else:
            store_zip = "<MISSING>"
        store = []
        store.append("https://shsalons.com")
        store.append(location.text.capitalize())
        store.append(location_details[1].replace("Add: ",""))
        store.append(location_details[2].split(",")[0])
        store.append(state)
        store.append(store_zip)
        store.append("US")
        store.append("<MISSING>")
        phone_split = re.findall(re.compile(".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"),location_details[0])
        if phone_split:
            phone = phone_split[-1]
        else:
            phone = "<MISSING>"
        store.append(phone)
        store.append("<MISSING>")
        geo_lcoation = json.loads(location_soup.find("div",{"class":"gmap2"})["data-gmap"])
        store.append(geo_lcoation["lat"])
        store.append(geo_lcoation["long"])
        store.append(hours)
        store.append(base_url + location["href"])
        yield store
    
def scrape():
    data = fetch_data()
    write_output(data)

scrape()

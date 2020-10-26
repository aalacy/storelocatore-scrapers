import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import re
import json


session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w',encoding="utf-8", newline='') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    base_url = "https://fastautoloansvirginiainc.com"

    soup = bs(session.get("https://fastautoloansvirginiainc.com/sitemap.xml").text, "lxml")
    
    for url in soup.find_all("loc"):

        if "virginia-title-loan-locations" in url.text:

            page_url = url.text
            
            location_soup = bs(session.get(page_url).text, "lxml")
            try:
                json_data = json.loads(location_soup.find(lambda tag: (tag.name == "script") and "streetAddress" in tag.text).text)
            except:
                continue
            street_address = json_data['address']['streetAddress']
            city = json_data['address']['addressLocality']
            state = json_data['address']['addressRegion']
            zipp = json_data['address']['postalCode']

            location_name = "Title Loans Are Here At {0}, {1}".format(city,state.upper())
            phone = json_data['telephone']
            coords = location_soup.find("a",href = re.compile("https://www.google.com/maps/place"))['href']
            lat = coords.split("@")[1].split(",")[0]
            lng = coords.split("@")[1].split(",")[1]
            
            try:
                hours = " ".join(list(location_soup.find("span",{"class":"s1"}).stripped_strings))
            except:
                hours = "<MISSING>"
            
            store_number = page_url.split("/")[4].replace("va","")
            
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
            store.append("<MISSING>")
            store.append(lat)
            store.append(lng)
            store.append(hours)
            store.append(page_url)
            store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
           
            yield store

            

def scrape():
    data = fetch_data()
    write_output(data)

scrape()

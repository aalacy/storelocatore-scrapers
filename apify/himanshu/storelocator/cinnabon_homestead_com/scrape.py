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
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)
def fetch_data():
    base_url= "http://cinnabon.homestead.com/Locations.html"
    r = session.get(base_url)
    soup= BeautifulSoup(r.text,"lxml")
    link = soup.find_all("div",{"id":"element496"})
    city1 = list(link[0].stripped_strings)[1:]
    r1 = session.get(base_url)
    soup1 = BeautifulSoup(r1.text, "lxml")
    link1 = soup1.find_all("div", {"id": "element497"})
    location_name1 = list(link1[0].stripped_strings)
    r2 = session.get(base_url)
    soup2 = BeautifulSoup(r2.text, "lxml")
    link2 = soup2.find_all("div", {"id": "element499"})
    phone1 = list(link2[0].stripped_strings)[0:]
    for q in range(len(location_name1)):
        st = location_name1[q]
        phone = phone1[q]
        city = city1[q].replace("Nova Scotia","Dartmouth")
        if "Dartmouth" in city:
            state = "Nova Scotia" 
        else:
            state = "Ontario"
        store = []
        store.append("http://cinnabon.homestead.com/")
        store.append(st.encode('ascii', 'ignore').decode('ascii').strip())
        store.append("<MISSING>")
        store.append(city.encode('ascii', 'ignore').decode('ascii').strip())
        store.append(state.encode('ascii', 'ignore').decode('ascii').strip())
        store.append("<MISSING>")
        store.append("CA")
        store.append("<MISSING>")
        store.append(phone.encode('ascii', 'ignore').decode('ascii').strip())
        store.append("<MISSING>")
        store.append("<MISSING>")
        store.append("<MISSING>")
        store.append("<MISSING>")
        # print(store)
        store.append(base_url)
        
        yield store
def scrape():
    data = fetch_data()
    write_output(data)
scrape()

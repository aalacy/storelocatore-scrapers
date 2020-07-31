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
    base_url= "https://www.grifolsplasma.com/en/locations/find-a-donation-center"
    r = session.get(base_url)
    soup= BeautifulSoup(r.text,"lxml")
    address = []
    store_name=[]
    store_detail=[]
    return_main_object=[]
    k= soup.find_all("div",{"class":"all-centers-grid-block"})
    for l in k:
        d = (l.find_all("a"))
        for g in d:
            link = (g['href'])
            # print(link)
            r1 = session.get(link)
            soup1 = BeautifulSoup(r1.text,"lxml")
            if "https://www.grifolsplasma.com/en/-/sanantonio-tx" in link:
                continue
            # try:
            location_name = (soup1.find("div",{"class":"center-address"}).find("h2").text)
            street_address = soup1.find("div",{"class":"center-address"}).find("p").text
            city1 = soup1.find("div",{"class":"center-address"}).find_all("p")[1].text
            zipp = (city1.split(",")[-1].strip())
            city = (city1.split(",")[0].strip())
            state = (city1.split(",")[1].strip())
            phone = soup1.find("div",{"class":"center-address"}).find_all("p")[-1].text.replace("\n","").replace("\r","").replace("\t","").strip()
            hours_of_operation = soup1.find("div",{"class":"center-column-2"}).text.strip().replace("PM","PM ").replace("Hours","").strip().replace("Closed","Closed ").split(" Labor Day")[0].split(" Thanks")[0]
            location_type = location_name.split(" ")[0]
            # print(location_type)
            store = []
            store.append("https://www.biotestplasma.com/")
            store.append(location_name if location_name else "<MISSING>") 
            store.append(street_address if street_address else "<MISSING>")
            store.append(city if city else "<MISSING>")
            store.append(state if state else "<MISSING>")
            store.append(zipp if zipp else "<MISSING>")
            store.append("US")
            store.append("<MISSING>") 
            store.append(phone if phone else "<MISSING>")
            store.append(location_type.replace("TPR","Talecris Plasma Resources").replace("PlasmaCare","Plasma Care").replace("Biomat","Biomat USA"))
            store.append("<MISSING>")
            store.append("<MISSING>")
            store.append(hours_of_operation if hours_of_operation else "<MISSING>")
            store.append(link if link else "<MISSING>")
            if store[2] in address :
                continue
            address.append(store[2])
            yield store
def scrape():
    data = fetch_data()
    write_output(data)
scrape()

import csv
from  sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
session = SgRequests()


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():

    base_url = "https://www.bossplow.com"
    r = session.get("https://www.bossplow.com/en/dealer-directory")
    soup1 = BeautifulSoup(r.text, "lxml")
    for link in soup1.find("div", {"class":"col-xs-12"}).find_all("a"):
        if link['href'].count('/') !=5:
            continue    
        page_url = base_url + link['href']
        # print(page_url)
        r1 = session.get(page_url)
        soup = BeautifulSoup(r1.text, "lxml")
        location_name = soup.find("h3").text.strip()
        addr = list(soup.find("address").stripped_strings)
        street_address = addr[0].split("|")[0].strip()
        city = addr[0].split("|")[1].split(",")[0].strip()
        state = addr[0].split("|")[1].split(",")[1].split(" ")[1]
        zipp = " ".join(addr[0].split("|")[1].split(",")[1].split(" ")[2:]).upper()
        if zipp == "UB11 1FW":
            continue
        # print(zipp)
        if zipp.replace('-','').isdigit():
            country_code = "US"
        else:
            country_code = "CA"
        try:
            phone = addr[1]
        except:
            phone = "<MISSING>"
        store_number = page_url.split("/")[-1]
        if soup.find("ul",{"class":"list-hours"}):
            hours = " ".join(list(soup.find("ul",{"class":"list-hours"}).stripped_strings))
        else:
            hours = "<MISSING>"
    
        store = []
        store.append(base_url )
        store.append(location_name if location_name else '<MISSING>')
        store.append(street_address if street_address else '<MISSING>')
        store.append(city if city else '<MISSING>')
        store.append(state if state else '<MISSING>')
        store.append(zipp if zipp else '<MISSING>')
        store.append(country_code if country_code else '<MISSING>')
        store.append(store_number if store_number else '<MISSING>')
        store.append(phone if phone else '<MISSING>')
        store.append('<MISSING>')
        store.append('<MISSING>')
        store.append('<MISSING>')
        store.append(hours if hours else '<MISSING>')
        store.append(page_url)
       # print("data ===="+str(store))
        #print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~`")
        yield store
             
def scrape():
    data = fetch_data()

    write_output(data)


scrape()

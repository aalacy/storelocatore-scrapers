import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8", newline='') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    headers = {
             'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.79 Safari/537.36',    
    }

    base_url = "https://fundltc.com/"   
    

    r = session.get("https://fundltc.com/Healthcare%20Facility%20Locator/Facility_Locator.aspx", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    for link in soup.find("table",{"width":"100%"}).find_all("a"):
        page_url = link['href']
        # print(page_url)
        store_number = page_url.split("=")[-1]

        location_r = session.get(page_url)
        location_soup = BeautifulSoup(location_r.text, "lxml")

        location_name = location_soup.find("span",{"id":"ctl00_ctl00_cphRight_cphText_lblFacilityName"}).text
        addr = list(location_soup.find("span",{"id":"ctl00_ctl00_cphRight_cphText_lblAddress"}).stripped_strings)
        try:
            street_address = addr[0]
        except:
            # print("No data..skipping")
            continue
        city = addr[1].split(",")[0]
        state = addr[1].split(",")[1].split(" ")[1]
        zipp = addr[1].split(",")[1].split(" ")[2]
        phone = location_soup.find("span",{"id":"ctl00_ctl00_cphRight_cphText_lblPhone"}).text

        store = []
        store.append(base_url)
        store.append(location_name)
        store.append(street_address)
        store.append(city)
        store.append(state)
        store.append(zipp if zipp else "<MISSING>")   
        store.append("US")
        store.append(page_url.split("=")[-1])
        store.append(phone)
        store.append("<MISSING>")
        store.append("<MISSING>")
        store.append("<MISSING>")
        store.append("<MISSING>")
        store.append(page_url)
        # print("data==="+str(store))
        # print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~`")

        yield store

def scrape():
    data = fetch_data()
    write_output(data)


scrape()

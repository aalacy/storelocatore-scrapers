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
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    base_url = "https://www.belmond.com"
    r = session.get("https://www.belmond.com",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    for country in soup.find_all("ul",{'class':"main-menu nav-level-4 nav-group-1-1-0-2-1-1 li-vertical"}):
        if country.find("h4") == None or country.find("h4").text != "USA":
            continue
        for location in country.find_all("a"):
            location_request = session.get(location['href'],headers=headers)
            location_soup = BeautifulSoup(location_request.text,"lxml")
            location_details = list(location_soup.find("footer",{'class':"module footer product"}).find("p").stripped_strings)
            store = []
            store.append("https://www.belmond.com")
            store.append(location_soup.find("title").text)
            store.append(location_details[-1].split(",")[0].replace("· ",""))
            store.append(location_details[-1].split(",")[1])
            if len(location_details[-1].split(",")) == 3:
                store.append(" ".join(location_details[-1].split(",")[2].split(" ")[1:-1]))
                store.append(location_details[-1].split(",")[2].split(" ")[-1])
            else:
                store.append(location_details[-1].split(",")[2])
                store.append(location_details[-1].split(",")[3].split(" ")[1])
            store.append("US")
            store.append("<MISSING>")
            store.append(location_details[3].replace("· ",""))
            store.append("BELMOND")
            store.append("<MISSING>")
            store.append("<MISSING>")
            store.append("<MISSING>")
            return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()

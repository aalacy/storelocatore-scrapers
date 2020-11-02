import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re


session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    base_url = "https://www.acmestores.com"
    r = session.get(base_url + "/page/129")
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    for tr in soup.find("table",{"class": "table-striped"}).find("tbody").find_all("tr"):
        store = []
        td = tr.find_all("td")
        if td[0].text == "Corporate Office":
            pass
        else:
            temp_address = td[1].text.split(",")
            if len(temp_address) == 2:
                temp_street = temp_address[0].split("(")[0]
                temp_city = temp_address[0].split(")")[1]
                temp_address[0] = temp_street
                temp_address.insert(1,temp_city) 
            store.append("https://www.acmestores.com")
            store.append(td[0].text)
            store.append(temp_address[0])
            store.append(temp_address[1])
            store.append(temp_address[2].split(" ")[1])
            store.append(temp_address[2].split(" ")[2])
            store.append("US")
            store.append(td[0].text.split("No. ")[1].split("-")[0])
            store.append(td[2].text)
            store.append("Acme")
            geo_location = tr.find("a")["href"]
            if "&ll" in geo_location:
                store.append(geo_location.split("&ll=")[1].split(",")[0])
                store.append(geo_location.split("&ll=")[1].split(",")[1].split("&")[0])
            elif "&sll" in geo_location:
                store.append(geo_location.split("&sll=")[1].split(",")[0])
                store.append(geo_location.split("&sll=")[1].split(",")[1].split("&")[0])
            elif "/@" in geo_location:
                store.append(geo_location.split("/@")[1].split(",")[0])
                store.append(geo_location.split("/@")[1].split(",")[1])
            else:
                store.append("<MISSING>")
                store.append("<MISSING>")
            store.append("<MISSING>")
            return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()

import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import ast

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
    base_url = "https://www.athletico.com"
    r = session.get(base_url + "/locations")
    print("1")
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    for states in soup.find_all("div",{"class": "four columns serviceCard"}):
        state_link = states.find("a")["href"]
        state_request = session.get(base_url + state_link)
        state_soup = BeautifulSoup(state_request.text,"lxml")
        for table in state_soup.find_all("tbody"):
            for link in table.find_all("a"):
                if link["href"][0] == "/":
                    print(base_url + link["href"])
                    location_request = session.get(base_url + link["href"])
                    location_soup = BeautifulSoup(location_request.text,"lxml")
                else:
                    print(link["href"])
                    location_request = session.get(link["href"])
                    location_soup = BeautifulSoup(location_request.text,"lxml")
                contact_information = list(location_soup.find("div",{"id": "contactInfo"}).stripped_strings)
                location_address = list(location_soup.find("div",{"id": "geographicInfo"}).stripped_strings)
                if len(location_address) == 5:
                    location_address[1:3] = [' '.join(location_address[1:3])]
                store=[]
                store.append("https://www.athletico.com")
                store.append(location_soup.find("h1",{"class": "innerPage"}).text)
                store.append(location_address[1])
                store.append(location_address[2].split(",")[0])
                if store[-1] == "":
                    store[-1] = store[1]
                store.append(location_address[2].split(",")[1].split(" ")[1])
                store.append(location_address[2].split(",")[1].split(" ")[-1])
                store.append("US")
                store.append("<MISSING>")
                store.append(contact_information[1])
                store.append("ATHLETICO PHYSICAL THERAPY")
                store.append("<INACCESSIBLE>")
                store.append("<INACCESSIBLE>")
                store.append(' '.join(list(location_soup.find("table").stripped_strings)))
                return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()

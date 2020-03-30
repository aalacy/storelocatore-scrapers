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
    base_url = "https://www.academybank.com"
    r = session.get(base_url + "/locations")
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    for states in soup.find_all("div",{"class": "views-summary views-summary-unformatted"}):
        link = states.find("a")['href']
        state_request = session.get(base_url + link)
        state_soup = BeautifulSoup(state_request.text,"lxml")
        for locations in state_soup.find_all("div",{"class": "views-summary views-summary-unformatted"}):
            location_link = locations.find("a")['href']
            location_request = session.get(base_url + location_link)
            location_soup = BeautifulSoup(location_request.text,"lxml")
            for li in location_soup.find("ol").find_all("li",recusive=False):
                store = []
                location_name = li.find("div",{"class": "title"}).text
                location_address = list(li.find("div",{"class": "address"}).stripped_strings)
                if li.find("div",{"class":"phone"}) != None:
                    location_phone =  li.find("div",{"class": "phone"}).text
                else:
                    location_phone =  "<MISSING>"
                location_hours =  li.find("div",{"class": "hours"}).text
                location_type = "Academy bank " + list(li.find("div",{"class": "type"}).stripped_strings)[0]
                location_geo = li.find("div",{"class": "directions"}).find("a")["href"]
                location_latitude = location_geo.split("&saddr=")[1].split(",")[0]
                location_longitude = location_geo.split("&saddr=")[1].split(",")[1]
                store.append("https://www.academybank.com")
                store.append(location_name)
                store.append(location_address[0])
                store.append(location_address[1])
                store.append(location_address[3])
                store.append(location_address[4])
                store.append("US")
                store.append("<MISSING>")
                store.append(location_phone)
                store.append(location_type)
                store.append(location_latitude)
                store.append(location_longitude)
                store.append(location_hours.replace("\n"," "))
                return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()

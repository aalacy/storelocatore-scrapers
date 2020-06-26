import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
session = SgRequests()
import requests
def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        for row in data:
            writer.writerow(row)
def fetch_data():
    base_url = "https://www.cslplasma.com"
    r = requests.get(base_url + "/locations/search-results-state")
    soup = BeautifulSoup(r.text, "lxml")
    address = []
    return_main_object = []
    comming_soon = []
    for option in soup.find('select',{"name": "SelectedState"}).find_all("option"):
        if option['value'] == "":
            continue
        location_request = requests.get(base_url + option['value'])
        lcoation_soup = BeautifulSoup(location_request.text, 'lxml')
        for location in lcoation_soup.find_all("div", {"class": "center-search-item"}):
            store = []
            location_address = list(location.find("div", {"class": "center-search-item-addr"}).stripped_strings)
            if location_address[1] != "Coming Soon" and location_address[1] != "Coming soon":
                name = location.find("span", {'class': "center-search-item-name"}).text
                street_address = location_address[1].strip()
                city = location_address[-1].split(',')[0].strip()
                state = location_address[-1].split(',')[-1].split()[0].strip()
                zipp = location_address[-1].split(',')[-1].split()[-1].strip()
                if "" == city:
                    city = "<MISSING>"
                location_hours = list(location.find('div', {"class": "center-search-item-contact"}).stripped_strings)
                phone = ""
                if "Ph:" in location_hours:
                    phone = location_hours[location_hours.index("Ph:") + 1]
                else:
                    phone = "<MISSING>"
                page_url1 = location.find_all("a")[1]['href']
                if "javascript:togglePreferredCenter" in page_url1:
                    page_url1 = location.find_all("a")[0]['href']
                page_url = (base_url+page_url1)
                data_8 = page_url.split("-")[0].split("/")[-1]
                if len(data_8) == 3:
                    store_number = (data_8.replace("eau",'<MISSING>'))
                else:
                    store_number = ("<MISSING>")
                latitude = "<MISSING>"
                longitude = "<MISSING>"
                if "30721" in zipp:
                    city = "Dalton"
                if "83651" in zipp:
                    city = "Nampa"
                if "62702" in zipp:
                    city = "Springfield"
                if "79924" in zipp:
                    city = "El Paso"
                if "65202" in zipp:
                    city = "columbia"
                if "23502" in zipp:
                    city = "norfolk"
                store = []
                store.append("https://www.cslplasma.com")
                store.append(name)
                store.append(street_address)
                store.append(city if city != "" else "<MISSING>")
                store.append(state)
                store.append(zipp)
                store.append("US")
                store.append(store_number)
                store.append(phone if phone != "" else "<MISSING>")
                store.append("<MISSING>")
                store.append(latitude)
                store.append(longitude)
                store.append(location_hours[-1] if location_hours[-1] != "Contact Info" and location_hours[-1] != "Coming Soon" else "<MISSING>")
                store.append(page_url)
                if store[2] in address :
                    continue
                address.append(store[2])
                yield store
def scrape():
    data = fetch_data()
    write_output(data)
scrape()

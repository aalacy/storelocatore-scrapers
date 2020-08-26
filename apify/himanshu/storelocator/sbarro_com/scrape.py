import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json


session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    addresses =[]
    addresses1 =[]
    #### US location
    base_url = "https://sbarro.com"
    
    
    r = session.get("https://sbarro.com/locations/?user_search=")
    soup = BeautifulSoup(r.text, "lxml")
    links = soup.find_all("h2",{"class":"location-name"})
    coords = soup.find_all("section",{"class":"locations-result"})
    latitude = []
    longitude = []
    for coord in coords:
        latitude.append(coord['data-latitude'])
        longitude.append(coord['data-longitude'])
    
    for index,link in enumerate(links):
        page_url = base_url+link.find("a")['href']
        r1 = session.get(page_url)
        soup1 = BeautifulSoup(r1.text, "lxml")
        location_name = soup1.find("h1",{"class":"location-name"}).text.strip()
        street_address = " ".join(soup1.find("p",{"class":"location-address"}).text.replace(",,",',').split(",")[:-2]).strip()
        city = soup1.find("p",{"class":"location-address"}).text.replace(",,",',').split(",")[-2].strip().capitalize()
        temp_state_zip = soup1.find("p",{"class":"location-address"}).text.replace(",,",',').split(",")[-1].strip().split(" ")
        if len(temp_state_zip) == 2:
            state = temp_state_zip[0]
            zipp = temp_state_zip[1]
        else:
            state = temp_state_zip[0]
            zipp = "<MISSING>"
        try:
            phone = soup1.find("div",{"class":"location-phone location-cta"}).find("span",{"class":"btn-label"}).text.strip()
        except:
            phone = "<MISSING>"
        hours_of_operation = " ".join(list(soup1.find("div",{"class":"location-hours"}).stripped_strings))
        country_code = "US"
        location_type = "Restaurant"

        store = []
        store.append(base_url)
        store.append(location_name if location_name else "<MISSING>")
        store.append(street_address if street_address else "<MISSING>")
        store.append(city if city else "<MISSING>")
        store.append(state if state else "<MISSING>")
        store.append(zipp if zipp else "<MISSING>")
        store.append(country_code if country_code else "<MISSING>")
        store.append("<MISSING>") 
        store.append(phone if phone else "<MISSING>") 
        store.append(location_type if location_type else "<MISSING>")
        store.append(latitude[index])
        store.append(longitude[index])
        store.append(hours_of_operation.replace("Hours of Operation","") if hours_of_operation.replace("Hours of Operation","") else "<MISSING>")
        store.append(page_url)

        if store[2] in addresses1:
                continue
        addresses1.append(store[2])
        # print("data===="+str(store))
        # print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~`")
        yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()

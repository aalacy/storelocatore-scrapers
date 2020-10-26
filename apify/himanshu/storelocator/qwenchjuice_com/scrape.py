
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
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)



def fetch_data():
    base_url = 'https://qwenchjuice.com/locations'
    r = session.get(base_url)
    soup = BeautifulSoup(r.text, "lxml")
    return_main_object = []
    soup.find_all("div", {"class": "address_box"})[0].find("a", {"class", "contact_call"}).text
    for location in soup.find_all("div", {"class": "address_box"}):
        name = location.find("h4").text.strip()
        store_name = '<MISSING>'
        store_id = "<MISSING>"
        current_location = location.find("div", {"class", "current_locations"}).find("address").text
        obj = current_location.split(",")
        address = obj[0].strip().replace("4114 Sepulveda Blvd","4114 Sepulveda Blvd Unit C").replace("11815 NW 169th PL","11815 NW 169th PL #6022").replace("4462 Mission Blvd","4462 Mission Blvd ste 102")
        state = ''
        zip = ''
        city = ''
        country = 'US'
        store = []
        phone = location.find("a", {"class":"contact_call"}).text.strip()
        lat = '<MISSING>'
        long = '<MISSING>'
        hours_of_operation = '<MISSING>'
        if len(obj) < 3:
            city = obj[1].strip().split(' ')
            zip = city[-1]
            # print(zip)
            state = city[-2]
            tmp = ''
            for i in range(-3, -1+len(city)*-1, -1):
                tmp = city[i] + ' ' +  tmp
            city = tmp
        else:
            state = obj[2].strip().split(' ')
            zip = state[-1].replace("0N1","L6H 0N1").replace("Beaverton","97006").replace("Deigo","90017").replace("City","90230")
            state = state[0].replace("Beaverton","OR").replace("San","CA").replace("Culver","CA")
            # print
            city = obj[1].strip().replace("#6022","Beaverton").replace("ste 102","San Diego").replace("Unit C","Culver City")
        if "L6H 0N1" in zip :
            country = "CA"
        store.append(base_url)
        store.append(name)
        store.append(address)
        store.append(city)
        store.append(state)
        store.append(zip)
        store.append(country)
        store.append(store_id)
        store.append(phone)
        store.append(store_name)
        store.append(lat)
        store.append(long)
        store.append(hours_of_operation)
        store.append("https://qwenchjuice.com/locations")
        return_main_object.append(store)
    return return_main_object
    

def scrape():
    data = fetch_data()
    write_output(data)
scrape()


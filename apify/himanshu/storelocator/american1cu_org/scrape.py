import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
session = SgRequests()
def write_output(data):
    with open('data.csv', mode='w', newline = "") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        for row in data:
            writer.writerow(row)
def fetch_data():
    coordinates = {}
    base_url= "https://www.american1cu.org"
    Union_soup = BeautifulSoup(session.get("https://www.american1cu.org/locations#locatormap").text.replace('<div class="listbox" />','<div class="listbox" >'),"lxml")
    Union_coords = Union_soup.find(lambda tag:(tag.name == "script") and "var point" in tag.text).text
    for direction in Union_coords.split("infowindow.setContent")[1:]:
        cordination = direction.split("onClick='getDir(")[1].split(");' value")[0].split(",")
        lat = cordination[0].strip()
        lng = cordination[1].strip()
        street_address = direction.split("<p>")[1].split("<br />")[0]
        coordinates[street_address] = {"lat":lat, "lng":lng}
    for info in Union_soup.find_all("div",{"class":"listbox"}):
        addr = list(info.stripped_strings)
        location_name = addr[0]
        street_address = addr[1]
        city = addr[2].split(",")[0]
        state = addr[2].split(",")[1].split()[0]
        zipp = addr[2].split(",")[1].strip().split(" ")[-1]
        if len(addr) > 4:
            if location_name =="Home Office Drive Thru":
                phone = "<MISSING>"
            else:
                phone = addr[4]
            for index in range(len(addr)):
                if "Hours:" in addr[index]:
                    hours = " ".join(addr[index:]).split("This is not")[0].split("Inside")[0].replace("Lobby Hours:","")
                    break
            location_type = "American 1 Credit Union Branches"
        else:
            phone = "<MISSING>"
            hours = "<MISSING>"
            location_type = "American 1 Credit Union ATMs"
        lat = coordinates[street_address]['lat']
        lng = coordinates[street_address]['lng']
        if location_type =="American 1 Credit Union ATMs":
            continue
        else:
            href = str(info.find("a")['href'])
            store = []
            store.append(base_url)
            store.append(location_name)
            store.append(street_address)
            store.append(city)
            store.append(state)
            store.append(zipp)
            store.append("US")
            store.append("<MISSING>")
            store.append(phone)
            store.append(location_type)
            store.append(lat)
            store.append(lng)
            store.append(hours)
            store.append("https://www.american1cu.org/locations")
            store = [str(x).strip() if x else "<MISSING>" for x in store]
            yield store
    Other_coordinates = {}
    Other_soup= BeautifulSoup(session.get("https://www.american1cu.org/locations?street=&search=&state=&radius=99&options%5B%5D=atms&options%5B%5D=shared_branches").text.replace('<div class="listbox" />','<div class="listbox" >'),"lxml")
    Other_coords = Other_soup.find(lambda tag:(tag.name == "script") and "var point" in tag.text).text
    for direction in Other_coords.split("infowindow.setContent")[1:-1]:
        cordination = direction.split("onClick='getDir(")[1].split(");' value")[0].split(",")
        lat = cordination[0].strip()
        lng = cordination[1].strip()
        street_address = direction.split("<p>")[1].split("<br />")[0].strip()
        Other_coordinates[street_address] = {"lat":lat, "lng":lng}
    for info in Other_soup.find_all("div",{"class":"listbox"}):
        addr = list(info.stripped_strings)
        location_name = addr[1]
        street_address = addr[3]
        city = addr[4].split(",")[0]
        href = str(info.find("a")['href'])
        try:
            if location_name == "MSU Pavillion":
                zipp = "<MISSING>"
            else:
                zipp = addr[4].split(",")[1].strip().split(" ")[-1]
            state = addr[4].split(",")[1].strip().split(" ")[0]
        except:
            zipp = "<MISSING>"
            state = "<MISSING>"
        if len(addr) > 4:
            for index in range(len(addr)):
                if "Hours:" in addr[index]:
                    hours = " ".join(addr[index:]).split("This is not")[0].split("Inside")[0].replace("Lobby Hours: ","")
                    break
            location_type = "Other ATMs"
        else:
            hours = "<MISSING>"
            location_type = "Other Shared Branches"
        href = str(info.find("a")['href'])
        location_name = addr[1]
        store = []
        store.append(base_url)
        store.append(location_name)
        store.append(street_address)
        store.append(city)
        store.append(state)
        store.append(zipp)
        store.append("US")
        store.append("<MISSING>")
        store.append("<MISSING>")
        store.append(location_type)
        store.append(Other_coordinates[street_address]['lat'])
        store.append(Other_coordinates[street_address]['lng'])
        store.append(hours)
        store.append("https://www.american1cu.org/locations?search=&state=&options%5B%5D=atms&options%5B%5D=shared_branches")
        store = [str(x).strip() if x else "<MISSING>" for x in store]
        yield store
    atm_soup = BeautifulSoup(session.get("https://www.american1cu.org/locations?street=&search=&state=&radius=99&options%5B%5D=cuatms").text.replace('<div class="listbox" />','<div class="listbox" >'),"lxml")
    atm_coords = atm_soup.find(lambda tag:(tag.name == "script") and "var point" in tag.text).text
    for direction in atm_coords.split("infowindow.setContent")[1:-1]:
        cordination = direction.split("onClick='getDir(")[1].split(");' value")[0].split(",")
        lat = cordination[0].strip()
        lng = cordination[1].strip()
        street_address = direction.split("<p>")[1].split("<br />")[0]
        coordinates[street_address] = {"lat":lat, "lng":lng}
    for info in atm_soup.find_all("div",{"class":"listbox"}):
        addr = list(info.stripped_strings)
        if len(addr)==4:
            location_type = "American 1 Credit Union ATMs"
            location_name = addr[0]
            street_address = addr[2]
            city = addr[3].split(",")[0]
            state = addr[3].split(",")[1].strip().split(" ")[0]
            zipp = addr[3].split(",")[1].strip().split(" ")[1]
            phone = "<MISSING>"
            hours_of_operation = "<MISSING>"
            lat = coordinates[street_address]['lat']
            lng = coordinates[street_address]['lng']
            location_name = location_name+"(ATM)"
            store = []
            store.append(base_url)
            store.append(location_name)
            store.append(street_address)
            store.append(city)
            store.append(state)
            store.append(zipp)
            store.append("US")
            store.append("<MISSING>")
            store.append(phone)
            store.append(location_type)
            store.append(lat)
            store.append(lng)
            store.append(hours_of_operation)
            store.append("https://www.american1cu.org/locations")
            store = [str(x).strip() if x else "<MISSING>" for x in store]
            yield store
def scrape():
    data = fetch_data()
    write_output(data)
scrape()



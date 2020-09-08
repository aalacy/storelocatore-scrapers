import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
session = SgRequests()
def write_output(data):
    with open('data.csv', mode='w', newline = "") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)
def fetch_data():
    coordinates = {}
    addressess = []
    base_url= "https://www.american1cu.org"
    # American  Credit Union Location
    Union_soup = BeautifulSoup(session.get("https://www.american1cu.org/locations").text.replace('<div class="listbox" />','<div class="listbox" >'),"html5lib")
    Union_coords = Union_soup.find(lambda tag:(tag.name == "script") and "var point" in tag.text).text
    for direction in Union_coords.split("var point = new google.maps.LatLng")[1:]:
        lat = re.findall(r'[-+]?\d*\.\d+',direction.split(");")[0])[0]
        lng = re.findall(r'[-+]?\d*\.\d+',direction.split(");")[0])[1]
        location_name = direction.split("<span class='cuname'>")[1].split("</span><p class='locicons'>")[0]
        coordinates[location_name] = {"lat":lat, "lng":lng}
    for info in Union_soup.find_all("div",{"class":"listbox"}):
        addr = list(info.stripped_strings)
        location_name = addr[0]
        street_address = addr[1]
        city = addr[2].split(",")[0]
        state = addr[2].split(",")[1].split()[0]
        zipp = addr[2].split(",")[1].strip().split(" ")[-1]
        # print(zipp)
        
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
        store.append(coordinates[location_name]['lat'])
        store.append(coordinates[location_name]['lng'])
        store.append(hours)
        store.append("https://www.american1cu.org/locations")
        store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
        if store[2] in addressess:
            continue
        addressess.append(store[2])
        yield store
    ## Other location
    Other_coordinates = {}
    Other_soup= BeautifulSoup(session.get("https://www.american1cu.org/locations?search=&state=&options%5B%5D=atms&options%5B%5D=shared_branches").text.replace('<div class="listbox" />','<div class="listbox" >'),"html5lib")
    Other_coords = Other_soup.find(lambda tag:(tag.name == "script") and "var point" in tag.text).text
    for direction in Other_coords.split("var point = new google.maps.LatLng")[1:-1]:
        lat = re.findall(r'[-+]?\d*\.\d+',direction.split(");")[0])[0]
        lng = re.findall(r'[-+]?\d*\.\d+',direction.split(");")[0])[1]
        
        location_name = direction.split("<span class='cuname'>")[1].split("</span> <span class='listdist'>")[0].strip()
        Other_coordinates[location_name] = {"lat":lat, "lng":lng}
    for info in Other_soup.find_all("div",{"class":"listbox"}):
        addr = list(info.stripped_strings)
        # print(addr)
        location_name = addr[1]
        street_address = addr[3]
        city = addr[4].split(",")[0]
        # print(city)
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
        store.append(Other_coordinates[location_name]['lat'])
        store.append(Other_coordinates[location_name]['lng'])
        store.append(hours)
        store.append("https://www.american1cu.org/locations?search=&state=&options%5B%5D=atms&options%5B%5D=shared_branches")
        store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
        if store[2] in addressess:
            continue
        addressess.append(store[2])
        yield store
def scrape():
    data = fetch_data()
    write_output(data)
scrape()



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

    Union_soup = BeautifulSoup(session.get("https://www.american1cu.org/locations").text.replace('<div class="listbox" />','<div class="listbox" >'),"lxml")
    Union_coords = Union_soup.find(lambda tag:(tag.name == "script") and "var point" in tag.text).text

    for direction in Union_coords.split("var point = new google.maps.LatLng")[1:]:
        lat = re.findall(r'[-+]?\d*\.\d+',direction.split(");")[0])[0]
        lng = re.findall(r'[-+]?\d*\.\d+',direction.split(");")[0])[1]
        href = direction.split('href=')[1].split('target=')[0].replace('"',"").replace("\\","").strip()
        coordinates[href] = {"lat":lat, "lng":lng}
    
    for info in Union_soup.find_all("div",{"class":"listbox"}):

        addr = list(info.stripped_strings)

        location_name = addr[0]
        street_address = addr[2]
        city = addr[3].split(",")[0]
        state = addr[3].split(",")[1].split()[0]
        zipp = addr[3].split(",")[1].split()[1]
        
        if len(addr) > 4:
            phone = addr[5]

            for index in range(len(addr)):
                if "Hours:" in addr[index]:
                    hours = " ".join(addr[index:]).split("This is not")[0].split("Inside")[0]
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
        store.append(coordinates[href]['lat'])
        store.append(coordinates[href]['lng'])
        store.append(hours)
        store.append("https://www.american1cu.org/locations")
        store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
        if store[2] in addressess:
            continue
        addressess.append(store[2])
        yield store
    

    ## Other location
    Other_coordinates = {}
    
    Other_soup= BeautifulSoup(session.get("https://www.american1cu.org/locations?search=&state=&options%5B%5D=atms&options%5B%5D=shared_branches").text.replace('<div class="listbox" />','<div class="listbox" >'),"lxml")
    Other_coords = Other_soup.find(lambda tag:(tag.name == "script") and "var point" in tag.text).text

    for direction in Other_coords.split("var point = new google.maps.LatLng")[1:]:
        lat = re.findall(r'[-+]?\d*\.\d+',direction.split(");")[0])[0]
        lng = re.findall(r'[-+]?\d*\.\d+',direction.split(");")[0])[1]
        href = direction.split('href=')[1].split('target=')[0].replace('"',"").replace("\\","").strip()
        Other_coordinates[href] = {"lat":lat, "lng":lng}
    
    for info in Other_soup.find_all("div",{"class":"listbox"}):

        addr = list(info.stripped_strings)
        location_name = addr[0]
        street_address = addr[2]
        city = addr[3].split(",")[0]
        state = addr[3].split(",")[1].split()[0]
        href = str(info.find("a")['href'])
        try:
            zipp = addr[3].split(",")[1].split()[1]
        except:
            zipp = "<MISSING>"
        
        if len(addr) > 4:
            for index in range(len(addr)):
                if "Hours:" in addr[index]:
                    hours = " ".join(addr[index:]).split("This is not")[0].split("Inside")[0]
                    break

            location_type = "Other ATMs"
        else:
            hours = "<MISSING>"
            location_type = "Other Shared Branches"

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
        store.append("<MISSING>")
        store.append(location_type)
        store.append(Other_coordinates[href]['lat'])
        store.append(Other_coordinates[href]['lng'])
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



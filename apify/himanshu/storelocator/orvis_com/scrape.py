import csv
import requests
from bs4 import BeautifulSoup
import re
import json

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
    base_url = "https://orvis.com"
    r = requests.get("https://stores.orvis.com/",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    geo_object = {}
    for script in soup.find_all("script"):
        if "regionData" in script.text:
            location_list = script.text.split("regionData:")[1].split("alias:")[1:-1]
            for i in range(len(location_list)):
                state = location_list[i].split("}")[0].replace("'","").replace(" ","")
                print("https://stores.orvis.com/" + state)
                state_request = requests.get("https://stores.orvis.com/" + state)
                state_soup = BeautifulSoup(state_request.text,"lxml")
                for script1 in state_soup.find_all("script"):
                    if "var contentString =" in script1.text:
                        for geo_location in script1.text.split("var contentString =")[1:]:
                            lat = geo_location.split("google.maps.LatLng(")[1].split(",")[0]
                            lng = geo_location.split("google.maps.LatLng(")[1].split(",")[1].split(")")[0]
                            store_name = (geo_location.split("new google.maps.Marker(")[1].split("});")[0] + "}").split("title:")[1].split("icon")[0].strip().replace('"',"")[:-1]
                            geo_object[store_name] = [lat,lng]
                for location in state_soup.find_all("div",{"class":"OSL-results-column-wrapper"})[1:]:
                    name = location.find("h4",{"class":"margin-bottom-5"}).text
                    address = list(location.find("p",{"class":"margin-bottom-10"}).stripped_strings)
                    phone = location.find_all("a")[-1].text
                    if location.find("div",{"class":"weekly-hours"}) == None:
                        hours = "<MISSING>"
                    else:
                        hours = " ".join(list(location.find("div",{"class":"weekly-hours"}).stripped_strings))
                    store = []
                    store.append("https://orvis.com")
                    store.append(name)
                    store.append(address[0])
                    store.append(address[-1].split(",")[0] if address[-1].split(",")[0] != "" else "<MISSING>")
                    store.append(address[-1].split(",")[1].split(" ")[-2] if address[-1].split(",")[1].split(" ")[-2] != "" else "<MISSING>")
                    store.append(address[-1].split(",")[1].split(" ")[-1] if len(address[-1].split(",")[1].split(" ")[-1]) > 4 else "<MISSING>")
                    store.append("US")
                    store.append("<MISSING>")
                    store.append(phone.split("(")[0] if phone.strip() != "" else "<MISSING>")
                    store.append("orvis")
                    for key in geo_object:
                        if key in name:
                            store.append(geo_object[key][0])
                            store.append(geo_object[key][1])
                            break
                    if len(store) == 10:
                        store.append("<INACCESSIBLE>")
                        store.append("<INACCESSIBLE>")
                    store.append(hours)
                    print(store)
                    return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()

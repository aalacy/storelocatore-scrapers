import csv
import requests
from bs4 import BeautifulSoup
import re
import json

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        "X-Requested-With": "XMLHttpRequest",
        "content-type": "application/x-www-form-urlencoded",
    }
    base_url = "https://www.hushpuppies.com"
    data = 'format=ajax'
    r = requests.post("https://www.hushpuppies.com/US/en/stores?distanceMax=100000&zip=11756&distanceUnit=mi&country=US&formType=findbyzipandcountry&sz=25&start=0",headers=headers,data=data)
    soup = BeautifulSoup(r.text,"lxml")
    location_count = int(soup.find_all("a",{'class':"p-prev-button"})[-1]["href"].split("start=")[-1]) + 1
    return_main_object = []
    addresses = []
    for i in range(0,location_count,25):
       
        page_request = requests.post("https://www.hushpuppies.com/US/en/stores?distanceMax=100000&zip=11756&distanceUnit=mi&country=US&formType=findbyzipandcountry&sz=25&start="+ str(i),headers=headers,data=data)
        page_soup = BeautifulSoup(page_request.text,"lxml")
        for location in page_soup.find("tbody").find_all("tr",recursive=False):
            
           
            name = " ".join(list(location.find("div",{"class":"store-name"}).find("span").stripped_strings))
            address = list(location.find("td",{"class":"store-address"}).stripped_strings)
            if address[-1] == "Get Directions":
                del address[-1]
            store = []
            store.append("https://www.hushpuppies.com")
            store.append(name.split("\n")[-1][2:])
            store.append(" ".join(address[:-2]))
            if store[-1] in addresses:
                continue
            addresses.append(store[-1])
            if address[-1] == "United States":
                if len(address[-2].split(",")) == 2:
                    if len(address[-2].split(",")[1].split(" ")) != 1:
                        store.append(address[-2].split(",")[0].replace("\n",""))
                        store.append(address[-2].split(",")[1].split(" ")[-2].replace("\n",""))
                        store.append(address[-2].split(",")[1].split(" ")[-1])
                    else:
                        store.append(address[-2].split(",")[0].replace("\n",""))
                        store.append(address[-2].split(",")[1].replace("\n",""))
                        store.append("<MISSING>")
                else:
                    store.append(address[-2].split(",")[0].split("\n")[0])
                    store.append("<MISSING>")
                    store.append(address[-2].split(",")[0].split("\n")[1])
                store.append("US")
            else:
                if len(address[-2].split(",")) == 2:
                    store.append(address[-2].split(",")[0].replace("\n",""))
                    store.append(address[-2].split(",")[1].split(" ")[0].replace("\n",""))
                    store.append(" ".join(address[-2].split(",")[1].split(" ")[1:]))
                else:
                    store.append(address[-2].split(",")[0].split("\n")[0])
                    store.append("<MISSING>")
                    store.append(address[-2].split(",")[0].split("\n")[1])
                store.append("CA")
            store.append(location.find("a",{"class":"editbutton"})["id"])
            store.append(location.find("td",{'class':"store-phone"}).text)
            if store[-1] == "":
                store[-1] = "<MISSING>"
            store.append("hush puppies")
            if "data-location" in location.find("a",{"class":"editbutton"}).attrs:
                geo_location = json.loads(location.find("a",{"class":"editbutton"})["data-location"].replace("'",'"'))
                store.append(geo_location["latitude"])
                store.append(geo_location["longitude"])
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

import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
session = SgRequests()
def write_output(data):
    with open('data.csv', mode='w',encoding="utf-8", newline = "") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    addressess = []
    headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    base_url = "https://pksa.com"
    r = session.get("https://pksa.com/franchise/pksa-locations",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    # https://pksa.com/grand-blanc
    for location in soup.find_all("h4",{"class":'heading-primary'}):
        try:
            page_url = "https://pksa.com"+(location.find("a")['href'])
        except:
            continue
        # print(page_url)
        r = session.get(page_url,headers=headers)
        soup = BeautifulSoup(r.text,"lxml")
        data = (soup.find("div",{"class":"left-footer"}))
        addr = (list(data.stripped_strings)[-1]).replace("(Inside Immanuel Lutheran Church & School)",'Macomb, MI 48044')
        city = addr.split(",")[0]
        try:
            state =addr.split(",")[1].strip().split(" ")[0]
            zipp = addr.split(",")[1].strip().split(" ")[-1]
        except:
            state = "<MISSING>"
            zipp = "<MISSING>"
        location_name = (list(data.stripped_strings)[0])
        if location_name == "PKSA Karate Bloomfield":
            street_address = (list(data.stripped_strings)[2])
        else:
            street_address = (list(data.stripped_strings)[1]).replace("(Located in Highland Acres Church of God Gym)\n            ","")
        try:
            phone = soup.find("div",{"class":"right-footer"}).find("span",{"title":"Call with Google Voice"}).text
        except:
            phone = soup.find("span",{"title":"Call with Google Voice"}).text
        geo_data = str(soup).split("map = new google.maps.Map(mapnode, { zoom: 15, center: {")[1].split("} }); var marker")[0].split(",")
        latitude = geo_data[0].replace("lat: ","")
        longitude = geo_data[1].replace(" lng: ","")
        hours_of_operation = "<MISSING>"
        if "PKSA Karate Midland" in location_name:
            state = "MI"
            zipp = "48640"
            city = city.replace(zipp,"").replace(state,"")
        if "PKSA Karate Detroit" in location_name:
            street_address = "3627C Cass Ave"
        if "PKSA Karate Holland" in location_name:
            street_address = "3006 West Shore Dr, Ste 30"
        store = []
        store.append(base_url)
        store.append(location_name)
        store.append(street_address.replace("3627CCass Ave","3627C Cass Ave"))
        store.append(city)
        store.append(state)
        store.append(zipp)
        store.append("US")
        store.append("<MISSING>")
        store.append(phone)
        store.append("PKSA Karate")
        store.append(latitude)
        store.append(longitude.replace("lng:-83.335008","-83.335008"))
        store.append(hours_of_operation)
        store.append(page_url)
        store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
        if store[2] in addressess:
            continue
        addressess.append(store[2])
        yield store
def scrape():
    # fetch_data()
    data = fetch_data()
    write_output(data)
scrape()

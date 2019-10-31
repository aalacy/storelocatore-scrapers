import csv
import requests
from bs4 import BeautifulSoup
import re
import json
import time

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    headers = {
        "user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36"
    }
    base_url = "https://www.hilton.com"
    r = requests.get("https://www.hilton.com/en/locations/curio/",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    addresses = []
    for script in soup.find_all("script"):
        if "__NEXT_DATA__ = " in script.text:
            location_list = json.loads(script.text.split("__NEXT_DATA__ = ")[1].split("module={}")[0])["props"]['pageProps']["serverState"]["apollo"]["data"]
    for key in location_list:
        if "address" in location_list[key] and "id" in location_list[key]["address"]:
            address = location_list[location_list[key]["address"]["id"]]
            if address["country"] not in ("US","CA"):
                continue
            cord = location_list[location_list[key]["coordinate"]["id"]]
            store_unique_identifier =  location_list[key]["ctyhocn"]
            request_data = r'{"operationName":"GetHotelInfo","variables":{"ctyhocn":"' + store_unique_identifier + r'","language":"en"},"query":"query GetHotelInfo($ctyhocn: String!, $language: String!) {\n  hotel(ctyhocn: $ctyhocn, language: $language) {\n    address {\n      addressFmt\n    }\n    brandCode\n    galleryImages(numPerCategory: 2, first: 12) {\n      alt\n      hiResSrc(height: 430, width: 950)\n      src\n    }\n    homepageUrl\n    name\n    open\n    openDate\n    phoneNumber\n    resEnabled\n    amenities(filter: {groups_includes: [hotel]}) {\n      id\n      name\n    }\n  }\n}\n"}'
            request_header = {
                "user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36",
                "content-type": "application/json"
            }
           # print(address)
            location_json_request = requests.post("https://www.hilton.com/graphql/customer?pod=brands&type=GetHotelInfo",data=request_data,headers=request_header)
            location_url = location_json_request.json()["data"]["hotel"]["homepageUrl"]
           # print(location_url)
            location_request = requests.get(location_url,headers=headers)
            location_soup = BeautifulSoup(location_request.text,"lxml")
            if location_soup.find("h1",text=re.compile("You've stumped us")):
                continue
            name = location_soup.find("span",{'class':"property-name"}).text.strip()
            street_address = location_soup.find("span",{'class':"property-streetAddress"}).text.strip()
            if street_address in addresses:
                continue
            addresses.append(street_address)
            city = location_soup.find("span",{'class':"property-addressLocality"}).text.strip()
            state = location_soup.find("span",{'class':"property-addressRegion"}).text.strip()
            store_zip = location_soup.find("span",{'class':"property-postalCode"}).text.strip()
            phone = location_soup.find("span",{'class':"property-telephone"}).text.strip()
            store = []
            if(state == 'Washington'):
                state ='WA'
            store.append("https://curiocollection3.hilton.com")
            store.append(name)
            store.append(street_address)
            store.append(city)
            store.append(state)
            store.append(store_zip)
            store.append(address["country"])
            store.append("<MISSING>")
            store.append(phone if phone else "<MISSING>")
            store.append("<MISSING>")
            store.append(cord["latitude"])
            store.append(cord["longitude"])
            store.append("<MISSING>")
            store.append(location_url)
            yield store

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
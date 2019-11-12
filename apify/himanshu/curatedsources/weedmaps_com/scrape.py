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
    page = 1
    urls = []
    while True:
        r = requests.get("https://api-g.weedmaps.com/discovery/v1/deals?filter%5Bcategory%5D=all&page=" + str(page) + "&page_size=150&latlng=40.73%2C-73.5",headers=headers)
        location_list = r.json()["data"]["deals"]
        return_main_object = []
        if location_list == []:
            break
        for location in location_list:
            page_url = location["listing"]["web_url"] + "/about"
            # print(page_url)
            if page_url in urls:
                continue
            urls.append(page_url)
            location_request = requests.get(page_url,headers=headers)
            location_soup = BeautifulSoup(location_request.text,"lxml")
            if location_soup.find("script",{'type':"application/ld+json"}) == None:
                continue
            location_data = json.loads(location_soup.find("script",{'type':"application/ld+json"}).text)
            address = location_data["address"]
            hours = " ".join(list(location_soup.find("div",{"class":re.compile("components__OpenHours")}).stripped_strings))
            store = []
            store.append("https://weedmaps.com")
            store.append(location_data["name"])
            store.append(address["streetAddress"] if address["streetAddress"] else "<MISSING>")
            store.append(address["addressLocality"] if address["addressLocality"] else "<MISSING>")
            store.append(address["addressRegion"] if address["addressRegion"] else "<MISSING>")
            store.append(address["postalCode"] if address["postalCode"] else "<MISSING>")
            postalCode = store[-1]
            ca_zip_split = re.findall(r'[A-Z]{1}[0-9]{1}[A-Z]{1}\s*[0-9]{1}[A-Z]{1}[0-9]{1}',postalCode.upper())
            if ca_zip_split:
                store.append("CA")
            else:
                store.append("US")
            if str(store[-2]) == "1":
                store[-1] = "CA"
                store[-2] = "<MISSING>"
            if store[-1] == "US":
                if store[-2].replace("-","").replace(" ","").isdigit() == False:
                    continue
                if store[5] in store[2] and store[3] in store[2]:
                    store[2] = store[2].split(",")[0]
            store.append("<MISSING>")
            phone = ""
            phone_split = re.findall(re.compile(".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"),location_data["telephone"])
            if phone_split:
                phone = phone_split[0]
            store.append(phone if phone else "<MISSING>")
            store.append(location["listing"]["listing_type"])
            store.append(location_data["geo"]["latitude"])
            store.append(location_data["geo"]["longitude"])
            store.append(hours if hours else "<MISSING>")
            store.append(page_url)
            store = [x.encode('ascii', 'ignore').decode('ascii').strip() if type(x) == str else x for x in store]
            yield store
        page += 1

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
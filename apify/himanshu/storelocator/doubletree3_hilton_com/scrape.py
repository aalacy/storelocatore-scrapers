import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import time

def write_output(data):
    with open('data.csv', mode='w',newline="") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

session = SgRequests()

def fetch_data():
    headers = {
        "user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36"
    }
    base_url = "https://www.hilton.com"
    r = session.get("https://www.hilton.com/en/locations/doubletree/",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    addresses = []
    location_list = []
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
            request_data = r'{"operationName":"hotel","variables":{"ctyhocn":"' + store_unique_identifier + r'","language":"en"},"query":"query hotel($ctyhocn: String!, $language: String!) {\n  hotel(ctyhocn: $ctyhocn, language: $language) {\n    address {\n      addressFmt\n    }\n    brandCode\n    galleryImages(numPerCategory: 2, first: 12) {\n      alt\n      hiResSrc(height: 430, width: 950)\n      src\n    }\n    homepageUrl\n    name\n    open\n    openDate\n    phoneNumber\n    resEnabled\n    amenities(filter: {groups_includes: [hotel]}) {\n      id\n      name\n    }\n  }\n}\n"}'
            request_header = {
                "user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36",
                "content-type": "application/json"
            }
            location_json_request = session.post("https://www.hilton.com/graphql/customer?pod=brands&operationName=hotel", data=request_data, headers=request_header)
            if location_json_request == None:
                continue
            if  location_json_request.json()["data"] == None:
                continue
            if location_json_request.json()["data"]["hotel"] == None:
                continue
            location_url = location_json_request.json()["data"]["hotel"]["homepageUrl"]
            location_request = session.get(location_url, headers=headers)
            if location_request == None:
                continue
            location_soup = BeautifulSoup(location_request.text,"lxml")
            if location_soup.find("h1",text=re.compile("You've stumped us")):
                continue
            if location_soup.find("span",{'class':"property-name"}):
                name = location_soup.find("span",{'class':"property-name"}).text.strip()
                street_address = location_soup.find("span",{'class':"property-streetAddress"}).text.strip()
                if street_address in addresses:
                    continue
                addresses.append(street_address)
                city = location_soup.find("span",{'class':"property-addressLocality"}).text.strip()
                state = location_soup.find("span",{'class':"property-addressRegion"}).text.strip()
                store_zip_tag = location_soup.find("span",{'class':"property-postalCode"}).text.strip()
                phone_tag = location_soup.find("span",{'class':"property-telephone"}).text.strip()
            else:
                location_details = {}
                for script in location_soup.find_all("script",{'type':"application/ld+json"}):
                    try:
                        location_details = json.loads(script.text)
                        if "address" in location_details:
                            break
                    except:
                        continue
                if location_details == {}:
                    continue
                try:
                    name = location_details["name"]
                    street_address = location_details["address"]["streetAddress"]
                    if street_address in addresses:
                        continue
                    addresses.append(street_address)
                    city = location_details["address"]["addressLocality"]
                    state = location_details["address"]["addressRegion"]
                    store_zip_tag = location_details["address"]["postalCode"]
                    phone_tag = location_details["telephone"]
                except:
                    continue
            phone_list = re.findall(re.compile(".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"), str(phone_tag))
            if phone_list:
                phone = phone_list[-1]
            else:
                phone = "<MISSING>"
            ca_zip_list = re.findall(r'[A-Z]{1}[0-9]{1}[A-Z]{1}\s*[0-9]{1}[A-Z]{1}[0-9]{1}', str(store_zip_tag))
            us_zip_list = re.findall(re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str(store_zip_tag))
            if ca_zip_list:
                store_zip = ca_zip_list[-1]
            elif us_zip_list:
                store_zip = us_zip_list[-1]
            else:
                store_zip= "<MISSING>"
            if "Newfoundland/Labr." in state:
                state = "Newfoundland and Labrador"

            store = []
            if(state == 'Washington'):
                state ='WA'
            store.append("https://doubletree3.hilton.com")
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
            # print("data === ",str(store))
            # print("-------------------------------------------------------------------------------")
            yield store

def scrape():
    data = fetch_data()
    write_output(data)

scrape()

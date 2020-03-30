import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import time


session = SgRequests()

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
    base_url = "https://sixflags.com"
    r = session.get("https://sixflags.com",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    addresses = []
    for state in soup.find_all("div",{"class":'pin'}):
        for location in state.find_all("a"):
            if location["href"][0] != "/":
                continue
            location_request = session.get(base_url + location["href"],headers=headers)
            location_soup = BeautifulSoup(location_request.text,"lxml")
            if location_soup.find("a",text="Directions") == None:
                continue
            address_request = session.get(base_url + location_soup.find("a",text="Directions")["href"],headers=headers)
            address_soup = BeautifulSoup(address_request.text,"lxml")
            phone_request = session.get(base_url + location_soup.find("a",text="Contact Us")["href"],headers=headers)
            phone_soup = BeautifulSoup(phone_request.text,"lxml")
            phone_split = phone_soup.find(text=re.compile(".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"))
            if phone_split:
                phone = re.findall(re.compile(".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"),str(phone_split))[-1].replace(")","")
            if address_soup.find("p",text=re.compile("Our physical location is")):
                address = address_soup.find("p",text=re.compile("Our physical location is")).text.split("ur physical location is ")[-1].replace(",,",",")
                street_address = " ".join(address.split(",")[0:-2])
                city = address.split(",")[-2]
                store_zip_split = re.findall(re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"),address)
                if store_zip_split:
                    store_zip = store_zip_split[-1]
                else:
                    store_zip = "<MISSING>"
                state = address.split(",")[-1].replace(store_zip,"")
            elif address_soup.find("strong",text=re.compile("ADDRESS",re.I)):
                address = address_soup.find("strong",text=re.compile("ADDRESS",re.I)).parent
                address = list(address.stripped_strings)
                if re.findall(re.compile(".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"),address[-1]):
                    address = address[:-1]
                street_address = address[-2]
                city = address[-1].split(",")[0]
                store_zip_split = re.findall(re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"),address[-1])
                if store_zip_split:
                    store_zip = store_zip_split[-1]
                else:
                    store_zip = "<MISSING>"
                state_split = re.findall("([A-Z]{2})",address[-1])
                if state_split:
                    state = state_split[-1]
                else:
                    state = "<MISSING>"
            elif address_soup.find("h4",text="ADDRESS"):
                if address_soup.find("h4",text="ADDRESS").parent.find_all("p")[-1].find("iframe"):
                    address = address_soup.find("h4",text="ADDRESS").parent.find_all("p")[-2]
                else:
                    address = address_soup.find("h4",text="ADDRESS").parent.find_all("p")[-1]
                address = list(address.stripped_strings)
                street_address = " ".join(address[1:-1])
                city = address[-1].split(",")[0]
                store_zip_split = re.findall(re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"),address[-1])
                if store_zip_split:
                    store_zip = store_zip_split[-1]
                else:
                    store_zip = "<MISSING>"
                state_split = re.findall("([A-Z]{2})",address[-1])
                if state_split:
                    state = state_split[-1]
                else:
                    state = "<MISSING>"
            elif address_soup.find("p",text=re.compile("The Park’s address is: ")):
                address = address_soup.find("p",text=re.compile("The Park’s address is: ")).text.split("The Park’s address is: ")[-1]
                street_address = address.split(",")[0]
                city = address.split(",")[1]
                store_zip_split = re.findall(re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"),address)
                if store_zip_split:
                    store_zip = store_zip_split[-1]
                else:
                    store_zip = "<MISSING>"
                state = address.split(",")[-1].replace(store_zip,"")
            elif address_soup.find("em",text=re.compile("Please use: ")):
                address = address_soup.find("em",text=re.compile("Please use: ")).text.split("Please use: ")[-1]
                street_address = " ".join(address.split(",")[0:-2])
                city = address.split(",")[-2]
                store_zip_split = re.findall(re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"),address)
                if store_zip_split:
                    store_zip = store_zip_split[-1]
                else:
                    store_zip = "<MISSING>"
                state_split = re.findall("([A-Z]{2})",address)
                if state_split:
                    state = state_split[-1]
                else:
                    state = "<MISSING>"
            else:
                street_address = "<INACCESSIBLE>"
                city = "<INACCESSIBLE>"
                state = "<INACCESSIBLE>"
                zip = "<INACCESSIBLE>"
            store = []
            store.append("https://sixflags.com")
            store.append(location.text)
            store.append(street_address)
            if store[-1] in addresses:
                continue
            addresses.append(store[-1])
            store.append(city)
            store.append(state.replace(".",""))
            store.append(store_zip)
            store.append("US")
            store.append("<MISSING>")
            store.append(phone if phone else "<MISSING>")
            store.append("<MISSING>")
            lat = ""
            lng = ""
            for iframe in address_soup.find_all("iframe"):
                if "!3d" in iframe["src"] and "!2d" in iframe["src"]:
                    lat = iframe["src"].split("!3d")[1].split("!")[0]
                    lng = iframe["src"].split("!2d")[1].split("!")[0]
            store.append(lat if lat else "<MISSING>")
            store.append(lng if lng else "<MISSING>")
            store.append("<MISSING>")
            store.append("<MISSING>")
            store = [x.encode('ascii', 'ignore').decode('ascii').strip() if type(x) == str else x for x in store]
            yield store


def scrape():
    data = fetch_data()
    write_output(data)

scrape()
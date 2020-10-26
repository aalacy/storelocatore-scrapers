import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json


session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    return_main_object = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
    }
    r = session.get("http://cubbys.com/locations/",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    location_url = []
    for location in soup.find("div",{'class':'et_pb_portfolio_items'}).find_all("div",recursive=False):
        url = location.find("a")["href"]
        if url in location_url:
            continue
        location_url.append(url)
        print(url)
        location_request = session.get(url,headers=headers)
        location_soup = BeautifulSoup(location_request.text,"lxml")
        name = location_soup.find("div",{"class":'header-content'}).find("h1").text.strip()
        location_details = list(location_soup.find("div",{"class":'header-content'}).find("div").stripped_strings)
        if len(location_details) == 1:
            location_details = location_details[0].split("\n")
        if "\n" in location_details[1]:
            location_details.extend(location_details[1].split("\n"))
            del location_details[1]
        if len(location_details) > 2:
            if location_details[2].isdigit():
                location_details[1] = location_details[1] + " " +  location_details[2]
                del location_details[2]
            if len(location_details[1].split(",")) == 1:
                location_details[1] = location_details[1] + "," +  location_details[2]
                del location_details[2]
        location_details[1] = location_details[1].replace("\xa0"," ")
        store = []
        store.append("http://cubbys.com")
        store.append(name)
        store.append(location_details[0])
        store.append(location_details[1].split(",")[0])
        store_zip_split = re.findall("([0-9]{5})",location_details[1])
        if store_zip_split:
            store_zip = store_zip_split[0]
        else:
            store_zip = "<MISSING>"
        state_split = re.findall("([A-Z]{2})",location_details[1])
        if state_split:
            state = state_split[0]
        else:
            state = "<MISSING>"
        store.append(state)
        store.append(store_zip)
        store.append("US")
        store.append(location["id"].split("-")[-1])
        store.append("(" + location_details[2].split("(")[-1] if len(location_details) > 2 else "<MISSING>")
        store.append("<MISSING>")
        geo_location = location_soup.find("div",{"class":"et_pb_map_pin"})
        store.append(geo_location["data-lat"])
        store.append(geo_location["data-lng"])
        hours = ""
        if location_soup.find("h2",text=re.compile("hours", re.IGNORECASE)):
            hours = " ".join(list(location_soup.find("h2",text=re.compile("hours", re.IGNORECASE)).parent.stripped_strings)[1:])
            if location_soup.find("h2",text=re.compile("hours", re.IGNORECASE)).parent.find("h3"):
                seperator = location_soup.find("h2",text=re.compile("hours", re.IGNORECASE)).parent.find("h3").text.strip()
                hours = hours.split(seperator)[0]
            elif len(location_soup.find("h2",text=re.compile("hours", re.IGNORECASE)).parent.find_all("h2")) != 1:
                seperator = location_soup.find("h2",text=re.compile("hours", re.IGNORECASE)).parent.find_all("h2")[1].text.strip()
                hours = hours.split(seperator)[0]
        store.append(hours.replace("\n"," ") if hours else "<MISSING>")
        yield store

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
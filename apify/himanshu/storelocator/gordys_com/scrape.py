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
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    return_main_object = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
    }
    r = session.get("https://www.shopfamilyfare.com/locations",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    count = int(soup.find("ul",{'class':"pagination"}).find_all("a")[-2].text)
    location_url = []
    for i in range(1,count+1):
        r = session.get("https://www.shopfamilyfare.com/locations?page=" + str(i),headers=headers)
        soup = BeautifulSoup(r.text,"lxml")
        for location in soup.find_all("div",{"class":"store"}):
            phone = location.find("a",{'href':re.compile("tel:")}).text.strip()
            address = list(location.find("p",{"class":"address"}).stripped_strings)
            name = location.find("a").text.strip()
            url = location.find("a")["href"]
            location_request = session.get(url,headers=headers)
            location_soup = BeautifulSoup(location_request.text,"lxml")
            street_address = address[0]
            city = address[1].split(",")[0]
            store_zip = re.findall(re.compile(r"(\b\d{5}-\d{4}\b|\b\d{5}\b\s)"),address[-1])[-1]
            state = address[-1].replace(city,"").replace(store_zip,"").replace(",","")
            hours = " ".join(list(location_soup.find("table",{'class':'hours'}).stripped_strings))
            store = []
            store.append("https://gordys.com")
            store.append(name)
            store.append(street_address)
            store.append(city)
            store.append(state)
            store.append(store_zip)
            store.append("US")
            store.append(url.split("/")[-1])
            store.append(phone)
            store.append("<MISSING>")
            store.append(location["data-latitude"])
            store.append(location["data-longitude"])
            store.append(hours if hours else "<MISSING>")
            store.append(url)
            yield store

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
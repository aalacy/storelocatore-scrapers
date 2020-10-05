import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import sgzip
session = SgRequests()
def write_output(data):
    with open('data.csv', mode='w',encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        for row in data:
            writer.writerow(row)
def fetch_data():
    MAX_RESULTS = 50
    MAX_DISTANCE = 5
    search = sgzip.ClosestNSearch()
    search.initialize(country_codes=['CA'])
    zip_code = search.next_zip()
    adressess = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        "X-Requested-With": "XMLHttpRequest",
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    }
    base_url = "https://www.landroverusa.com/"
    while zip_code:
        result_coords =[]
        r = session.get("https://www.landrover.ca/en/national-dealer-locator.html?placeName="+ str(zip_code),headers=headers)
        soup = BeautifulSoup(r.text,"lxml")
        for i in soup.find_all("div",{"class":"infoCardDealer infoCard"}):
            location_name = i.find("span",{"class":"dealerNameText fontBodyCopyLarge"}).text
            addr = i.find("span",{"class":"addressText"}).text.split(",")
            street_address = addr[0]
            city = addr[1]
            state = addr[2]
            zipp = addr[3]
            phone = i.find("span",{"class":"phoneNumber"}).find("a").text
            try:
                page_url = i.find("div",{"class":"dealerWebsiteDiv"}).find("a")['href']
            except:
                page_url = "<MISSING>"
            lat = i['data-lat']
            lng = i['data-lng']
            store = []
            store.append(base_url)
            store.append(location_name)
            store.append(street_address)
            store.append(city)
            store.append(state)
            store.append(zipp)
            store.append("CA")
            store.append("<MISSING>")
            store.append(phone if phone != "" else "<MISSING>")
            store.append("Land Rover CA")
            store.append(lat)
            store.append(lng)
            store.append("<MISSING>")
            store.append(page_url)
            if store[2] in adressess:
                continue
            adressess.append(store[2])
            store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
            yield store
        if len(soup.find_all("div",{"class":"infoCardDealer infoCard"})) < MAX_RESULTS:
            search.max_distance_update(MAX_DISTANCE)
        elif len(soup.find_all("div",{"class":"infoCardDealer infoCard"})) == MAX_RESULTS:
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " + str(MAX_RESULTS) + " results")
        zip_code = search.next_zip()
def scrape():
    data = fetch_data()
    write_output(data)
scrape()
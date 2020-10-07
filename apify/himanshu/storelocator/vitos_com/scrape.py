import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
session = SgRequests()
def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        for row in data:
            writer.writerow(row)
def fetch_data():
    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36'
    }
    base_url= "https://vitos.com/"
    r = session.get(base_url,headers=headers)
    soup= BeautifulSoup(r.text,"lxml")
    box = soup.find_all("div",{"role":"gridcell"})
    for cell in box:
        loc = list(cell.stripped_strings)
        location_name = loc[0]
        street_address = loc[1]
        city = loc[2].split(",")[0].strip()
        state = loc[2].split(",")[1].strip()
        zipp = "<MISSING>"
        if len(loc)== 6:
            phone = loc[4]
            hours_of_operation = loc[3].replace("1030","10:30").replace("230","2:30").replace("830","8:30")
        else:
            phone =  loc[5]
            hours_of_operation = ", ".join(loc[3:5]).replace("1030","10:30").replace("230","2:30").replace("830","8:30")
        page_url = session.get(cell.find("a")['href'],headers=headers).url
        store_number = page_url.split("vitos")[1]
        lat = "<MISSING>"
        lng = "<MISSING>"
        store = []
        store.append(base_url)
        store.append(location_name)
        store.append(street_address)
        store.append(city)
        store.append(state)
        store.append(zipp)
        store.append("US")
        store.append(store_number)
        store.append(phone)
        store.append("Vito's Pizza & Subs")
        store.append(lat)
        store.append(lng)
        store.append(hours_of_operation)
        store.append(page_url)
        store = [x.encode('ascii', 'ignore').decode('ascii').strip() if type(x) == str else x for x in store]
        yield store
        
def scrape():
    data = fetch_data()
    write_output(data)
scrape()
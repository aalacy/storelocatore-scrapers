import csv
import requests
from bs4 import BeautifulSoup
import re
import json
import sgzip

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
    addresses = []
    zips = sgzip.for_radius(100)
    for store_zip in zips:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
            "X-Requested-With": "XMLHttpRequest",
            "content-type": "application/x-www-form-urlencoded",
        }
        data = '_SERVICENAME=MYLEPOST_wr_dsplcr&_WEBAPP=MYLEPOST&_WEBROUTINE=wr_dsplcr&_PARTITION=TAL&_LANGUAGE=ENG&_SESSIONKEY=&_LW3TRCID=false&COUNTRY=&CITY=&STATE=&ZIP=' + str(store_zip) + '&ENTMILES=100&PST_LIST..=0'
        try:
            r = requests.post("http://www.members.legion.org/CGI-BIN/lansaweb?webapp=MYLEPOST+webrtn=wr_editlcr+ml=LANSA:XHTML+partition=TAL+language=ENG",headers=headers,data=data)
        except:
            pass
        soup = BeautifulSoup(r.text,"lxml")
        for location in soup.find("table").find_all("tr")[1:]:
            name = location.find_all("h3")[1].text
            address = list(location.find("address").stripped_strings)
            phone = location.find("a",{"href":re.compile("tel:")}).text
            store = []
            store.append("https://www.legion.org")
            store.append(name)
            store.append(" ".join(address[:-1]))
            if store[-1] in addresses:
                continue
            addresses.append(store[-1])
            store.append(address[-1].split(",")[0])
            store.append(address[-1].split(",")[1].split(" ")[-2])
            store.append(address[-1].split(",")[1].split(" ")[-1])
            store.append("US")
            store.append("<MISSING>")
            store.append(phone if phone.lower() != "unavailable" else "<MISSING>")
            store.append("the american legion")
            store.append("<MISSING>")
            store.append("<MISSING>")
            store.append("<MISSING>")
            return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()

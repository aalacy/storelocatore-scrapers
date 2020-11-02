import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import io
import json
session = SgRequests()
def write_output(data):
    with open('data.csv', mode='w', newline='') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    address = []
    datas=[]
    address_main = []
    headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    base_url = "https://www.gogamexchange.com/"
    base_url = "https://www.gogamexchange.com/"
    db_1 =  'https://www.gogamexchange.com/stores/louisiana/alexandria/'
    r1 = session.get(db_1, headers=headers)
    soup_1 = BeautifulSoup(r1.text, "lxml")
    data_9 = (soup_1.find("select",{"name":"store"}).find_all("option"))
    for k in data_9:
        if len(k['value']) == 1:
            continue
        else:
            url = (k['value'].split("::")[1])
            r2 = session.get(url, headers=headers)
            soup_2 = BeautifulSoup(r2.text, "lxml")
            data_7 = (soup_2.find("p",{"class":"address-target"}))
            hours = " ".join(list(soup_2.find("span",{"class":"hours-target"}).stripped_strings)[0:])
            zipp = data_7.text.split("\r")[-1].split(" ")[-1].strip().replace("J","37040")
            st = (" ".join(data_7.text.split("\r")[:1]).replace(",",""))
            if "615 N. Commerce St Suite A" in st:
                zipp = "73401"
            city = k.text.split(",")[0]
            state = k.text.split(",")[1].strip()
            store1 = []
            store1.append(base_url)
            store1.append(k.text)
            store1.append(" ".join(data_7.text.split("\r")[:1]).replace(",",""))
            store1.append(city)
            store1.append(state)
            store1.append(zipp)
            store1.append("US")
            store1.append("<MISSING>")
            store1.append(k['value'].split("::")[0])
            store1.append("<MISSING>")
            store1.append("<MISSING>")
            store1.append("<MISSING>")
            store1.append(hours)
            store1.append(k['value'].split("::")[1])
            yield store1
def scrape():
    data = fetch_data()
    write_output(data)
scrape()

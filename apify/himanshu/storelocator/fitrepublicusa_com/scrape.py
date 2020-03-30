import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import unicodedata


session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    base_url= "https://www.fitrepublicusa.com/locations"
    r = session.get(base_url)
    soup= BeautifulSoup(r.text,"lxml")
    store_name=[]
    store_detail=[]
    return_main_object=[]
    # print(soup)

    k= soup.find("div",{"class":"sqs-block html-block sqs-block-html","id":"block-17db0418b04d7073c0cc"}).find_all("p")
    

    for i in k:
        store=[]
        link =  i.find("a")['href']
        if "map=" in link:
            lat = i.find("a")['href'].split("map=")[-1].split(',')[0]
            lng = i.find("a")['href'].split("map=")[-1].split(',')[1]
        elif len(i.find_all("a")) > 1 and "map=" in i.find_all("a")[1]["href"]:
            lat = i.find_all("a")[1]['href'].split("map=")[-1].split(',')[0]
            lng = i.find_all("a")[1]['href'].split("map=")[-1].split(',')[1]
        else:
            lat = "<MISSING>"
            lng = '<MISSING>'
        name = list(i.stripped_strings)[0]
        st = list(i.stripped_strings)[1].split("-")[0]
        phone = "-".join(list(i.stripped_strings)[1].split("-")[1:]).strip()
        city = list(i.stripped_strings)[2].split(",")[0]
        state = list(i.stripped_strings)[2].split(",")[1].split( )[0]
        zip1 = list(i.stripped_strings)[2].split(",")[1].split( )[-1].replace("MO","64468")
        # print("================")

        store.append("https://www.fitrepublicusa.com")
        store.append(name)
        store.append(st)
        store.append(city)
        store.append(state)
        store.append(zip1)
        store.append("US")
        store.append("<MISSING>")
        store.append(phone)
        store.append("<MISSING>")
        store.append(lat)
        store.append(lng)
        store.append("<MISSING>")
        store.append("https://www.fitrepublicusa.com/locations")
        for i in range(len(store)):
            if type(store[i]) == str:
                store[i] = ''.join((c for c in unicodedata.normalize('NFD', store[i]) if unicodedata.category(c) != 'Mn'))
        store = [x.replace("–","-") if type(x) == str else x for x in store]
        store = [x.encode('ascii', 'ignore').decode('ascii').strip() if type(x) == str else x for x in store]
        yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()



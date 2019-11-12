import csv
import requests
from bs4 import BeautifulSoup
import re
import json
import unicodedata
import sgzip
import time

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def request_wrapper(url,method,headers,data=None):
    request_counter = 0
    if method == "get":
        while True:
            try:
                r = requests.get(url,headers=headers)
                return r
                break
            except:
                time.sleep(2)
                request_counter = request_counter + 1
                if request_counter > 10:
                    return None
                    break
    elif method == "post":
        while True:
            try:
                if data:
                    r = requests.post(url,headers=headers,data=data)
                else:
                    r = requests.post(url,headers=headers)
                return r
                break
            except:
                time.sleep(2)
                request_counter = request_counter + 1
                if request_counter > 10:
                    return None
                    break
    else:
        return None

def fetch_data():
    cords = sgzip.coords_for_radius(100)
    return_main_object = []
    addresses = []
    r_headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36',
        "content-type": "application/json;charset=UTF-8"
    }
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    for cord in cords:
        base_url = "https://sportclips.com"
        r_data = '{"strLocation":"1","strLat":' + str(cord[0]) + ',"strLng":' + str(cord[1]) + ',"strRadius":"100","country":"US"}'
        r = request_wrapper("https://sportclips.com/CustomWeb/StoreLocator.asmx/SearchByLocation","post",headers=r_headers,data=r_data)
        if r == None:
            continue
        data = json.loads(r.json()["d"])["Results"]
        for store_data in data:
            # print(store_data["Url"])
            location_request = request_wrapper(store_data["Url"],"get",headers=headers)
            if location_request == None:
                continue
            location_soup = BeautifulSoup(location_request.text,"lxml")
            if ".ca/" in store_data["Url"]:
                hours = " ".join(list(location_soup.find("div",{"class":"container second"}).find("div",{"class":"wtp-article"}).stripped_strings))
                if "COMING SOON!".lower() in hours.lower():
                    continue
                name = location_soup.find("div",{'class':"wtp-responsive-col col-md-6"}).find_all("h2")[-1].text.strip()
                address = location_soup.find("div",{'class':"wtp-responsive-col col-md-6"}).find("p").text.strip()
                store = []
                store.append("https://sportclips.com")
                store.append(name)
                store.append(" ".join(address.split(",")[:-2]))
                if store[-1] in addresses:
                    continue
                addresses.append(store[-1])
                store.append(address.split(",")[-2])
                ca_zip_split = re.findall(r'[A-Z]{1}[0-9]{1}[A-Z]{1}\s*[0-9]{1}[A-Z]{1}[0-9]{1}',address.split(",")[-1])
                if ca_zip_split:
                    ca_zip = ca_zip_split[-1]
                store.append(address.split(",")[-1].replace(ca_zip,""))
                store.append(ca_zip)
                store.append("CA")
                store.append("<MISSING>")
                store.append(store_data["Address"].split("|")[-1] if store_data["Address"].split("|")[-1] else "<MISSING>")
                store.append("sport clips")
                store.append(store_data["Lat"])
                store.append(store_data["Long"])
                store.append(hours if hours else "<MISSING>")
                store.append(store_data["Url"])
                for i in range(len(store)):
                    if type(store[i]) == str:
                        store[i] = ''.join((c for c in unicodedata.normalize('NFD', store[i]) if unicodedata.category(c) != 'Mn'))
                store = [x.replace("–","-") if type(x) == str else x for x in store]
                store = [x.encode('ascii', 'ignore').decode('ascii').strip() if type(x) == str else x for x in store]
                # print(store)
                yield store
            else:
                if location_soup.find("div",{"class":"store-block"}) == None:
                    continue
                hours = " ".join(list(location_soup.find("div",{"class":"store-block"}).stripped_strings))
                if "COMING SOON!".lower() in hours.lower():
                    continue
                name = location_soup.find("h1").text.strip()
                address = list(location_soup.find("address").stripped_strings)
                if location_soup.find("a",{'href':re.compile("tel:")}):
                    phone = location_soup.find("a",{'href':re.compile("tel:")}).text.strip()
                else:
                    phone = "<MISSING>"
                store = []
                store.append("https://sportclips.com")
                store.append(name)
                store.append(address[0])
                if store[-1] in addresses:
                    continue
                addresses.append(store[-1])
                store.append(address[1])
                store.append(address[3])
                store.append(address[4])
                store.append("US")
                store.append("<MISSING>")
                store.append(phone if phone else "<MISSING>")
                store.append("sport clips")
                store.append(store_data["Lat"])
                store.append(store_data["Long"])
                store.append(hours if hours else "<MISSING>")
                store.append(store_data["Url"])
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
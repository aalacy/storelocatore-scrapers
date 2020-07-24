import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import time
session = SgRequests()


def write_output(data):
    with open('data.csv', mode='w', newline="") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def get(url, headers, attempts=1): 
    global session
    if attempts == 10: 
        print(f'could not get {url} after {attempts} tries... giving up')
        raise SystemExit
    try: 
        # print(url)
        r = session.get(url, headers=headers)
        return r
    except Exception as ex: 
        print(f'>>> exception getting {url} : {ex}')
        print(f'>>> reset session and try again')
        session = SgRequests()
        return get(url, headers, attempts+1)


def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36',
    }
    base_url= "https://www.kohls.com/stores.shtml"
    r = get(base_url,headers=headers)
    address =[]
    soup= BeautifulSoup(r.text,"lxml")
    for state_link in soup.find("div",{"class":"tlsmap_list"}).find_all("a",{"class":"regionlist"}):
        r1 = get(state_link['href'], headers=headers)
        soup1 = BeautifulSoup(r1.text,"lxml")
        for city_link in soup1.find("div",{"class":"tlsmap_list"}).find_all("a",{"class":"citylist"}):
            r2 = get(city_link['href'], headers=headers)
            soup2 = BeautifulSoup(r2.text,"lxml")
            try:
                for url in soup2.find("div",{"class":"tlsmap_list"}).find_all("span",{"class":"location-title"}):
                    page_url = url.find("a")['href']
                    store_number = page_url.split("-")[-1].split(".s")[0]
                    r3 = get(page_url, headers=headers)
                    soup3 = BeautifulSoup(r3.text,"lxml")
                    json_data = json.loads(re.sub(r"\s+", " ",soup3.find("script",{"type":"application/ld+json"}).text.strip()))
                    if type(json_data)==list: 
                        for l in json_data:
                            location_name = l['name']
                            location_type = l['@type']
                            latitude = l['geo']['latitude']
                            longitude = l['geo']['longitude']
                            phone = l['address']['telephone']
                            street_address = l['address']['streetAddress']
                            city = l['address']['addressLocality']
                            state = l['address']['addressRegion']
                            zip1 = l['address']['postalCode']       
                    else:
                        location_name = json_data['name']
                        latitude =json_data['geo']['latitude']
                        longitude = json_data['geo']['longitude']
                        location_type = json_data['@type']
                        phone = json_data['address']['telephone']
                        street_address = json_data['address']['streetAddress']
                        city = json_data['address']['addressLocality']
                        state = json_data['address']['addressRegion']
                        zip1 = json_data['address']['postalCode']
                    hours = " ".join(list(soup3.find("div",{"class":"hours"}).stripped_strings)).replace("\n","").replace("ExceptionHours","").replace("Exception Hours","").strip()
                    store = []
                    store.append("https://www.kohls.com/")
                    store.append(location_name)
                    store.append(street_address)
                    store.append(city)
                    store.append(state)
                    store.append(zip1)   
                    store.append("US")
                    store.append(store_number)
                    store.append(phone)
                    store.append(location_type)
                    store.append(latitude)
                    store.append(longitude)
                    store.append(hours)
                    store.append(page_url) 
                    if store[2] in address :
                        continue
                    address.append(store[2])
                    yield store
            except:
                continue
def scrape():
    data = fetch_data()
    write_output(data)
scrape()

import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import random


session = SgRequests()


def write_output(data):
    with open('data.csv', mode='w',newline="") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    addressess = []

    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36'
    
    }

    base_url = "https://www.crateandbarrel.ca/"
    location_url = 'https://www.crateandbarrel.ca/stores/'
    r = session.get(location_url, headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    string = str(soup)
    script = string.split('<script type="application/ld+json">')[1:14]
    for s in script:
        jd = s.split("</script>")[0].replace(',"event":[]','').strip()
        value = json.loads(jd)
        location_name = value['name']
        street_address = value['address']['streetAddress']
        city = value['address']['addressLocality']
        state = value['address']['addressRegion']
        zipp = value['address']['postalCode']
        country_code = "CA"
        phone = value['telephone']
        if value['@type'] == 'LocalBusiness':
            location_type = 'Warehouse'
        else:
            location_type = 'Store'
        
        latitude = value['geo']['latitude']
        longitude = value['geo']['longitude']
        page = soup.find_all("a",{"class":"btn-view-info button button-secondary button-md"})
        div = soup.find_all("div",{"class":"drawer-set col-xs-12"})
        for i in div:
            name = i.find("a").find("h3",{"class":"store-name"}).text
            if name == location_name:
                page_url = "https://www.crateandbarrel.ca" + i.find("a",{"class":"btn-view-info button button-secondary button-md"})['href']
                store_number = i.find("a",{"class":"btn-view-info button button-secondary button-md"})['href'].split("/")[-1].replace("str","")
                hoo = i.find("ul",{"class":"hours"}).find_all("li")
                hours = []
                for hour in hoo:
                    frame = hour.text
                    hours.append(frame)
                hours_of_operation = ", ".join(hours)
                # print(name)
                # print(hours_of_operation)
               

        store = []
        store.append(base_url)
        store.append(location_name)
        store.append(street_address)
        store.append(city)
        store.append(state)
        store.append(zipp)   
        store.append(country_code)
        store.append(store_number)
        store.append(phone)
        store.append(location_type)
        store.append(latitude)
        store.append(longitude)
        store.append(hours_of_operation)
        store.append(page_url)
        store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]

        if store[2] in addressess:
            continue
        addressess.append(store[2])
        yield store

def scrape():
    data = fetch_data()
    write_output(data)

scrape()

import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import time
import html5lib
session = SgRequests()
def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation",
                         "page_url"])
        for row in data:
            writer.writerow(row)
def fetch_data():
    addresses = []
    headers = {'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',
    }
    base_url = "https://www.publicstorage.com"
    r =  session.get("https://www.publicstorage.com/site-map-states",headers=headers)
    soup = BeautifulSoup(r.text, "lxml")    
    data = soup.find("div",{"class":"ps-sitemap-states__states"})
    for i in data.find_all("a"):
        r1 = session.get(base_url+i['href'],headers=headers)
        soup1 = BeautifulSoup(r1.text, "lxml")
        links = soup1.find_all("a", {"class":"base-link"})
        for link in links:
            if link['href'] == "":
                continue
            page_url = base_url+link['href']
            r3 = session.get(page_url,headers=headers)
            soup3 = BeautifulSoup(r3.text, "html5lib")
            json_data = json.loads(soup3.find(lambda tag: (tag.name == "script") and "addressCountry" in tag.text).text)['@graph']
            street_address = json_data[0]['address']['streetAddress']
            city = json_data[0]['address']['addressLocality']
            state = json_data[0]['address']['addressRegion']
            zipp = json_data[0]['address']['postalCode']
            location_name = json_data[0]['name']
            store_number = page_url.split("/")[-1]
            if "telephone" in json_data[0]:
                temp_phone = json_data[0]['telephone'].replace("+","")
                phone = "("+temp_phone[:3]+")"+temp_phone[3:6]+"-"+temp_phone[6:]
            else:
                phone = "<MISSING>"
            latitude = json_data[0]['geo']['latitude']
            longitude = json_data[0]['geo']['longitude']
            country_code = "US"
            if soup3.find_all("div", {"class":"ps-properties-property__info__hours__section col-md-12 col-lg-6"}):
                hours_of_operation = " ".join(list(soup3.find_all("div", {"class":"ps-properties-property__info__hours__section col-md-12 col-lg-6"})[0].stripped_strings)) +" "+ " ".join(list(soup3.find_all("div", {"class":"ps-properties-property__info__hours__section col-md-12 col-lg-6"})[1].stripped_strings))
            else:
                hours_of_operation = "<MISSING>"
            store = []
            store.append(base_url)
            store.append(location_name)
            store.append(street_address)
            store.append(city)
            store.append(state)
            store.append(zipp)
            store.append(country_code)
            store.append(store_number)
            store.append(phone )
            store.append("<MISSING>")
            store.append(latitude)
            store.append(longitude)
            store.append(hours_of_operation)
            store.append(page_url)
            if store[2] in addresses:
                continue
            addresses.append(store[2])
            store = [x.encode('ascii', 'ignore').decode('ascii').strip() if type(x) == str else x for x in store]
            yield store
def scrape():
    data = fetch_data()
    write_output(data)
scrape()
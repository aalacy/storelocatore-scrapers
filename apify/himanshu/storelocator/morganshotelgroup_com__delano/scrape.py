import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import html5lib
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
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
    }
    base_url = "https://www.morganshotelgroup.com/delano"
    r = session.get("https://www.sbe.com/hotels/delano", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    for i in soup.find_all("div",{"class":"card__text"})[1:3]:
        page_url = "https://www.sbe.com/"+i.find("a")['href']
        r1 = session.get(page_url,headers=headers)
        soup1 = BeautifulSoup(r1.text,'html5lib')
        jd = json.loads(soup1.find_all("script",{"type":"application/ld+json"})[1].text)
        location_name = jd['name']
        street_address = jd['address']['streetAddress']
        city = jd['address']['addressLocality']
        state = jd['address']['addressRegion']
        zipp = jd['address']['postalCode']
        country_code = jd['address']['addressCountry']
        phone = jd['telephone']
        location_type = jd['@type']
        page_url = jd['url']
        map_url = jd['hasMap'].split("@")[1].split(",15z")[0].split(",")
        latitude = map_url[0]
        longitude = map_url[1]

        store = []
        store.append(base_url if base_url else '<MISSING>')
        store.append(location_name if location_name else '<MISSING>')
        store.append(street_address if street_address else '<MISSING>')
        store.append(city if city else '<MISSING>')
        store.append(state if state else '<MISSING>')
        store.append(zipp if zipp else '<MISSING>')
        store.append(country_code)
        store.append('<MISSING>')
        store.append(phone if phone else '<MISSING>')
        store.append(location_type)
        store.append(latitude if latitude else '<MISSING>')
        store.append(longitude if longitude else '<MISSING>')
        store.append('<MISSING>')
        store.append(page_url)
        store = [x.encode('ascii', 'ignore').decode('ascii').strip() if type(x) == str else x for x in store]
        yield store
def scrape():
    data = fetch_data()
    write_output(data)
scrape()


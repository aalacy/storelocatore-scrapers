import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
session = SgRequests()
def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        for row in data:
            writer.writerow(row)
def fetch_data():
    addressess = []
    base_url = "https://www.avalon-hotel.com/"
    r = session.get(base_url)
    soup = BeautifulSoup(r.text,"lxml")
    store_listing = soup.find("li",{"id": "menu-item-1347"}).find('ul')
    alla = store_listing.find_all('li')
    for i in range(len(alla)):
        link=alla[i].find('a')['href']
        r1 = session.get(link)
        soup1 = BeautifulSoup(r1.text,"lxml")
        jd = json.loads(str(soup1).split('<script type="application/ld+json">[')[1].split(']</script>')[0])
        location_name = jd['name']
        street_address = jd['address']['streetAddress']
        city = jd['address']['addressLocality']
        state = jd['address']['addressRegion']
        zipp = jd['address']['postalCode']
        country_code= jd['address']['addressCountry']
        phone = jd['telephone']
        location_type = jd['@type']
        latitude = jd['geo']['latitude']
        longitude = jd['geo']['longitude']
        hours_of_operation = "Monday to Sunday - 24 hours"
        page_url = jd['url']
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
        store.append(hours_of_operation if hours_of_operation else '<MISSING>')
        store.append(page_url)
        store = [x.strip() if type(x) == str else x for x in store]
        if store[2] in addressess:
            continue
        addressess.append(store[2])
        yield store
def scrape():
    data = fetch_data()
    write_output(data)
scrape()

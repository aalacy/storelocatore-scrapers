import csv
import sys

from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
# import pprint
# pp = pprint.PrettyPrinter(indent=4)



session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url",])
        # Body
        for row in data:
            writer.writerow(row)



def fetch_data():

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }
    base_url = "https://www.towncaredental.com"
    addresses = []
    locator_domain = base_url
    location_name = ""
    street_address = ""
    city = ""
    state = ""
    zipp = ""
    country_code = "US"
    store_number = ""
    phone = ""
    location_type = ""
    latitude = ""
    longitude = ""
    hours_of_operation = ""
  
    location_url = "https://www.towncaredental.com/locations/"
    r = session.get(location_url, headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    link = soup.find_all("p",{"class":"website"})
    for i in link:
        location_url1 = i.a['href']
        r1 = session.get(location_url1, headers=headers)
        soup1 = BeautifulSoup(r1.text, "lxml")
        json1 = json.loads(soup1.find("script",{"type":"application/ld+json"}).text)
        street_address = json1['address']['streetAddress']
        city = json1['address']["addressLocality"]
        state = json1['address']['addressRegion']
        zipp = json1['address']['postalCode']
        phone = json1['telephone']
        lat = json1['geo']['latitude']
        lng = json1['geo']['longitude']
        location_name =json1['name']
        time = ''
        for j in json1['openingHoursSpecification']:
            time = time + ' ' +j['dayOfWeek'] + ' '+ j['opens']+ ' '+j['closes']
        hours_of_operation = time.replace("00:00 00:00","close")
        latitude = lat
        longitude = lng
        page_url = i.a['href']
        store = [locator_domain, location_name.strip(), street_address.strip(), city.strip(), state, zipp.strip(), country_code,
                store_number, phone.strip(), location_type, latitude, longitude, hours_of_operation.strip(),page_url]

        if str(store[2]) + str(store[-3]) not in addresses:
            addresses.append(str(store[2]) + str(store[-3]))                   
            store = [x if x else "<MISSING>" for x in store]
            print("data = " + str(store))
            print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
            yield store

        # coord = search.next_coord()   # zip_code = search.next_zip()    
        # break

def scrape():
    data = fetch_data()

    write_output(data)


scrape()

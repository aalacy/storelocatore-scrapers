import requests
from bs4 import BeautifulSoup
import csv

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():

    base_link = "https://www.honeydewdonuts.com/locations/"

    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
    headers = {'User-Agent' : user_agent}

    req = requests.get(base_link, headers=headers)

    try:
        base = BeautifulSoup(req.text,"lxml")
    except (BaseException):
        print '[!] Error Occured. '
        print '[?] Check whether system is Online.'

    items = base.findAll('dl', attrs={'class': 'store'})

    data = []
    for item in items:
        locator_domain = "honeydewdonuts.com"
        location_name = item.find('a').text.strip()
        street_address = location_name
        raw_data = item.find('div').find('dd').text
        city = raw_data[:raw_data.find(',')].strip()
        state = raw_data[raw_data.find(',')+1:raw_data.rfind(' ')].strip()
        zip_code = raw_data[raw_data.rfind(' ')+1:].strip()
        try:
            int(zip_code)
        except:
            zip_code = state[2:].strip()
            state = state[:2].strip()
        country_code = "US"
        link = "https://www.honeydewdonuts.com" + item.find('a')['href']
        store_number = link[link.rfind("/")+1:]
        phone = item.findAll('div')[1].find('dd').text
        if phone == "":
            phone = "<MISSING>"
        location_type = "<MISSING>"
        link = "https://www.honeydewdonuts.com" + item.find('a')['href']

        req = requests.get(link, headers=headers)

        try:
            base = BeautifulSoup(req.text,"lxml")
        except (BaseException):
            print '[!] Error Occured. '
            print '[?] Check whether system is Online.'

        full_page = str(base)
        maps_point = full_page.rfind("maps.LatLng")
        raw_gps = full_page[full_page.find("(",maps_point)+1:full_page.find(";",maps_point)-2]

        latitude = raw_gps[:raw_gps.find(',')]
        longitude = raw_gps[raw_gps.find(',')+1:]

        if latitude == "":
            latitude = "<MISSING>"
        if longitude == "":
            longitude = "<MISSING>"
            
        hours_of_operation = "<MISSING>"
        print "Got page details"

        data.append([locator_domain, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()

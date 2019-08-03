import csv
import re

import requests
from bs4 import BeautifulSoup
from w3lib.html import remove_tags

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    base_url = "https://www.gertrudehawkchocolates.com/find-a-store"
    cities = [x.get('value') for x in BeautifulSoup(requests.get(base_url).text, 'html.parser').find("select", {"name":"city"}).findAll('option') if x]
    data = []
    for city in cities:
        city_url = base_url+"?state=&city={}&zip=&distance=5".format(city.replace(' ', '+'))
        soup = BeautifulSoup(requests.get(city_url).text)
        for location in soup.findAll("div", {"class": "location-details"}):
            l_data = [remove_tags(s.replace('\r\n','')).rstrip().strip() for s in str(location.p).split('<br/>')]
            l_ = []
            l_.append(city_url)
            if not l_data[0][0].isdigit():
                l_.append(l_data[0])
                del l_data[0]
                l_.append(l_data[0])
                del l_data[0]
            else:
                l_.append("<MISSING>")
                l_.append(l_data[0])
                del l_data[0]
            if not l_data[0].startswith(city):
                del l_data[0]
            d = re.match(r'(?P<city>.+?)\s,(?P<state>[A-Z][A-Z])(\s(?P<zip>.+))?', l_data[0]).groupdict()
            del l_data[0]
            if d.get('city'):
                l_.append(d['city'])
            else:
                l_.append("<MISSING>")
            if d.get('state'):
                l_.append(d['state'])
            else:
                l_.append("<MISSING>")
            if d.get('zip'):
                l_.append(d['zip'])
            else:
                l_.append("<MISSING>")
            l_.append('US')
            l_.append('<MISSING>')
            if '-' in l_data[0]:
                l_.append(l_data[0])
            else:
                l_.append("<MISSING>")
            l_.append("<MISSING>")
            l_.append("<MISSING>")
            l_.append("<MISSING>")
            l_.append("<MISSING>")
            data.append(l_)
    return data




def scrape():
    data = fetch_data()
    write_output(data)

scrape()

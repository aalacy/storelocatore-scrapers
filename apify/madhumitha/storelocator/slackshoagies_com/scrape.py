import csv
import requests
from bs4 import BeautifulSoup
import re
import json
import time

headers = requests.utils.default_headers()
headers.update({
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0',
})

DOMAIN = 'http://slackshoagies.com'
MISSING = '<MISSING>'

def write_output(data):
    with open('data.csv', mode='w', encoding='utf-8', newline='') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    data = {'locator_domain':[], 'location_name':[], 'street_address':[], 'city':[], 'state':[], 'zip':[], 'country_code':[], 'store_number':[], 'phone':[], 'location_type':[], 'latitude':[], 'longitude':[], 'hours_of_operation':[]}
    url = "http://slackshoagies.com/locations.htm"
    response = requests.get(url, headers = headers)
    soup = BeautifulSoup(response.content, "html.parser")
    loc = soup.find('div', attrs = {'align':'left'})
    title = loc.findAll('strong')
    directions = loc.findAll('a', href = True)
    try:
        for latlng in directions:
            if re.findall('maps', latlng['href']) != []:
                ll = re.findall(r'[-+]?[0-9]*\.?[0-9]+', latlng['href'])
                ln = []
                for l in ll:
                    if re.findall('\.', l) != []:
                        ln.append(l)
                if ll != []:
                    data['latitude'].append(ln[0])
                    data['longitude'].append(ln[1])
                else:
                    data['latitude'].append(MISSING)
                    data['longitude'].append(MISSING)

        for t in title:
            if re.findall('\d+', t.text) != []:
                loc_data = t.text.strip()
                data['location_name'].append(re.findall('\D+', loc_data)[0].strip())
                data['phone'].append(re.findall('\d.*', loc_data)[0].strip())
        ad_strip = re.split('\n', loc.text)

        for a in ad_strip:
            if re.findall('\d', a) != []:
                if re.findall('^\d.*', a.strip()) != []:
                    ad_data = re.split(',', a.strip())
                    data['street_address'].append(ad_data[0].strip())
                    city_data = ad_data[-1]
                    if 'directions' in ad_data[-1]:
                        city_data = re.sub(' directions', '', ad_data[-1])
                    data['state'].append(city_data.rsplit(' ', 1)[-1].strip())
                    data['city'].append(city_data.rsplit(' ', 1)[0].strip())
                    DOMAIN = 'http://slackshoagies.com'
                    country = 'US'
                    store_number = location_type = zipcode = hours_of_operation = MISSING
                    data['locator_domain'].append(DOMAIN)
                    data['country_code'].append(country)
                    data['store_number'].append(store_number)
                    data['location_type'].append(location_type)
                    data['zip'].append(zipcode)
                    data['hours_of_operation'].append(hours_of_operation)
        data = list(zip(data['locator_domain'], data['location_name'], data['street_address'], data['city'], data['state'], data['zip'], data['country_code'], data['store_number'], data['phone'], data['location_type'], data['latitude'], data['longitude'], data['hours_of_operation']))
    except requests.exceptions.RequestException:
        pass
    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()

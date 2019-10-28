import csv
import requests
from bs4 import BeautifulSoup
import re

DOMAIN = 'https://www.homewatchcaregivers.com'
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
    data=[]
    url = "https://www.homewatchcaregivers.com/locations/"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    loc = soup.findAll('li', attrs = {'class':'location'})
    for l in loc:
        try:
            city = l['data-city']
            lat = l['data-latitude']
            lon = l['data-longitude']
            store_number = l['data-loc-id']
            location_name = l['data-name'].strip()
            country = l['data-country'].strip()
            if country == 'usa':
                country = 'US'
            elif country == 'can':
                country = 'CA'
            ad = l.find('address').text.strip()
            if len(re.split('\n', ad)) >= 2:
                street_address = re.split('\n', ad)[0].strip()
            else:
                link = l.find('a', attrs = {'class':'website-link btn v1'}, href = True)['href']
                website = DOMAIN + link
                res = requests.get(website)
                w_soup = BeautifulSoup(res.content, "html.parser")
                street_address = w_soup.find('span', attrs = {'itemprop':'streetAddress'}).text.strip()
            city_data = re.split(',', ad)[-1].strip()
            zipcode = re.split('\.', city_data)[-1].strip()
            state = re.split('\.', city_data)[-2].strip()
            phone = l.find('a', attrs = {'class':'phone'}).text.strip()
            location_type = hours_of_operation = MISSING
            data.append([DOMAIN, location_name, street_address, city, state, zipcode, country, store_number, phone, location_type, lat, lon, hours_of_operation])
        except requests.exceptions.RequestException:
            pass
    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()

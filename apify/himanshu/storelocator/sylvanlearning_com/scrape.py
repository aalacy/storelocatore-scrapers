import csv
import requests
from bs4 import BeautifulSoup
import re
import io
import json
import time
def remove(string):
    pattern = re.compile(r'\s+')
    return re.sub(pattern, ' ', string)

def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    base_url = "https://www.sylvanlearning.com/locations"
    r = requests.get(base_url, headers=headers)
    addresses = []


    base_url = 'https://www.sylvanlearning.com/'
    location_url = 'https://www.sylvanlearning.com/locations/'
    r = requests.get(location_url)
    soup = BeautifulSoup(r.text,"lxml")
    # us canada url fetch
    location  = []
    vb  = {}
    for x in soup.find('div',{'class':'unitedStates'}).find_all('a'):
        location.append(x)
        vb[x] = ['US']
    for x in soup.find('div',{'class':'canada'}).find_all('a'):

        location.append(x)
        vb[x] = ['CA']
    # end

    if location != ['']:
        for y in  location:
            try:

                if y in vb:
                    country_code = vb[y][0]

                r = requests.get(base_url+y['href'])
                soup = BeautifulSoup(r.text,"lxml")
                for j in soup.find_all('div',{'class':'locationResults'}):
                    locator_domain = base_url
                    location_name = j.find('h2',{'itemprop':'name'}).text

                    street_address =  j.find('span',{'itemprop':'streetAddress'}).text
                    city =  j.find('span',{'itemprop':'addressLocality'}).text
                    state =  j.find('span',{'itemprop':'addressRegion'}).text.replace('Washington','WA')

                    zip =  j.find('span',{'itemprop':'postalCode'}).text
                    phone =  j.find('span',{'itemprop':'telephone'}).text
                    gethour = j.find('h2', {'itemprop':'name'}).find('a')['href']

                    r = requests.get(gethour)
                    location_type = ''
                    store_number = ''
                    soup = BeautifulSoup(r.text,"lxml")

                    hours_of_operation = ''
                    if soup.find('div',{'class':'locationHoursContainer'}) != None:
                        hours_of_operation = remove(soup.find('div',{'class':'locationHoursContainer'}).find('ul').text)
                    latitude = ''
                    longitude = ''
                    if soup.find('script') != None:
                        lat_long = soup.find('script').text.split(',')
                        if len(lat_long) > 1:
                            latitude = lat_long[0].strip().replace('var mapLat','').replace('=','').replace('"','').strip()
                            longitude = lat_long[1].strip().replace('mapLng', '').replace('=', '').replace('"', '').strip()
                    page_url = gethour
                    if ',' in street_address:
                        street_address = street_address.split(',')[0]
                    store = []
                    store.append(locator_domain if locator_domain else '<MISSING>')
                    store.append(location_name if location_name else '<MISSING>')
                    store.append(street_address if street_address else '<MISSING>')
                    store.append(city if city else '<MISSING>')
                    store.append(state if state else '<MISSING>')
                    store.append(zip if zip else '<MISSING>')
                    store.append(country_code if country_code else '<MISSING>')
                    store.append(store_number if store_number else '<MISSING>')
                    store.append(phone if phone else '<MISSING>')
                    store.append(location_type if location_type else '<MISSING>')
                    store.append(latitude if latitude else '<MISSING>')
                    store.append(longitude if longitude else '<MISSING>')
                    store.append(hours_of_operation if hours_of_operation else '<MISSING>')
                    store.append(page_url if page_url else '<MISSING>')

                    # print("data===",str(store))
                    yield store
            except:
                continue


def scrape():
    data = fetch_data()
    write_output(data)
scrape()

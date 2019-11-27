import csv
import requests
from bs4 import BeautifulSoup
import re
import http.client
import sgzip
import json


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation",'page_url'])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    base_url = "https://shop.guess.com/en/"
    return_main_object = []
    addresses = []
    search = sgzip.ClosestNSearch()
    search.initialize()
    MAX_RESULTS = 50
    MAX_DISTANCE = 10
    current_results_len = 0  # need to update with no of count.
    zip_code = search.next_zip()

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }



    location_url = "https://stores.guess.com.prod.rioseo.com/"
    r = requests.get(location_url,headers=headers)

    soup = BeautifulSoup(r.text,"lxml")

    for x in soup.find('ul',{'class':'custom-map-list'}).find_all('a'):


        r = requests.get(x['href'], headers=headers)
        soup = BeautifulSoup(r.text, "lxml")
        for x in soup.find('ul',{'class':'custom-map-list'}).find_all('a'):
            r = requests.get(x['href'], headers=headers)
            soup = BeautifulSoup(r.text, "lxml")
            for x in soup.find('ul', {'class': 'custom-map-list'}).find_all('li'):

                r = requests.get(x.find('a')['href'], headers=headers)
                soup = BeautifulSoup(r.text, "lxml")

                locator_domain = base_url

                location_name =  soup.find('span',{'class':'location-name'}).text;
                street_address = soup.find('meta',{'name':'address'})['content'].strip().split(',')[0];

                city = soup.find('meta',{'name':'city'})['content'].strip()
                state =  soup.find('meta',{'name':'state'})['content'].strip().split(',')[0]
                zip =  soup.find('meta',{'name':'zip'})['content'].strip()

                ca_zip_list = re.findall(r'[A-Z]{1}[0-9]{1}[A-Z]{1}\s*[0-9]{1}[A-Z]{1}[0-9]{1}', str(zip))
                us_zip_list = re.findall(re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str(zip))

                if ca_zip_list:
                    zip = ca_zip_list[-1]
                    country_code = "CA"
                if us_zip_list:
                    zip = us_zip_list[-1]
                    country_code = "US"


                store_number = ''
                page_url =  x.find('a')['href']
                phone = soup.find('a',{'class':'phone'}).text.strip()

                location_type = '<MISSING>'
                latitude = soup.find('a',{'class':'directions'})['href'].split(',')[-2].split('=')[-1]


                longitude = soup.find('a',{'class':'directions'})['href'].split(',')[-1]



                hours_of_operation = re.sub(r"\s+", " ", soup.find('div',{'class':'hours'}).text)



                if street_address in addresses:
                    continue

                addresses.append(street_address)

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
                print("===", str(store))
                # return_main_object.append(store)
                yield store



def scrape():
    data = fetch_data()
    write_output(data)


scrape()

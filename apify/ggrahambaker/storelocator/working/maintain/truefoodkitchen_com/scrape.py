import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import json


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    session = SgRequests()
    HEADERS = { 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36' }

    locator_domain = 'https://www.truefoodkitchen.com/'
    ext = 'locations'
    r = session.get(locator_domain + ext, headers = HEADERS)


    soup = BeautifulSoup(r.content, 'html.parser')

    main = soup.find('section', {'class': 'accordion'})
    hrefs = main.find_all('a')

    link_list = []
    for h in hrefs:
        if '/' not in h['href']:
            href = locator_domain + h['href']
        else:
            href = locator_domain[:-1] + h['href']
        if 'goo' in href:
            continue
        if 'tel:' in href:
            continue
            

        link_list.append(href)


    hours_map = {'1': 'Monday', '2': 'Tuesday', '3': 'Wednesday', '4': 'Thursday', '5': 'Friday', '6': 'Saturday', '7': 'Sunday'}


    all_store_data = []
    for link in link_list:
        print(link)
        r = session.get(link, headers = HEADERS)
        soup = BeautifulSoup(r.content, 'html.parser')
        
        slug = soup.find('div', {'class': 'mfcard'})
        
        if slug == None:
            continue
        slug = slug['location_id']
        
        
        url = 'https://momentfeed-prod.apigee.net/lf/location/store-info/' + slug + '?auth_token=IFWKRODYUFWLASDC'

        r = session.get(url, headers = HEADERS)
        loc = json.loads(r.content)
        
        street_address = loc['address'] + ' ' + loc['addressExtended']
        phone_number = loc['phone']
        hours_unformatted = loc['hours'].split(';')
        hours = '' 
        for h in hours_unformatted:
            day_info = h.split(',')
            if len(day_info) == 1:
                continue
            day = hours_map[day_info[0]]
            hours += day + ' ' + day_info[1] + '-' + day_info[2] + ' '


        if hours == '':
            hours = '<MISSING>'
        if phone_number == '':
            phone_number = '<MISSING>'

        lat = loc['latitude']
        longit = loc['longitude']
        
        city = loc['locality']
        state = loc['region']
        zip_code = loc['postcode']
        
        
        store_number = loc['corporateId']
        
        
        
        country_code = 'US'
        location_type = '<MISSING>'
        location_name = city
        
        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code, 
                    store_number, phone_number, location_type, lat, longit, hours, link]


        
        print(store_data)
        print()
        print()
        print()
        
        all_store_data.append(store_data)
        
        





    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()

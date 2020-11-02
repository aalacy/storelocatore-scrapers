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

    locator_domain = 'https://stopandshop.com/' 
    url = 'https://stores.stopandshop.com/'
    r = session.get(url, headers = HEADERS)

    soup = BeautifulSoup(r.content, 'html.parser')
    hrefs = soup.find_all('a', {'class': 'DirectoryList-itemLink'})
    state_links = []
    for h in hrefs:
        state_links.append(url + h['href'])

    city_link = []
    link_list = []
    for state in state_links:
        r = session.get(state, headers = HEADERS)
        soup = BeautifulSoup(r.content, 'html.parser')
        hrefs = soup.find_all('a', {'class': 'DirectoryList-itemLink'})
        for h in hrefs:
            link = url + h['href']
    
            if len(link.split('/')) == 6:
                link_list.append(link)
            else:
                city_link.append(link)

    for city in city_link:
        r = session.get(city, headers = HEADERS)
        soup = BeautifulSoup(r.content, 'html.parser')
        hrefs = soup.find_all('a', {'class': 'Teaser-titleLink'})
        for h in hrefs:
            link = url + h['href'].replace('../', '')
            link_list.append(link)
            
    all_store_data = []
    for link in link_list:
        
        r = session.get(link, headers = HEADERS)
        soup = BeautifulSoup(r.content, 'html.parser')

        is_closed = soup.find_all('div', {'class': 'NAP-closedMessage'})
        if len(is_closed) > 0:
            continue

        location_name = soup.find('meta', {'itemprop': 'name'})['content']
        
        lat = soup.find('meta', {'itemprop': 'latitude'})['content']
        longit = soup.find('meta', {'itemprop': 'longitude'})['content']
        street_address = soup.find('meta', {'itemprop': 'streetAddress'})['content']
        city = soup.find('meta', {'itemprop': 'addressLocality'})['content']
        state = soup.find('abbr', {'itemprop': 'addressRegion'})['title']
        zip_code = soup.find('span', {'itemprop': 'postalCode'}).text
        
        phone_number = soup.find('span', {'itemprop': 'telephone'}).text

        store_number = soup.find('div', {'class': 'StoreDetails-storeNum'}).text.replace('Store Number', '').replace('#', '').strip()

        hours_json = json.loads(soup.find('div', {'class': 'js-location-hours'})['data-days'])
        hours = ''
        for h in hours_json:
            
            day_of_week = h['day']
            opening = str(h['intervals'][0]['start'])[:-2] + ':' + str(h['intervals'][0]['start'])[-2:]
            if h['intervals'][0]['end'] == 0:
                closing = 'Midnight'
            else:
                closing = str(h['intervals'][0]['end'])[:-2] + ':' + str(h['intervals'][0]['end'])[-2:]
            hours += day_of_week + ' ' + opening + ' - ' + closing + ' '
        
        hours = hours.strip()
        
        country_code = 'US'
        location_type = '<MISSING>'
        page_url = link
        
        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code, 
                    store_number, phone_number, location_type, lat, longit, hours, page_url]
        all_store_data.append(store_data)
        
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()

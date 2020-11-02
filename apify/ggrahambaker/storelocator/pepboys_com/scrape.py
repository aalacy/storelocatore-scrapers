import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import json

session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    locator_domain = 'https://www.pepboys.com/'
    to_scrape = 'https://stores.pepboys.com/'
    page = session.get(to_scrape)
    assert page.status_code == 200
    soup = BeautifulSoup(page.content, 'html.parser')
    main = soup.find('div', {'class': 'c-directory-list'})
    states = main.find_all('a', {'class': 'c-directory-list-content-item-link'})
    
    state_list = []
    city_list = []
    link_list = []
    for state in states:
        link = to_scrape + state['href']
        if len(link) > 34:
            link_list.append(link)
        else:
            state_list.append(link)

    for state in state_list:
        page = session.get(state)
        assert page.status_code == 200
        soup = BeautifulSoup(page.content, 'html.parser')
        main = soup.find('div', {'class': 'c-directory-list'})
        cities = main.find_all('a', {'class': 'c-directory-list-content-item-link'})
        for city in cities:
            link = to_scrape + city['href']
    
            if len(link.split('/')) == 5:
                city_list.append(link)
            else:
                link_list.append(link)

    for city in city_list:
        page = session.get(city)
        assert page.status_code == 200
        soup = BeautifulSoup(page.content, 'html.parser')
        
        locs = soup.find_all('a', {'class': 'Teaser-titleLink'})
        for loc in locs:
            link = loc['href']
            link_list.append(link)

    all_store_data = []

    for i, link in enumerate(link_list):
        if '..' in link:
            link = link.replace('../', to_scrape)
        page = session.get(link)
        assert page.status_code == 200
        soup = BeautifulSoup(page.content, 'html.parser')
        lat = soup.find('meta', itemprop="latitude")['content']
        longit = soup.find('meta', itemprop="longitude")['content']
        
        location_name = soup.find('h1', {'id': 'location-name'}).text.strip()
        street_address = soup.find('span', itemprop="streetAddress").text.strip()
        
        city = soup.find('span', itemprop='addressLocality').text.strip()
        
        state = soup.find('abbr', itemprop="addressRegion")
        if state == None:
            state = soup.find('abbr', itemprop="addressCountry")
        
        state = state.text.strip()
        
        zip_code = soup.find('span', itemprop="postalCode").text.strip()
        
        phone_number = soup.find('a', {'class': 'Nap-phoneLink'}).text.strip()
        
        hours_json = json.loads(soup.find('div', {'class': 'c-location-hours-details-wrapper'})['data-days'])
        
        hours = ''
        for day_of_week in hours_json:
            day = day_of_week['day']
            if len(day_of_week['intervals']) == 0:
                hours += day + ' Closed '
                continue

            start_temp = str(day_of_week['intervals'][0]['start'])
            start = start_temp[:-2] + ':' + start_temp[-2:]
            end_temp = str(day_of_week['intervals'][0]['end'])
            end = end_temp[:-2] + ':' + end_temp[-2:]

            hours += day + ' ' + str(start) + ' : ' + str(end) + ' '

        hours = hours.strip()
        
        country_code = 'US'

        location_type = '<MISSING>'
        page_url = link
        store_number = '<MISSING>'
        
        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                            store_number, phone_number, location_type, lat, longit, hours, page_url]

        all_store_data.append(store_data)

    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()

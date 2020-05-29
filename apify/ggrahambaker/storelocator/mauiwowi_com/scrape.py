import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup

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

    locator_domain = 'http://www.mauiwowi.com/' 
    ext = 'Locations'
    r = session.get(locator_domain + ext, headers = HEADERS)

    soup = BeautifulSoup(r.content, 'html.parser')
    locs = soup.find_all('div', {'class': 'divOpLLItemDescTopName'})

    link_list = []
    for loc in locs:
        link = loc.find('a')['href']
        if '/US/' not in link:
            continue

        link_list.append(locator_domain + link)

        all_store_data = []
    for link in link_list:
        r = session.get(link, headers = HEADERS)
        soup = BeautifulSoup(r.content, 'html.parser')
        
        location_name = soup.find('div', {'class': 'divSdCmsLBServiceArea'}).text.strip()
        store_number = link.split('/')[-1]
        
        city = link.split('/')[-2].replace('-', ' ')
        
        state = link.split('/')[-3].replace('-', ' ')
        
        has_phone_number = soup.find_all('div', {'class': 'divSdCmsLBPhone'})
        if len(has_phone_number) > 0:
            phone_number = has_phone_number[0].text.strip()
        else:
            phone_number = '<MISSING>'

        if phone_number == '':
            phone_number = '<MISSING>'
        
        lines = soup.prettify().split('\n')
        for line in lines:
            if 'var lat' in line.strip():
                lat = line.strip().split('"')[1]
                
            if 'var lng' in line.strip():
                longit = line.strip().split('"')[1]
        
        if lat == '0.00000000':
            lat = '<MISSING>'
            longit = '<MISSING>'
        
        country_code = 'US'
        street_address = '<MISSING>'
        zip_code = '<MISSING>'
        location_type = '<MISSING>'
        page_url = link
        hours = '<MISSING>'
        
        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code, 
                    store_number, phone_number, location_type, lat, longit, hours, page_url]

        all_store_data.append(store_data)

    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()

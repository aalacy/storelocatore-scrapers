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

    locator_domain = 'https://www.covenanthealth.org/' 
    ext = 'contact-us/locations/'
    r = session.get(locator_domain + ext, headers = HEADERS)

    soup = BeautifulSoup(r.content, 'html.parser')

    locs = soup.find_all('div', {'class': 'article'})

    all_store_data = []

    for loc in locs:
        uls = loc.find_all('ul')
        if len(uls) == 2:
            location_name = loc.find('h2').text
            lis = uls[0].find_all('li')
            addy = lis[0].find_all('span')

            phone_number = lis[1].text.strip()
            
            page_url = locator_domain[:-1] + uls[1].find_all('li')[1].find('a')['href']
            
        else:
            location_name = loc.find('h2').text
            lis = uls[0].find_all('li')
            addy = lis[0].find_all('span')

            phone_number = lis[0].find('a').text.strip()
            if 'Get Directions' in phone_number:
                phone_number = '<MISSING>'
            page_url = '<MISSING>'
            
        if len(addy) == 5:
            street_address = addy[0].text
            city = addy[2].text
            state = addy[3].text
            zip_code = addy[4].text
        else:
            street_address = addy[0].text
            city = addy[1].text
            state = addy[2].text
            zip_code = addy[3].text
        
        country_code = 'US'
        store_number = '<MISSING>'
        location_type = '<MISSING>'
        hours = '<MISSING>'
        lat = '<MISSING>'
        longit = '<MISSING>'
        
        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code, 
                    store_number, phone_number, location_type, lat, longit, hours, page_url]

        all_store_data.append(store_data)

    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()

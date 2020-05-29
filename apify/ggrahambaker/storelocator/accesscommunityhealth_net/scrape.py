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

    locator_domain = 'https://www.achn.net/' 
    ext = 'locations/'
    r = session.get(locator_domain + ext, headers = HEADERS)

    soup = BeautifulSoup(r.content, 'html.parser')
    locs = soup.find_all('div', {'class': 'search-result'})

    link_list = []
    for loc in locs:
        link = loc.find('a')['href']
        link_list.append(locator_domain[:-1] + link)

    all_store_data = []
    for link in link_list:
        r = session.get(link, headers = HEADERS)
        soup = BeautifulSoup(r.content, 'html.parser')
        
        h_days = soup.find('div', {'class': 'location-hours'})
        
        if h_days == None:
            hours = '<MISSING>'
        else:
            h_days = soup.find('div', {'class': 'location-hours'}).find_all('li')
            hours = ''
            for h in h_days:
                hours += h.text + ' '

        street_address = soup.find('div', {'itemprop': 'streetAddress'}).text
        if 'closed' in street_address:
            continue
        
        street_address = street_address.split(',')[0].replace('Chicago', '').strip()

        city = soup.find('span', {'itemprop': 'addressLocality'}).text
        state = soup.find('span', {'itemprop': 'addressRegion'}).text
        zip_code = soup.find('span', {'itemprop': 'postalCode'}).text
        location_name = soup.find('h1', {'itemprop': 'name'}).text
        
        phone_number = soup.find('div', {'itemprop': 'telephone'}).find('a').text    
        
        country_code = 'US'
        store_number = '<MISSING>'
        location_type = '<MISSING>'
        lat = '<MISSING>'
        longit = '<MISSING>'
        page_url = link
        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code, 
                    store_number, phone_number, location_type, lat, longit, hours, page_url]

        all_store_data.append(store_data)
        
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()

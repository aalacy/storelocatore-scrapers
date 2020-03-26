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


def addy_ext(addy):
    addy = addy.split(',')
    city = addy[0]
    state_zip = addy[1].strip().split(' ')
    state = state_zip[0]
    zip_code = state_zip[1]
    return city, state, zip_code


def fetch_data():
    session = SgRequests()
    HEADERS = { 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36' }

    locator_domain = 'https://ffohome.com/' 
    ext = 'allshops'
    r = session.get(locator_domain + ext, headers = HEADERS)
    soup = BeautifulSoup(r.content, 'html.parser')

    locs = soup.find_all('div', {'class': 'info-wrap'})

    all_store_data = []
    for loc in locs:
        location_name = loc.find('a', {'class': 'shop-link'}).text
        page_url = locator_domain[:-1] + loc.find('a', {'class': 'shop-link'})['href']
        
        google_href = loc.find('a', {'class': 'show-directions'})['href'].split('+')
        lat = google_href[1].replace('/', '').replace(',', '').strip()
        longit = google_href[2]
        
        addy = loc.find('div', {'class': 'ffo-store-loc'}).find_all('span')
    
        if len(addy) == 1:
            street_address = '1 Furniture Ln'
            city, state, zip_code = addy_ext(addy[0].text)
        else:
            street_address = addy[0].text
            city, state, zip_code = addy_ext(addy[1].text)
    


        phone_number = loc.find('p', {'class': 'phone-number'}).find('a').text
        
        
        hours_div = loc.find_all('div', {'class': 'ffo-store-hours'})
        if len(hours_div) > 0:
            hours = hours_div[0].find('p').text.replace('mS', 'm S').replace('dS', 'd S')
        else:
            hours = loc.find('div', {'class': 'ffo_store_address'}).find_all('p')[1].text.replace('mS', 'm S').replace('dS', 'd S')

            

        country_code = 'US'
        store_number = '<MISSING>'
        location_type = '<MISSING>'
        
        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code, 
                    store_number, phone_number, location_type, lat, longit, hours, page_url]


        all_store_data.append(store_data)
        


    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()

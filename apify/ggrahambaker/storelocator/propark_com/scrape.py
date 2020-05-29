import csv
import os
from sgselenium import SgSelenium

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

    locator_domain = 'https://www.propark.com/' 
    ext = 'locations/'
    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)

    page_source = driver.page_source

    driver.quit()

    soup = BeautifulSoup(page_source, 'html.parser')

    locs = soup.find_all('div', {'class': 'box-wrap'})

    pop_up_tracker = []
    all_store_data = []
    dup_tracker = []
    for loc in locs:

        addy = loc.find('h4').text
        links = loc.find_all('a')
        if len(links) == 1:
            pop_up_link = links[0]['href'].replace('#', '').strip()
            coords = ['<MISSING>', '<MISSING>']
        else:        
            google_link = links[0]['href']
            start = google_link.find('@')
            if start < 0:
                if 'goo.gl/' in google_link:
                    coords = ['<MISSING>', '<MISSING>']
                elif google_link.find('?ll=') > 0:
                    start = google_link.find('?ll=')
                    end = google_link.find('&')
                    coords = google_link[start + 4:end].split(',')[:2]
                else:
                    nice = 0
                    
            else:
                end = google_link.find(',17z')
                coords = google_link[start + 1:end].split(',')[:2]

            pop_up_link = links[1]['href'].replace('#', '').strip()

        if pop_up_link not in pop_up_tracker:
            pop_up_tracker.append(pop_up_link)
        else:
            continue

        pop = soup.find('div', {'id': pop_up_link})
        location_name = pop.find('h3').text
        tds = pop.find_all('td')
        hours = ''
        phone_number = ''
        for td in tds:
            
            if 'PHONE' in td.text:
                phone_number = td.text.replace('PHONE', '')
                phone_number = ' '.join(phone_number.split())  
                
            if 'HOURS' in td.text:
                hours = td.text.replace('HOURS OF OPERATION', '')
                hours = ' '.join(hours.split())  
                
        if hours == '':
            hours = '<MISSING>'
        if phone_number == '':
            phone_number = '<MISSING>'
        
        if 'or' in phone_number:
            phone_number = phone_number.split('or')[0].strip()
        
        if '&' in phone_number:
            phone_number = phone_number.split('&')[0].strip()

        if '51 Depot Road Berlin' in addy:
            street_address = '51 Depot Road'
            city = 'Berlin'
            state = 'CT'
            zip_code = '06037'
        elif '24 Colony Street' in addy:
            street_address = '24 Colony Street'
            city = 'Meriden'
            state = 'CT'
            zip_code = '06450'
            
        elif '60 State Street' in addy:
            street_address = '60 State Street'
            city = 'Meriden'
            state = 'CT'
            zip_code = '06450'
        elif '40, 50, 60 Weston St' in addy:
            street_address = '40, 50, 60 Weston St'
            city = 'Hartford'
            state = 'CT'
            zip_code = '06103'
        
        else:
            if 'Enter from either: 93 Union St.' in addy:
                addy = '52 Olive St, New Haven, CT 06510'
            
            if '343 N Cherry Street Wallingford CT 06492' in addy:
                addy = '343 N Cherry Street, Wallingford, CT 06492'
                
            if '9810 August Drive Jacksonville' in addy:
                addy = '9810 August Drive, Jacksonville, FL 32226'

            if '2 Battery Wharf, Boston.' in addy:
                addy = '2 Battery Wharf, Boston, MA 02114'

            if '34 Valley Road Montclair' in addy:
                addy = '34 Valley Road, Montclair, New Jersey 07042'
                
            if '108-03 Beach Channel Dr Far' in addy:
                addy = '108-03 Beach Channel Dr, Far Rockaway, NY 11694'
                
            if '110-45 Queens Blvd,' in addy:
                addy = '110-45 Queens Blvd, Forest Hill, NY 11375'
                
            if '44 South Broadway White Plains' in addy:
                addy = '44 South Broadway, White Plains, New York 10601'
                
            if '1000 Casteel Dr. Coraopolis' in addy:
                addy = '1000 Casteel Dr, Coraopolis, PA 15108'
                
            if '1671 Murfreesboro Pike Nashville' in addy:
                addy = '1671 Murfreesboro Pike, Nashville, TN 37217'
            if '945 Market Street' in addy:
                addy = '945 Market Street, San Francisco, CA 94103'
            if '9300 Wilshire Boulevard' in addy:
                addy = '9300 Wilshire Boulevard, Beverly Hills, CA 90212'

            if '425 1st Street' in addy:
                addy = '425 1st Street, San Francisco, California 94105'

            if '1729 H Street Northwest' in addy:
                addy = '1729 H Street Northwest, Washington, DC 20006'

            if '902 Quentin Rd' in addy:
                addy = '902 Quentin Rd, Brooklyn, NY 11223'

            if '600 Columbus Avenue' in addy:
                addy = '600 Columbus Avenue, New York, New York 10024'

            if '840 Stelzer Rd' in addy:
                addy = '840 Stelzer Rd, Columbus, Ohio 43219'
            
            addy = addy.split(',')
            if len(addy) > 1:
                if len(addy) == 4:
                    street_address = addy[0].strip() + ' ' + addy[1].strip()
                    off = 1
                else:
                    street_address = addy[0].strip()
                    off = 0

                city = addy[1 + off].strip()

                if street_address not in dup_tracker:
                    dup_tracker.append(street_address)
                else:
                    continue
                
                state_zip = ' '.join(addy[2 + off].strip().split()).split(' ')
                if len(state_zip) == 1:
                    if len(state_zip[0]) == 2:
                        state = state_zip[0]
                        zip_code = '<MISSING>'
                    else:
                        zip_code = state_zip[0]
                        state = '<MISSING>'
                elif len(state_zip) == 3:
                    state = state_zip[0] + ' ' + state_zip[1]
                    zip_code = state_zip[2]
                else:
                    state = state_zip[0]
                    zip_code = state_zip[1]
            else:
                street_address = addy[0]
                city = '<MISSING>'
                state = '<MISSING>'
                zip_code = '<MISSING>'

        if len(zip_code) == 4:
            zip_code = '<MISSING>'

        country_code = 'US'
        page_url = '<MISSING>'
        lat = coords[0]
        longit = coords[1]
        location_type = '<MISSING>'
        store_number = '<MISSING>'
        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code, 
                    store_number, phone_number, location_type, lat, longit, hours, page_url]

        all_store_data.append(store_data)
        
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()

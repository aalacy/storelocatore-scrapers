import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('grifolsplasma_com___hash_tpr')



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
    city = addy[0].strip()
    state = addy[1].strip()
    zip_code = addy[2].strip()
    return city, state, zip_code

def fetch_data():
    session = SgRequests()
    HEADERS = { 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36' }

    locator_domain = 'https://www.grifolsplasma.com/' 
    ext = 'en/locations/find-a-donation-center'
    r = session.get(locator_domain + ext, headers = HEADERS)

    soup = BeautifulSoup(r.content, 'html.parser')

    locs = soup.find_all('div', {'class': 'nearby-center-detail'})

    link_list = []
    for loc in locs:
        loc_type = loc.find('h5').text
        # logger.info(loc_type)
        if 'Talecris Plasma Resources' not in loc_type:
            continue

        link = loc.find('a')['href']
        if link not in link_list:
            link_list.append([link, loc_type])
        else:
            continue
    all_store_data = []
    for link in link_list:
        # logger.info(link[0])
        if 'https://www.grifolsplasma.com/en/-/topeka-ks' == link[0]:
            continue
        r = session.get(link[0], headers = HEADERS)
        soup = BeautifulSoup(r.content, 'html.parser')
        try:
            info = soup.find('div', {'class': 'center-address'})
            location_name = info.find('h2').text

            addy = info.find_all('p')
        except:
            continue
        
        street_address = addy[0].text
        city, state, zip_code = addy_ext(addy[1].text)
        
        phone_number = addy[2].text
        
        hours = ''
        
        days = soup.find_all('p', {'class': 'hours'})
        
        for i, d in enumerate(days):
            if i == 7:
                break
            if d.find_all('span') == 0:
                continue
            
            try:
                day = d.find('span', {'class': 'day-name'}).text
            except:
                continue
            time = d.find('span', {'class': 'day-time'}).text
            
            hours += day + ' ' + time + ' '
            
        country_code = 'US'
        store_number = '<MISSING>'
        location_type = '<MISSING>'
        page_url = link[0]
        try:
            geo = re.findall(r'[0-9]{2}\.[0-9]+;e=-[0-9]{2,3}\.[0-9]+', str(soup))[0].replace(";e=",",").split(",")
            lat = geo[0]
            longit = geo[1]
        except:
            lat = '<MISSING>'
            longit = '<MISSING>'
        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code, 
                    store_number, phone_number, location_type, lat, longit, hours.strip(), page_url]

        all_store_data.append(store_data)

    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()

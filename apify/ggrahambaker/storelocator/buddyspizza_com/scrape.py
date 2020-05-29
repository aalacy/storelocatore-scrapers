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

def addy_ext(addy):
    com_split = addy.split(',')
    city = com_split[0]
    state_zip = com_split[1].strip().split(' ')
    state = state_zip[0]
    zip_code = state_zip[1]

    return city, state, zip_code

def fetch_data():
    session = SgRequests()
    HEADERS = { 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36' }

    locator_domain = 'https://www.buddyspizza.com/'
    ext = 'all-locations'
    response = session.get(locator_domain + ext, headers = HEADERS)
    soup = BeautifulSoup(response.content, 'html.parser')

    main = soup.find('div', {'id': 'content'})
    locs = main.find_all('h3')
    link_list = []
    for loc in locs:
        link = loc.find('a')['href']

        if '#' in link:
            continue
        if 'http' in link:
            link_list.append(link)
        else:
            link_list.append('https://www.buddyspizza.com' + link )

    all_store_data = []
    for link in link_list:
        response = session.get(link, headers = HEADERS)
        soup = BeautifulSoup(response.content, 'html.parser')
        main = soup.find('div', {'id': 'content'})
        conts = main.find_all('div', {'class': 'sqs-block-content'})
        location_name = conts[0].text
        
        for cont in conts:
            if 'Address' in cont.text:
                addy = str(cont.find('p'))
                addy = addy.split('<br/>')

                street_address = addy[1]
                city, state, zip_code = addy_ext(addy[2])
                
            if 'Phone' in cont.text:
                if 'downtown detroit' in location_name:
                    print(':)')
                    phone_number = cont.find_all('p')[2].text.replace('Phone', '')
                else:
                    phone_number = cont.text.split('\n')[1]
                
            if 'Hours' in cont.text:
                hours = str(cont.find('p')).split('</strong>')[1].replace('<br/>', ' ').replace('</p>', '')
            
        map_div = json.loads(soup.find('div', {'class': 'map-block'})['data-block-json'])
        lat = map_div['location']['markerLat']
        longit = map_div['location']['markerLng']    
        
        country_code = 'US'
        store_number = '<MISSING>'
        location_type = '<MISSING>'
        page_url = link

        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code, 
                    store_number, phone_number, location_type, lat, longit, hours, page_url]

        all_store_data.append(store_data)        
        print('-----')
        
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()

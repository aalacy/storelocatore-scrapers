import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import json
import time

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

    locator_domain = 'buddyspizza.com'
    base_link  = 'https://www.buddyspizza.com/locations'
    response = session.get(base_link, headers = HEADERS)
    time.sleep(2)
    soup = BeautifulSoup(response.content, 'html.parser')

    main = soup.find('div', {'id': 'content'})
    locs = main.find_all(class_="margin-wrapper") 
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
        print(link)
        time.sleep(2)
        soup = BeautifulSoup(response.content, 'html.parser')
        main = soup.find('div', {'id': 'content'})
        conts = main.find_all('div', {'class': 'sqs-block-content'})
        location_name = soup.title.text
        
        for cont in conts:
            if 'Address' in cont.text:
                addy = str(cont.find('p'))
                addy = addy.split('<br/>')

                if "," not in addy[1]:
                    street_address = addy[1]
                    city, state, zip_code = addy_ext(addy[2])
                else:
                    street_address = ' '.join(addy[1].split()[:-3]).strip()
                    city, state, zip_code = addy_ext(' '.join(addy[1].split()[-3:]).strip())                
                
            if 'Phone' in cont.text:
                phone_number = cont.find_all('a')[-1].text.replace('Phone', '')
                
            if 'Hours' in cont.text:
                hours = str(cont.find_all('p')[-1]).split('</strong>')[1].replace('<br/>', ' ').replace('</p>', '').replace('\xa0',' ').strip()
        
        try:
            map_div = json.loads(soup.find_all('div', {'class': 'sqs-block embed-block sqs-block-embed'})[1]['data-block-json'])
        except:
            map_div = json.loads(soup.find_all('div', {'class': 'sqs-block embed-block sqs-block-embed'})[0]['data-block-json'])

        map_link = map_div['html']
        lat_pos = map_link.rfind("!3d")
        lat = map_link[lat_pos+3:map_link.find("!",lat_pos+5)].strip()
        lng_pos = map_link.find("!2d")
        longit = map_link[lng_pos+3:map_link.find("!",lng_pos+5)].strip()
        
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

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

    locator_domain = 'https://www.cnbank.com/' 
    ext = 'locations.aspx'
    r = session.get(locator_domain + ext, headers = HEADERS)

    soup = BeautifulSoup(r.content, 'html.parser')

    links = soup.find_all('a', {'class': 'link-blk_new'})
    link_list = []
    for link in links:
        if 'Branch_Pages' not in link['href']:
            continue
        if locator_domain[:-1] + link['href'] not in link_list:
            link_list.append(locator_domain[:-1] + link['href'])

    all_store_data = []
    for link in link_list:
        r = session.get(link, headers = HEADERS)
        soup = BeautifulSoup(r.content, 'html.parser')
        cont = soup.find('div', {'class': 'interiorContainer'}).find('div', {'class': 'grid_4'})
        location_name = cont.find('h1').text
        if 'Coming Soon' in location_name:
            continue
        
        phone_number = cont.find('span', {'class': 'visible-desktop'}).text
        
        addy = []
        addy_split = cont.find('p').prettify().split('\n')
        for s in addy_split:
            if '<a' in s:
                break
            if '<' in s:
                continue
            addy.append(s.strip())
        
        if len(addy) == 3:
            street_address = addy[0] + ' ' + addy[1].replace('(mailing address)', '').strip()
        else:
            street_address = addy[0]
            
        city, state, zip_code = addy_ext(addy[-1].replace('\xa0', ' '))
        
        h_rows = soup.find('table', {'class': 'branchTable'}).find_all('tr')
        hours = ''
        for row in h_rows:
            col = row.find_all('td')
            day = col[0].text.strip()
            time = col[1].text.strip() if col[1].text.strip() != '' else 'Closed'
            hours += day + ' ' + time + ' '
        
        for line in soup.prettify().split('\n'):
            if 'center:' in line.strip():
                coords = line.strip().split('(')[1].split(')')[0].split(',')
                lat = coords[0]
                longit = coords[1].strip()
                
        country_code = 'US'
        store_number = '<MISSING>'
        location_type = '<MISSING>'
        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code, 
                    store_number, phone_number, location_type, lat, longit, hours, link]

        all_store_data.append(store_data)
            
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()

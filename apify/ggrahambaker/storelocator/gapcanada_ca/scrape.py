import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re

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

    locator_domain = 'https://www.gapcanada.ca/' 
    ext = 'stores#browse-by-state-section'
    r = session.get(locator_domain + ext, headers = HEADERS)

    soup = BeautifulSoup(r.content, 'html.parser')
    ul = soup.find('ul', {'id': 'browse-content'})

    locs = [locator_domain[:-1] + l['href'] for l in ul.find_all('a')]
    city_links = []
    for l in locs:
        r = session.get(l, headers = HEADERS)
        soup = BeautifulSoup(r.content, 'html.parser')
        
        links = [a['href'] for a in soup.find_all('a', {'class': 'ga-link'})]
        for link in links:
            if '?bc=true' in link:
                continue
            city_links.append(locator_domain[:-1] + link)

    link_list = []
    for city in city_links:
        r = session.get(city, headers = HEADERS)
        soup = BeautifulSoup(r.content, 'html.parser')
        links = [a['href'] for a in soup.find_all('a', {'class': 'view-store'})]
        for link in links:
            if '?bc=true' in link:
                continue
            link_list.append(locator_domain[:-1] + link)
        
    dup_tracker = set()
    all_store_data = []
    for i, link in enumerate(link_list):
        print("Link %s of %s" %(i+1,len(link_list)))
        print(link)
        if link != "https://www.gapcanada.ca/stores/on/london/":
            r = session.get(link, headers = HEADERS)
            soup = BeautifulSoup(r.content, 'html.parser')
            
            location_name = ' '.join(soup.find('div', {'class': "location-name"}).text.split()) 
            
            addy = soup.find('p', {'class': 'address'}).find_all('span')
            street_address = ' '.join(addy[0].text.split())
      
            city, state, zip_code = addy_ext(' '.join(addy[1].text.split()))
                
            google_link = soup.find('a', {'class': 'directions'})['href']
            
            start = google_link.find('daddr=')
            coords = google_link[start + 6:].split(',')
            
            phone_number = soup.find('a', {'class': 'phone'}).text.strip()
            if phone_number == '':
                phone_number = '<MISSING>'
        
            hours_div = soup.find('div', {'class': 'hours'})
            dayparts = hours_div.find_all('span', {'class': 'daypart'})
            times = hours_div.find_all('span', {'class': 'time'})
            hours = ''
            for i, day in enumerate(dayparts):
                hours += dayparts[i].text.strip() + ' ' + times[i].text.strip() + ' ' 
            hours = hours.replace("\n","").strip()
            hours = (re.sub(' +', ' ', hours)).strip()

            country_code = 'CA'
            store_number = link.split("-")[-1]
            location_type = '<MISSING>'

            lat = coords[0]
            longit = coords[1]
            
            page_url = link
        else:
            location_name = "Wellington Commons Gap Factory Store"
            street_address = "1230 Wellington Road Suite 111"
            city, state, zip_code = "London", "ON", "N6E 1M3"
            phone_number = "(548) 482-5796"
            hours = 'Mon 10:00am - 9:00pm Tue 10:00am - 9:00pm Wed 10:00am - 9:00pm Thu 10:00am - 9:00pm Fri 10:00am - 9:00pm Sat 10:00am - 9:00pm Sun 11:00am - 6:00pm'
            country_code = 'CA'
            store_number = '<MISSING>'
            location_type = '<MISSING>'
            lat = "42.9284123"
            longit = "-81.2175352"
            page_url = link

        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code, 
                    store_number, phone_number, location_type, lat, longit, hours, page_url]
        all_store_data.append(store_data)

    return all_store_data

def addy_ext(addy):
    addy = addy.split(',')
    city = addy[0]
    state_zip = addy[1].strip().split(' ')
    if len(state_zip) == 4:
        print('four!!')
    else:
        state = state_zip[0]
        zip_code = state_zip[1] + ' ' + state_zip[2]
    return city, state, zip_code

def scrape():
    data = fetch_data()
    write_output(data)

scrape()

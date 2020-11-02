import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('seamar_org')



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
    if len(addy) == 3:
        city = addy[0]
        state = addy[1]
        zip_code = addy[2]
    else:
        city = addy[0]
        state_zip = addy[1].strip().split(' ')
        state = state_zip[0]
        zip_code = state_zip[1]
    return city, state, zip_code

def fetch_data():
    session = SgRequests()
    HEADERS = { 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36' }

    locator_domain = 'https://seamar.org/' 
    ext = 'seamar-clinics.html'
    r = session.get(locator_domain + ext, headers = HEADERS)

    soup = BeautifulSoup(r.content, 'html.parser')

    alpha = soup.find_all('ul', {'class': 'ul1'})
    dup_tracker = []
    link_list = []
    for a in alpha:
        counties = a.find_all('li')
        for c in counties:
            link = locator_domain + c.find('a')['href']
            if link not in dup_tracker:
                dup_tracker.append(link)
            else:
                continue

            link_list.append(link)

    all_store_data = []
    for link in link_list:
        r = session.get(link, headers = HEADERS)
        soup = BeautifulSoup(r.content, 'html.parser')
        cats = soup.find_all('section', {'class': 'detailed-services'})
        
        for cat in cats:
            location_type = cat.find('div', {'class': 'widget-title'}).text
   
            dls = cat.find_all('dl')
            for d in dls:
                location_name = d.find('dt').text
                cols = d.find('dd').find_all('ul')
                off = 0
                if len(cols) == 2:
                    info = cols[0].find_all('li')
                    
                    hours_raw = cols[1].prettify().split('\n')
                    hours_arr = [h for h in hours_raw if '<' not in h]
                    #logger.info(hours_arr)
                    hours = ''
                    for h in hours_arr:
                        if 'Hours' in h:
                            continue
                        if 'More Info' in h:
                            break
                        
                        hours += h.strip() + ' '
                    if 'Mount Vernon Dental Clinic' in location_name:
                        page_url = 'https://seamar.org/skagit-dental-mountvernon.html'
                    elif 'Health Education - Bellevue' in location_name:
                        page_url = 'https://seamar.org/health-education.html'
                    else:
                        page_url = locator_domain + cols[1].find('a')['href']
                        
                    if '228 W First Street' in info[1].text:
                        street_address = info[1].text.strip()
                        city, state, zip_code = addy_ext(info[2].text.strip())
                        phone_number = info[3].text.replace('P:', '').strip()

                    else: 
                        if 'Mobile' in info[1].text:
                            off = 1
                        else:
                            off = 0

                        addy_raw = info[1 + off].prettify().split('\n')
                        addy = [a.strip() for a in addy_raw if '<' not in a]

                        street_address = addy[0]
                        if '12835 Bel-Red Rd, Suite 145' in street_address:
                            city, state, zip_code = addy_ext(addy[2])
                        elif 'Everett Community College' in street_address:
                            street_address = addy[1]
                            city, state, zip_code = addy_ext(addy[2])
                        elif '14090 Fryelands Blvd SE' in street_address:
                            city, state, zip_code = addy_ext(addy[2])
                        elif '10217 125th St. Ct. E.' in street_address:
                            city, state, zip_code = addy_ext(addy[-2])
                        else:
                            city, state, zip_code = addy_ext(addy[1])

                        if len(addy) > 3:
                            phone_number = addy[2].replace('P:', '').strip()
                        else:
                            phone_number = info[2 + off].text.replace('P:', '').strip()
                
                else:
                    info_raw = cols[0].prettify().split('\n')
                    
                    info = [a.strip() for a in info_raw if '<' not in a]
                    
                    if info[-1] == '':
                        info = info[:-1]
                        
                    if len(info) == 2:
                        continue
                        
                    elif len(info) == 2:
                        continue
                    elif len(info) > 3:
                        if 'Kent Medical' in info[0]:
                            start = 2
                        else:
                            start = 1
                        
                        street_address = info[start]
                        city, state, zip_code = addy_ext(info[start + 1])
                        page_url = '<MISSING>'
                        if len(info) == 3:
                            phone_number = '<MISSING>'
                            hours = '<MISSING>'
                        else:
                            phone_number = info[start + 2].replace('P:', '').strip()
                            hours = '<MISSING>'
                            
                country_code = 'US'
                store_number = '<MISSING>'
                lat ='<MISSING>'
                longit = '<MISSING>'
                if '-->' in hours:
                    hours = '<MISSING>'

                if hours.strip() == '':
                    hours = '<MISSING>'

                if '14090 Fryelands' in street_address:
                    phone_number = '360.512.2044'

                if '10217 125th' in street_address:
                    phone_number = '253.864.4550'
                    
                if "12835 Bel-Red Rd," in street_address:
                    phone_number = '425.460.7114'

                if '2000 Tower Street' in street_address:
                    phone_number = '425.259.8738'

                street_address = street_address.split(',')[0].split('Suite')[0].strip()

                phone_number = phone_number.split('F')[0].strip()
                
                store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code, 
                            store_number, phone_number, location_type, lat, longit, hours, page_url]

                all_store_data.append(store_data)
                
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()

import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('philsbbq_net')



session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

#helper for getting address
def addy_extractor(src):
    arr = src.split(',')
    city = arr[0]
    prov_zip = arr[1].split(' ')
    if len(prov_zip) == 3:
        state = prov_zip[1]
        zip_code = prov_zip[2]
    
    return [city, state, zip_code]

def fetch_data():
   
    locator_domain = 'https://philsbbq.net/'

    ext = 'phils-bbq-locations.html'
    to_scrape = locator_domain + ext

    page = session.get(to_scrape)
    assert page.status_code == 200
    soup = BeautifulSoup(page.content, 'html.parser')

    stores = soup.find_all('div', {'class': 'locationinfo'})

    all_store_data = []
    
    ## basic case
    for store in stores:
        location_name = store.find('h2').text.strip()
        #logger.info(store.find('h3').findNext('p').text)
        hours = store.find('h3').findNext('p').text
        #logger.info(store.find_all('img'))
        img = store.find_all('a')
        
        brs = img[1].find('br')

        if brs.previousSibling.name == 'span':
            street_address = brs.previousSibling.text
        else:
            street_address = brs.previousSibling
            
        if brs.nextSibling.name == 'span':
            addy_info_arr = addy_extractor(brs.nextSibling.text)
        else:
            addy_info_arr = addy_extractor(brs.nextSibling)

        city = addy_info_arr[0]
        state = addy_info_arr[1]
        zip_code = addy_info_arr[2]
        
        phone_number = img[2].text.strip()
        store_number = '<MISSING>'
        location_type = '<MISSING>'
        lat = '<MISSING>'
        longit = '<MISSING>'
        country_code = 'US'
        
        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                     store_number, phone_number, location_type, lat, longit, hours ]
        all_store_data.append(store_data)

    #weird format of html, gotta dive in here
    try:
        hours = soup.find('h2', text='San Diego International Airport').nextSibling.nextSibling.nextSibling.nextSibling.nextSibling.nextSibling.text
    except:
        hours = "<MISSING>"
    try:
        store_data = [locator_domain, soup.find('h2', text='San Diego International Airport').text, '<MISSING>', 'San Diego', 'CA', '<MISSING>', 'US',
                     '<MISSING>', '<MISSING>', 'airport', '<MISSING>', '<MISSING>', hours ]
        all_store_data.append(store_data)
    except:
        pass

    ## need to hardcode this

    store_data = [locator_domain, 'Corperate Office', '3750 Sports Arena Blvd. STE 6', 'San Diego', 'CA', '92110', 'US',
                     '<MISSING>', '619.814.0050', 'office', '<MISSING>', '<MISSING>', '<MISSING>' ]
    all_store_data.append(store_data)

    ## need to hardcode this

    store_data = [locator_domain, 'Petco Park', '<MISSING>', 'San Diego', 'CA', '<MISSING>', 'US',
                     '<MISSING>', '<MISSING>', '<MISSING>', '<MISSING>', '<MISSING>', '<MISSING>' ]
    all_store_data.append(store_data)

    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()

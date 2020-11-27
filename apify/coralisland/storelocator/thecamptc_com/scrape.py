from bs4 import BeautifulSoup
import csv
import re
from sgrequests import SgRequests

from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('thecamptc_com')



base_url = 'https://www.thecamptc.com'

def validate(item):    
    if item == None:
        item = ''
    if type(item) == int or type(item) == float:
        item = str(item)
    if type(item) == list:
        item = ' '.join(item)
    return item.strip()

def get_value(item):
    if item == None :
        item = '<MISSING>'
    item = validate(item)
    if item == '':
        item = '<MISSING>'
    return item

def eliminate_space(items):
    rets = []
    for item in items:
        item = validate(item)
        if item != '':
            rets.append(item)
    return rets

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():

    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
    HEADERS = {'User-Agent' : user_agent}

    session = SgRequests()

    output_list = []
    url = "https://www.thecamptc.com/locations.php"

    req = session.get(url, headers = HEADERS)
    base = BeautifulSoup(req.text,"lxml")

    store_list = base.find_all(class_="location-btn")
    
    for store_link in store_list:
        store_link = validate(store_link["href"])
        if "mexicali" in store_link:
            continue
        logger.info(store_link)
        store = BeautifulSoup(session.get(store_link, headers = HEADERS).text,"lxml")
        output = []
        try:
            raw_address = list(store.find(class_='location-details').stripped_strings)
        except:
            continue
        if raw_address:
            raw_hours = eliminate_space(list(store.find_all(class_='location-details')[1].stripped_strings))[1:]
            if "opening soon" in str(raw_hours).lower():
                continue
            phone = get_value(re.findall("[(\d)]{5} [\d]{3}-[\d]{4}", ', '.join(raw_address))[0])
            zipcode = get_value(re.findall("\d{5}", ', '.join(raw_address))[-1])
            output.append(base_url) # url
            output.append(store_link) # page_url
            output.append(store.h1.text) #location name
            output.append(raw_address[1]) #address
            output.append(raw_address[2].split('\n')[0].replace(",","")) # city
            output.append(raw_address[2].split('\n')[1].strip()) # state
            output.append(zipcode) #zipcode 
            output.append('US') #country code
            output.append("<MISSING>") #store_number
            output.append(phone) #phone
            output.append("<MISSING>") #location type
            geo_loc = validate(store.iframe["src"]).split('!2d')[1].split('!2m')[0].split('!3d')
            lat = geo_loc[1]
            if len(lat) > 30:
                lat = lat[:lat.find("!")]
            output.append(lat) #latitude
            output.append(geo_loc[0]) #longitude
            output.append(validate(' '.join(raw_hours))) #opening hours 
        output_list.append(output)

    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()

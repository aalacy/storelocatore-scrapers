import csv
import re
import pdb
from sgrequests import SgRequests
from lxml import etree
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('ifratellipizza_com')



base_url = 'https://www.ifratellipizza.com'

def validate(item):    
    if type(item) == list:
        item = ' '.join(item)
    return item.replace('\n', '').replace('\t', '').strip()

def get_value(item):
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

    output_list = []
    url = "https://www.ifratellipizza.com/locations/"
    session = SgRequests()
    request = session.get(url)
    response = etree.HTML(request.text)
    store_list = response.xpath('//a[@class="action-link-2"]/@href')
    for store_link in store_list:
        logger.info(store_link)
        store = etree.HTML(session.get(store_link).text)
        output = []
        output.append(base_url) # url
        output.append(store_link)
        output.append(get_value(store.xpath('.//span[@class="heading"]//text()'))) #location name
        output.append(get_value(store.xpath('.//span[@itemprop="streetAddress"]//text()'))) #address
        output.append(get_value(store.xpath('.//span[@itemprop="addressLocality"]//text()'))) #city
        output.append(get_value(store.xpath('.//span[@itemprop="addressRegion"]//text()'))) #state
        output.append(get_value(store.xpath('.//span[@itemprop="postalCode"]//text()'))) #zipcode
        output.append('US') #country code
        output.append("<MISSING>") #store_number
        output.append(get_value(store.xpath('.//span[@itemprop="telephone"]//text()'))) #phone
        output.append("<MISSING>") #location type

        all_scripts = store.xpath('.//script')
        for script in all_scripts:
            if "LatLng" in str(script.xpath('//text()')):
                map_link = str(script.xpath('//text()')).replace('\n', '').strip()
                break
        try:
            at_pos = map_link.find("LatLng")
            latitude = map_link[at_pos+7:map_link.find(",",at_pos)].strip()
            longitude = map_link[map_link.find(",", at_pos)+1:map_link.find(")", at_pos)].strip()
        except:
            latitude = "<MISSING>"
            longitude = "<MISSING>"

        output.append(latitude) #latitude
        output.append(longitude) #longitude
        output.append(get_value(', '.join(eliminate_space(store.xpath('.//meta[@itemprop="openingHours"]//@content'))))) #opening hours
        output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()

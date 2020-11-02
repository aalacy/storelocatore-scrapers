import csv
import re
import pdb
from sgrequests import SgRequests
from lxml import etree
import json

base_url = 'https://www.mathisbrothers.com'

def validate(item):    
    if item == None:
        item = ''
    if type(item) == int or type(item) == float:
        item = str(item)
    if type(item) == list:
        item = ' '.join(item)
    return item.replace(u'\u2013', '-').strip()

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
        if item != '' and item != '<br/>':
            rets.append(item.replace('\xa0',' '))
    return rets

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    output_list = []
    url = "https://www.mathisbrothers.com/stores"
    session = SgRequests()
    response = session.get(url).text
    source = validate(response.split('data-stores="')[1].split('" class="default-page ">')[0]).replace("&quot;", '"')
    store_list = json.loads(source)
    for store in store_list:
        output = []
        output.append(base_url) # url
        try:
            output.append(get_value(store['contentURL'])) # page url
        except:
            output.append(url)
        output.append(get_value(store['name'])) #location name
        output.append(get_value(store['address1'])) #address
        output.append(get_value(store['city'])) #city
        output.append(get_value(store['stateCode'])) #state
        output.append(get_value(store['postalCode'])) #zipcode
        output.append(get_value(store['countryCode'])) #country code
        output.append(get_value(store['id'])) #store_number
        output.append(get_value(store['phone'])) #phone
        output.append(get_value(store['storeType'])) #location type
        output.append(get_value(store['latitude'])) #latitude
        output.append(get_value(store['longitude'])) #longitude
        raw_hours = get_value(store['storeHours']).replace('&lt;', '<').replace('&gt;', '>').replace('\\', '')
        hours = eliminate_space(raw_hours.split('<div class="store-hours-title">'))[0]
        if len(hours) < 50:
            hours = eliminate_space(raw_hours.split('<div class="store-hours-title">'))[1]
        hours = eliminate_space(etree.HTML(hours).xpath('.//text()'))
        store_hours = []
        for hour in hours[1:]:
            if "inform" in hour.lower():
                continue
            if ":" in hour.lower() or "pm" in hour.lower() or " am" in hour.lower() or "closed" in hour.lower():
                store_hours.append(hour)
        final_hours = ""
        for store_hour in store_hours:
            final_hours = (final_hours + " " + get_value(store_hour)).strip()
        output.append(final_hours) #opening hours
        output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()

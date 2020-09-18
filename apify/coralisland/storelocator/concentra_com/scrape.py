import csv
import re
import pdb
import requests
from lxml import etree
import json
import usaddress


base_url = 'https://www.concentra.com'


def validate(item):    
    if item == None:
        item = ''
    if type(item) == int or type(item) == float:
        item = str(item)
    if type(item) == list:
        item = ' '.join(item)
    return item.replace('\u2013', '-').strip()

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

def parse_address(address):
    address = usaddress.parse(address)
    street = ''
    city = ''
    state = ''
    zipcode = ''
    for addr in address:
        if addr[1] == 'PlaceName':
            city += addr[0].replace(',', '') + ' '
        elif addr[1] == 'ZipCode':
            zipcode = addr[0].replace(',', '')
        elif addr[1] == 'StateName':
            state = addr[0].replace(',', '') + ' '
        else:
            street += addr[0].replace(',', '') + ' '
    return { 
        'street': get_value(street), 
        'city' : get_value(city), 
        'state' : get_value(state), 
        'zipcode' : get_value(zipcode)
    }

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    output_list = []
    url = "https://www.concentra.com//sxa/search/results/?s={449ED3CA-26F3-4E6A-BF21-9808B60D936F}|{449ED3CA-26F3-4E6A-BF21-9808B60D936F}&itemid={739CBD3C-A3B6-4CA2-8004-BF6005BB28E9}&sig=&v={D907A7FD-050F-4644-92DC-267C1FDE200C}&p=10000&g="
    page_url = ''
    session = requests.Session()
    headers = {
        'accept': 'application/json, text/javascript, */*; q=0.01',
        'cookie': '__cfduid=df148d149b661935236368e45115da24f1571513396; ASP.NET_SessionId=rdu4ywszqsabendr3d1p1cxe; SC_ANALYTICS_GLOBAL_COOKIE=717a5a569c504518b3cb1003628ecec0|False; sxa_site=concentra; __cflb=685459185; Able-Player={%22preferences%22:{%22prefAltKey%22:1%2C%22prefCtrlKey%22:1%2C%22prefShiftKey%22:0%2C%22prefTranscript%22:0%2C%22prefHighlight%22:1%2C%22prefAutoScrollTranscript%22:1%2C%22prefTabbable%22:0%2C%22prefCaptions%22:1%2C%22prefCaptionsPosition%22:%22below%22%2C%22prefCaptionsFont%22:%22sans-serif%22%2C%22prefCaptionsSize%22:%22100%25%22%2C%22prefCaptionsColor%22:%22white%22%2C%22prefCaptionsBGColor%22:%22black%22%2C%22prefCaptionsOpacity%22:%22100%25%22%2C%22prefDesc%22:0%2C%22prefDescFormat%22:%22video%22%2C%22prefDescPause%22:0%2C%22prefVisibleDesc%22:1%2C%22prefSign%22:0}%2C%22sign%22:{}%2C%22transcript%22:{}}',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest'
    }
    request = session.get(url, headers=headers)
    store_list = json.loads(request.text)['Results']
    for store in store_list:
        output = []
        page_url = base_url + validate(store['Url'])
        store_info = etree.HTML(session.get(page_url).text)
        detail = store_info.xpath('.//div[contains(@class, "component content clinic-sidebar")]')[0]
        output.append(base_url) # url
        output.append(page_url) # page url
        street = get_value(detail.xpath('.//span[@itemprop="streetAddress"]//text()'))
        street2 = validate(detail.xpath('.//div[@itemprop="address"]/text()'))
        if street2 != '':
            street = street + ', ' + street2
        output.append(get_value(detail.xpath('.//*[@class="field-centername"]//text()'))) #location name
        output.append(get_value(street)) #address
        output.append(get_value(detail.xpath('.//span[@itemprop="addressLocality"]//text()'))) #city
        output.append(get_value(detail.xpath('.//span[@itemprop="addressRegion"]//text()'))) #state
        output.append(get_value(detail.xpath('.//span[@itemprop="postalCode"]//text()'))) #zipcode
        output.append('US') #country code
        output.append('<MISSING>') #store_number
        output.append(get_value(detail.xpath('.//span[@itemprop="telephone"]//text()'))) #phone
        output.append('Concentra Occupational Health') #location type
        output.append(get_value(store['Geospatial']['Latitude'])) #latitude
        output.append(get_value(store['Geospatial']['Longitude'])) #longitude
        store_hours = eliminate_space(store_info.xpath('.//div[@class="hours-container"]//text()'))[1:]
        output.append(get_value(store_hours)) #opening hours
        output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()

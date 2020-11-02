import csv
import re
import pdb
from sgrequests import SgRequests
from lxml import etree
import json
import re

base_url = 'https://www.indochino.com'

def validate(item):
    if type(item) == list:
        item = ' '.join(item)
    while True:
        if item[-1:] == ' ':
            item = item[:-1]
        else:
            break
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
    headers = {
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.135 Safari/537.36',
        'authority': 'www.indochino.com',
        'method': 'GET',
        'path': '/showrooms',
        'accept-encoding': 'gzip, deflate, br',
        'scheme': 'https',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'
    }
    output_list = []
    url = "https://www.indochino.com/showrooms"
    session = SgRequests()
    request = session.get(url, headers=headers)
    response = etree.HTML(request.text)
    store_list = response.xpath('//div[contains(@class, "showroomLocations__LOC") and boolean(@name)]')
    for store in store_list:
        link = "https://www.indochino.com" + store.xpath('./a/@href')[0].strip()
        if "virtual" in link:
            continue
        data_id = validate(store.xpath('./@data-id'))
        # if data_id == "29463" or data_id == "29934" or data_id == "29560" or data_id == "28474":
        #     continue
        country = validate(store.xpath('./@class'))
        if 'cnt-US' in country:
            country = 'US'
        else:
            country = 'CA'
        city_state = get_value(store.xpath('.//div[@class="city"]//text()'))

        output = []
        output.append(base_url) # url
        output.append(link) # url
        output.append(validate(store.xpath('./@name'))) #location name
        address = get_value(store.xpath('.//div[@class="street"]//text()')).replace("\n"," ").replace("  "," ")
        address = (re.sub(' +', ' ', address)).strip()
        output.append(address) #address
        city = city_state[:-4].strip()
        state = city_state[-2:].strip()
        if city.lower() == "new":
            city = "New York"
            state = "NY"
        output.append(city) #city
        output.append(state) #state
        output.append("<MISSING>") #zipcode
        output.append(country) #country code
        output.append(data_id) #store_number
        output.append(get_value(store.xpath('.//div[@class="tel"]//text()'))) #phone
        output.append("<MISSING>") #location type
        output.append(validate(store.xpath('./@data-latitude'))) #latitude
        output.append(validate(store.xpath('./@data-longitude'))) #longitude
        output.append(get_value(eliminate_space(store.xpath('.//div[@class="showroomLocations__hours"]//text()'))[1:]).replace('\n', '')) #opening hours
        output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()

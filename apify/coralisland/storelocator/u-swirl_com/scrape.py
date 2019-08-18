import csv
import re
import pdb
import requests
from lxml import etree
import json

base_url = 'https://www.u-swirl.com'

def validate(str):
    ret = ' '.join(str).strip();
    if ret == '':
        return '<MISSING>'
    return ret

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    output_list = []
    url = "https://www.u-swirl.com/find-a-location?page=1"
    session = requests.Session()
    request = session.get(url)
    response = request.text
    data = response.split('jQuery.extend(Drupal.settings,')[1].split('</script>')[0].strip()[:-2]
    store_list = json.loads(data)['gmap']['auto1map']['markers']
    for store in store_list:
        output = []
        detail = etree.HTML(store['text'])
        output.append(base_url) # url
        output.append(store['title']) #location name
        output.append(detail.xpath('.//span[@itemprop="streetAddress"]//text()')[0]) #address
        output.append(detail.xpath('.//span[@itemprop="addressLocality"]//text()')[0]) #city
        output.append(detail.xpath('.//span[@itemprop="addressRegion"]//text()')[0]) #state
        output.append(detail.xpath('.//span[@itemprop="postalCode"]//text()')[0]) #zipcode
        output.append('US') #country code
        output.append('<MISSING>') #store_number
        output.append(validate(detail.xpath('.//div[@class="views-field views-field-field-phone"]//text()'))) #phone
        output.append('Self-serve Yogurt Bar') #location type
        output.append(store['latitude']) #latitude
        output.append(store['longitude']) #longitude
        output.append('<MISSING>') #opening hours
        output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
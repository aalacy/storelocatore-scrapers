import csv
import re
import pdb
import requests
from lxml import etree
import json

base_url = 'https://www.jasminethaicuisinegroup.com'

def validate(item):    
    if type(item) == list:
        item = ' '.join(item)
    return item.encode('ascii', 'ignore').encode("utf8").strip()

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
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    output_list = []
    url = "https://www.jasminethaicuisinegroup.com/"
    session = requests.Session()
    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "cookie": 'dm_timezone_offset=-420; dm_last_visit=1565781608943; dm_total_visits=1; __utma=19161763.499724319.1565781612.1565781612.1565781612.1; __utmc=19161763; __utmz=19161763.1565781612.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); __utmv=19161763.52e972f79bb04c809dd3e6f495a8f2f4; __utmt_b=1; __utmt_c=1; livesite_funyzqfk9sepskc0_engage=opened; __utmt_bv=1; bvUser="BVUSER2071620705"; dm_last_page_view=1565781626595; dm_this_page_view=1565781691446; _sp_id.9aaa=0dda7b3965c18a29.1565781613.1.1565781692.1565781613; _sp_ses.9aaa=1565783491623; __utmb=19161763.17.10.1565781612',
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36"
    }
    request = session.get(url, headers=headers)
    response = etree.HTML(request.text)
    store_list = response.xpath('//ul[@class="unifiednav__container unifiednav__container_sub-nav"]')[0].xpath('./li/a/@href')
    for link in store_list:
        link = base_url + link
        data = etree.HTML(session.get(link, headers=headers).text)
        store = eliminate_space(data.xpath('.//div[contains(@class, "dmRespCol  large-4  medium-4  small-12")]')[1].xpath('.//text()'))
        output = []
        output.append(base_url) # url
        output.append(store[0]) #location name
        output.append(store[1]) #address
        address = store[2].strip().split(',')
        output.append(address[0]) #city
        output.append(address[1].strip().split(' ')[0]) #state
        output.append(address[1].strip().split(' ')[1]) #zipcode
        output.append('US') #country code
        output.append("<MISSING>") #store_number
        output.append(store[3]) #phone
        output.append("Jasmine Thai Cuisine") #location type
        output.append(get_value(data.xpath('.//div[contains(@class, "inlineMap")]/@data-lat'))) #latitude
        output.append(get_value(data.xpath('.//div[contains(@class, "inlineMap")]/@data-lng'))) #longitude
        output.append(', '.join(store[4:-2])) #opening hours
        output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()

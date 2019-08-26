import csv
import re
import pdb
import requests
from lxml import etree
import json

base_url = 'https://www.kittles.com'

def validate(item):    
    if type(item) == list:
        item = ' '.join(item)
    return item.encode('ascii', 'ignore').encode("utf8").replace('\n', '').replace('\r','').strip()

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
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    output_list = []
    url = "https://www.kittles.com/storelocations.inc"
    session = requests.Session()
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        'accept-encoding': 'gzip, deflate, br',
        'cookie': '__cfduid=d20fbe58dce567547a60b5d218061b6331566384662; ASP.NET_SessionId=maala1ncmnxh2zofjxdpfahi; __cfruid=bfd53862d67cdb02096288323aa9a3ac65794deb-1566466975',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
    }
    request = session.get(url, headers=headers)
    response = etree.HTML(request.text)        
    store_list = response.xpath('.//div[@id="staticpagenav"]//a')
    for link in store_list:
        name = get_value(link.xpath('.//text()'))
        link = base_url + validate(link.xpath('./@href'))
        data = etree.HTML(session.get(link, headers=headers).text)
        store = json.loads(validate(data.xpath('//script[@type="application/ld+json"]')[1].xpath('.//text()')).replace('- -', '-'))
        store_hours = ', '.join(eliminate_space(data.xpath('.//div[@class="store-locations-info"]')[1].xpath('.//text()'))[1:])
        output = []
        output.append(base_url) # url
        output.append(name) #location name
        output.append(store['address']['streetAddress']) #address
        output.append(store['address']['addressLocality']) #city
        output.append(store['address']['addressRegion']) #state
        output.append(store['address']['postalCode']) #zipcode
        output.append(store['address']['addressCountry']) #country code
        output.append("<MISSING>") #store_number
        output.append(store['telephone']) #phone
        output.append("Kittle's Furniture and Mattress Stores") #location type
        output.append(str(store['geo']['latitude'])) #latitude
        output.append(str(store['geo']['longitude'])) #longitude          
        output.append(store_hours) #opening hours
        output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()

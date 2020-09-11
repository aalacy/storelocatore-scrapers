import csv
import re
import pdb
import requests
from lxml import etree
import json

base_url = 'https://marcherichelieu.ca'

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
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    output_list = []
    url = "https://marcherichelieu.ca/nous-trouver"
    session = requests.Session()
    source = session.get(url).text
    response = etree.HTML(source)
    store_list = response.xpath('//table[@class="table table-striped"]//tbody//tr')
    for link in store_list:
        link = base_url + link.xpath('.//a/@href')[-1]
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
            'Cookie': 'languageId=fr; storeId=8; storeCode=R1007; storeName=Marche Richelieu - Marche Chauvin; storeInfo=7890 Rue St-Denis, Montreal, Quebec 514-271-7367; NSC_qspe-nfusp-dng-xxx_iuuqt=ffffffffaf17097e45525d5f4f58455e445a4a42378b',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36'
        }
        data = session.get(link, headers=headers).text
        data = validate(data.split('var storeJsonLd = "')[1].split('";')[0]).replace('\\n', '').replace('\\', '')
        store = json.loads(data)
        output = []
        output.append(base_url) # url
        output.append(get_value(store['name'].replace('u00E9', 'e').replace('u00C9', 'E').replace('u0026', '&'))) #location name
        address = store['address']['streetAddress'].replace('u00E9', 'e').replace('u00C9', 'E').replace('u0026', '&').split(',')
        output.append(get_value(address[:-2])) #address
        output.append(get_value(address[-2])) #city
        output.append(get_value(store['address']['addressRegion'])) #state
        output.append(get_value(store['address']['postalCode'])) #zipcode
        output.append(get_value(store['address']['addressCountry'])) #country code
        output.append('<MISSING>') #store_number
        output.append(get_value(store['telephone'])) #phone
        output.append('Richelieu Market') #location type
        output.append(get_value(store['geo']['latitude'])) #latitude
        output.append(get_value(store['geo']['longitude'])) #longitude
        store_hours = []
        for hour in store['openingHoursSpecification']:
            store_hours.append(hour['dayOfWeek'] + ' ' + hour['opens'] + ' - ' + hour['closes'])
        output.append(get_value(store_hours)) #opening hours
        output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()

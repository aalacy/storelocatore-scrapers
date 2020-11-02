import csv
import re
import pdb
import requests
from lxml import etree
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('supershoes_com')




base_url = 'https://www.supershoes.com'


def validate(item):    
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
    history = []
    with open('cities.json') as data_file:    
        city_list = json.load(data_file)
    output_list = []
    url = "https://www.supershoes.com/index/page/store_locator"
    session = requests.Session()
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        'Accept-Encoding': 'gzip, deflate, br',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Cookie': 'PHPSESSID=8rvcsfpm5c2bpd9b6u6m8bnod0; wcsid=EeZYBzX3Ri8ss2sG2n3pG0IA6aTI6kbj; hblid=1xanSm5D8qj2kRoT2n3pG0I6I6B0rEoT; _okdetect=%7B%22token%22%3A%2215665455519380%22%2C%22proto%22%3A%22https%3A%22%2C%22host%22%3A%22www.supershoes.com%22%7D; olfsk=olfsk7310642676038785; _okbk=cd4%3Dtrue%2Cvi5%3D0%2Cvi4%3D1566545553135%2Cvi3%3Dactive%2Cvi2%3Dfalse%2Cvi1%3Dfalse%2Ccd8%3Dchat%2Ccd6%3D0%2Ccd5%3Daway%2Ccd3%3Dfalse%2Ccd2%3D0%2Ccd1%3D0%2C; _ok=1020-165-10-3492; _oklv=1566545791841%2CEeZYBzX3Ri8ss2sG2n3pG0IA6aTI6kbj',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
    }
    for city in city_list:
        data = {
            'action': 'search',
            'address': city['city'],
            'distance': '500',
            'chains[]': '1'
        }
        request = session.post(url, data=data, headers=headers)
        response = etree.HTML(request.text)
        store_list = response.xpath('//div[@id="nearest"]/ul/li')
        logger.info(('~~~~~~~~~~~', city, len(store_list)))
        for store in store_list:
            store = eliminate_space(store.xpath('.//text()'))
            output = []
            uni = get_value(store[0] + store[2])
            if uni not in history:
                output.append(base_url) # url
                output.append(store[0]) #location name
                output.append(store[2]) #address
                output.append(store[3].split(',')[0].strip()) #city
                output.append(store[3].split(',')[1].strip()) #state
                output.append(store[4]) #zipcode
                output.append('US') #country code
                output.append('<MISSING>') #store_number
                output.append(store[5]) #phone
                output.append("Super Shoes") #location type
                output.append('<MISSING>') #latitude
                output.append('<MISSING>') #longitude
                output.append(', '.join(store[7:])) #opening hours
                output_list.append(output)
                history.append(uni)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()

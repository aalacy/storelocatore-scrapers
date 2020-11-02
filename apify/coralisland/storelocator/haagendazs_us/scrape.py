import csv
import re
import pdb
import requests
from lxml import etree
import json


base_url = 'https://www.haagendazs.us'


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
    url = "https://www.haagendazs.us/locator/ws/11211/40.7093358/-73.9565551/5/0/2452?lat=40.7093358&lon=-73.9565551&radius=5&zipcode=11211&BrandFlavorID=2452&targetsearch=3"
    session = requests.Session()
    request = session.get(url)
    store_list = json.loads(request.text)
    for store in store_list:
        output = []
        output.append(base_url) # url
        output.append(get_value(store['Name'])) #location name
        output.append(get_value(store['Shop_Street__c'])) #address
        output.append(get_value(store['Shop_City__c'])) #city
        output.append(get_value(store['Shop_State_Province__c'])) #state
        output.append(get_value(store['Shop_Zip_Postal_Code__c'])) #zipcode
        output.append('US') #country code
        output.append(get_value(store['Id'])) #store_number
        output.append(get_value(store['phone'])) #phone
        output.append('Haagen-Dazs Ice Cream, Bars and Sorbet') #location type
        output.append(get_value(store['lat__c'])) #latitude
        output.append(get_value(store['lon__c'])) #longitude
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
            'Cookie': 'visid_incap_1323197=WlWQi1q2QM2Ga2T1jxpp02IkXV0AAAAAQUIPAAAAAAD+NwLbfbfai9Ake96Xbxrd; ps-location=13.36667%7C103.85%7CKH%7C-%7CSiemreab%7CSiem%20Reab%7CSiemreab%2C%20Siem%20Reab%7C; liveagent_oref=; liveagent_ptid=8af7008b-2edd-494c-9177-42f7376f26ab; incap_ses_219_1323197=4GBRd3jNIC5DaUosnQ4KAxz9bF0AAAAAz/bs7lthGOOyZbmOwsOreA==; liveagent_sid=052eb2c5-cbbb-478e-9619-60ae3fbcb04a; liveagent_vc=4',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36'
        }
        link = 'https://www.haagendazs.us/shops/' + get_value(store['Name']).replace(' ', '-').lower()
        detail = etree.HTML(session.get(link, headers=headers).text)
        store_hours = validate(eliminate_space(detail.xpath('.//div[@class="office-hours__item"]//text()')))
        output.append(store_hours) #opening hours
        output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()

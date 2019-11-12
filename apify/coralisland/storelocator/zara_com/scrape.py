import csv
import re
import pdb
import requests
from lxml import etree
import json
import usaddress


base_url = 'https://www.prestigepreschoolacademy.com'


def validate(item):    
    if item == None:
        item = ''
    if type(item) == int or type(item) == float:
        item = str(item)
    if type(item) == list:
        item = ' '.join(item)
    return item.replace(u'\u2013', '-').encode('ascii', 'ignore').encode("utf8").strip()

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
        for row in data:
            writer.writerow(row)

def fetch_data():
    output_list = []
    history = []
    with open('./cities.json') as data_file:    
        city_list = json.load(data_file)
    page_url = ''
    session = requests.Session()
    headers = {
        'accept': 'application/json, text/javascript, */*; q=0.01',
        'accept-encoding': 'gzip, deflate, br',
        'cookie': 'socControl=https%3A%2F%2Fwww.zara.com; rid=2d2b33b8-7afc-410d-ac95-bd53b8d204a0; _abck=9A9F6CD3CAA5110385C2B0A79955F22F~0~YAAQcFVqy88vl2FtAQAAXWTKdwJ7SCvAuXJZIUShcX3wIPJvN54eqFINbIgoLVmUYw7FifPD2UXjVBwgIUDIsj36QaZeJGtuPbAMCKV4O98yeob8PGgYeMsD1scUXHs4oSMfodWZY+EY3CXvTMeFM3LQUU69Ja/Tlbg7rmN6fIvExDK2lHVvB8HO8jrhEX7SmNndIjgq3dnWwA+7ABEBUuKZ3meQ6p0CqvY8pvi7KAh3gWkNzbkwMjoS3H4Upwtf3i1NnAb5rV6Ab3zOubW8E5+ZF4qw4WcQetT8P5e3p28=~-1~-1~-1; WC_cookiesMsg=1; policyVersion=1568242800000; foreignRegionConfirmed=uk; bm_sz=8BDA9E2699C5C30839BE712C5B4C7883~YAAQmVstFwr8vfttAQAAevqhRQW803gbiqd1cgP8BVIzqcbcb1bJFF9RRvVCBR2gJZGRZYeXkWXAWNDziGlHLjMuD1uzWWHTfcHRKRCKOfA82+ZuCBI1zosKaO/pMAZ4q9MjTvnYbWVtFdehJfhy21zb3/vLTf839y5sXvGpSeeSkDtzqBKXwmxD41brRQ==; web_version=STANDARD; ak_bmsc=45268AA8975A3DEC92CE7A693985BF0D58DDDEC5672A00008300C45DEC650E36~plXEAa13QHU9ZGdmgtA0ru4gDVDNvGpmNogvUTOPnua0MLszSInp0RAADZpWfNDe+KRCBWx4w9M4ZmRT5OaCyD5EK5/3+4B3LFRH3qWrYp66lpCjN96iEQq+n2lfFh9YW2lmUlLVzTztGbT6POPaV5pfHatWwCENzpTe08HpuFQF03RB6IwoMKFmiBQ/Eb+Flm12epC1fwn4Q1vVWzwAPF4dtdrmhCxsUxT8fcTKxkiYM=; chin={"status":"chat-status:not_connected","uid":"","crid":"","email":"","userJid":"","uiCurrentView":"view:hidden","areMessagesNotRead":false,"privacyAccepted":false,"isChatAttended":false,"timeShowInteractiveChat":0}; bm_mi=305F6BCE9086E3D8095A7B67C41C2529~goaslilN7SXxj+z2TXaMhDmPSBHqPJ2StfLzl0lSbEaaD5Igi76qrFHQ+/SXGLjYAjV7tFbCqaFiu3Am3lKiGXj4mcRoKvv4CFIbgeszUxk5/2U0lzNoIPAAeFS7DFlfYQIUTVw7ygZ4EqzFN6Cg9PzKfFIo8Zh8ZLiLRIyX0f4H1RB+gmuhy5cB2kKQQkkkfZuVnVeK3aD9aCSsj3FVB/2muFROddCYxq3NMLsBImaz6+MrSUvP7kwQxrADVyry; storepath=us/en; JSESSIONID=00005FrRR4qGv9TNR8MADTJsqYH:1aa7a0571; bm_sv=27F3BDE7970FD7760106C5E09F224AD4~fuLRS2oEG7LAa4pxf31oq0x8Hnhh45+1RdOmfiSpBrzibnS22Js3klWsqdXw19T1GZW07ZeSctdrcKkQHIsvwaiIQjZYaGuOA17b+jOC5d5SpUrLo32+l6SLh2EEP9KkYOA2/1Y8PyG37kdUbYz9Vm3D3DwjIqH55YBqTiCZq4Y=',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.87 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest'
    }
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for city in city_list:
            url = "https://www.zara.com/us/en/stores-locator/search?lat="+str(city['latitude'])+"&lng="+str(city['longitude'])+"&ajax=true"
            request = session.get(url, headers=headers)
            store_list = json.loads(request.text)
            for store in store_list:        
                store_id = validate(store.get('id'))                
                if store_id not in history:
                    history.append(store_id)
                    output = []
                    output.append(base_url) # url
                    output.append(base_url) # page url
                    output.append(get_value(store.get('name'))) #location name
                    output.append(get_value(store.get('addressLines'))) #address
                    output.append(get_value(store.get('city'))) #city
                    output.append(get_value(store.get('state'))) #state
                    output.append(get_value(store.get('zipCode'))) #zipcode
                    output.append(get_value(store.get('countryCode'))) #country code
                    output.append(get_value(store_id)) #store_number
                    output.append(get_value(store.get('phones')).replace('+', '')) #phone
                    output.append('Zara Store') #location type
                    output.append(get_value(store.get('latitude'))) #latitude
                    output.append(get_value(store.get('longitude'))) #longitude
                    days_of_week = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
                    store_hours = []
                    if len(store.get(('openingHours'))) > 0:
                        for hour in store.get('openingHours'):
                            store_hours.append(days_of_week[hour['weekDay']-1] + ' ' + hour['openingHoursInterval'][0]['openTime'] + '-' + hour['openingHoursInterval'][0]['closeTime'])                        
                    output.append(get_value(store_hours)) #opening hours
                    writer.writerow(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()

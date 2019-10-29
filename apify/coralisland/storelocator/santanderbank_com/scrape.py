import csv
import re
import pdb
import requests
from lxml import etree
import json

base_url = 'https://www.santanderbank.com'

def validate(item):    
    if type(item) == list:
        item = ' '.join(item)
    return item.encode('ascii', 'ignore').encode("utf8").strip()

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

def parse_detail(store, link):    
    output = []
    output.append(base_url) # url
    output.append(link) # url
    output.append(get_value(store.xpath('.//h1[@class="Nap-mainHeader"]//text()')))#location name
    output.append(get_value(store.xpath('.//span[@itemprop="streetAddress"]//text()'))) #address    
    output.append(get_value(store.xpath('.//span[@itemprop="addressLocality"]//text()')).replace(',', '')) #city
    output.append(get_value(store.xpath('.//abbr[@itemprop="addressRegion"]//text()'))) #state
    output.append(get_value(store.xpath('.//span[@itemprop="postalCode"]//text()'))) #zipcode
    output.append('US') #country code
    output.append("<MISSING>") #store_number
    output.append(get_value(store.xpath('.//span[@itemprop="telephone"]//text()'))) #phone
    output.append("Santander Bank ATM") #location type    
    output.append('<INACCESSIBLE>') #latitude
    output.append('<INACCESSIBLE>') #longitude
    output.append(get_value(eliminate_space(store.xpath('.//table[@class="c-location-hours-details"]//tbody')[0].xpath('.//text()')))) #opening hours
    return output
    
def fetch_data():
    output_list = []
    url = "https://locations.santanderbank.com/index.html"
    session = requests.Session()
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        'cookie': '_abck=A0DD8D34C881D41A70CB983C9700605B~0~YAAQgp3+pamWZ/ZtAQAA5oRKFAKZ4yG8ydHGu1KV3rAZvNrDVIeupbY2OYkFcvNQ/02Vlet8ALPELJ7OVc9KqUtBNRlEInUuzGF9V6cRIhA4gj7PCmylyAMnI6wd79nZbnh6i6GT7/h2Q1iXrn/lfbehs8wqrHvWzohMm7N4UVw5efOBBNQ0WkZZ8vlrGZVrlgfmpp8pJa7jiKOyZO4TOOIeOiTTOuP/5Z189SrWLEVzV8UB9j+5eQyoME+7v2yZMs1LMn0KP3VQ61LBRjdsYi7r0ADBihspzXJXjVGPsy3wvpeCWMW3Y+s=~-1~-1~-1; __cfduid=d6678c001b6715a84870a765dcddddf551572298923; bm_sz=6FED51D839497D580A2C47A25E5BD083~YAAQ5D14QddmgPVtAQAA44B7GAUjMD/dzvvFKYFTVuSsGukhH9S7FxyJROW4BG1Lg/6NC5GJcdMKQOqD2pC1Zk9n72ubJcHklAWFufLpeoCgACg+FpnqZYpxphkabrqJxsZN6o+HYrpIkbA/ALtQ8tO9nrr2/BNgbCBETrPKcSFFrA9VFwRJZ+eJ6Ku2OVVNCkzYMt+QFg==; ak_bmsc=0AD057C77612B823BECAF4A082B06DB541783DE4A32300008A71B85D3771A900~plodubGFvneiBmZHsUwBbvmUBESELxnbdOMKPYX5JB11Hr30PafE7Hmzi57+fk1JtMQ7pnzcD0t42yj5TLcLSdHBdj1Oe22tX0B/vUP9oOh/SB+VKVoiPnkcRx9Yz9QUBaBaRnc8Wc9J+juIPDDrDGv6muddG7mng8ENj4zEk/NNF0FoCehVtmnvFBFsAFZse4Dc7oSdZfFtNqxbBoOCZfr0XlkFuoojh8FqtIpumPBPw=; bm_mi=CEC0B7A53061AFFC73539A7694F89D82~06cNwhbcW9KOgaYoILzPnudzjoDI+BTyD+WTB9LPi2TfI2jUlBquxjMiTxc/OCYl0pMfBi2CWaTwiWGFMehWIc8h4D55ARDRSRkh59X9KFFSNILrSlayuRhcDrzsOat88ZHpdaffWoHhZ8a7BRnklwSysrooZwaxSoxNkSzB11SE8SxLDbNh9Ug5vBrjddNwSyL/rSnCpFeyuwmm3tSsKhjOcN6sduoWCspK5TMjK7UJpVzr8zW8k/9NJ5MFewNL; utag_main=v_id:016e144a81110010581cdc57a11f03073002906b0086e$_sn:2$_ss:0$_st:1572370690158$dc_visit:2$_pn:10%3Bexp-session$ses_id:1572368779113%3Bexp-session$dc_event:4%3Bexp-session; bm_sv=483848F80A124BE79C272D23A2CB626E~Ih85/yYWezsSkHjDv5MB1aJusIBEGgXxYCRtHZ14TU21JwNe4ron83rGWuxlL1becWWeb8dQNtSJ7LyTYL9aMGjWeqA9X6aGs8G91d4r2vFzw6x8BPx/OpQSWJcA+k+O9aji2eZd8pgoQQ0SPpnIeQ/3r7rbNMHW1RHwLZLO5kY=',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.70 Safari/537.36'
    }
    url = 'https://locations.santanderbank.com'
    request = session.get(url, headers=headers)
    response = etree.HTML(request.text)    
    state_list = response.xpath('//a[@class="c-directory-list-content-item-link"]/@href')
    for state in state_list:
        state = url + '/' + state
        state_response = etree.HTML(session.get(state, headers=headers).text)
        if state_response is not None:
            city_list = state_response.xpath('//a[@class="c-directory-list-content-item-link"]/@href')
            store_list = state_response.xpath('//a[@class="location-tile-link Link"]/@href')
            if len(city_list) > 0:
                for city in city_list:
                    city = url + '/' + city
                    city_response = etree.HTML(session.get(city, headers=headers).text)
                    if city_response is not None:
                        store_list = city_response.xpath('//a[@class="location-tile-link Link"]/@href')
                        if len(store_list) > 0:
                            for store in store_list:
                                store = url + '/' + store.replace('../', '')
                                store_response = etree.HTML(session.get(store, headers=headers).text)
                                if store_response is not None:
                                    output_list.append(parse_detail(store_response, store))
                        else:                            
                            output_list.append(parse_detail(city_response, city))
            elif len(store_list) > 0:
                for store in store_list:
                    store = url + '/' + store.replace('../', '')
                    store_response = etree.HTML(session.get(store, headers=headers).text)
                    if store_response is not None:
                        output_list.append(parse_detail(store_response, store))
            else:
                output_list.append(parse_detail(state_response, state))
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()

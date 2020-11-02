import csv
import re
import pdb
import requests
from lxml import etree
import json

base_url = 'https://agents.farmers.com'

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
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def parse_detail(store, link):    
    output = []
    output.append(base_url) # url
    output.append(link) # url
    output.append(get_value(store.xpath('.//h1[@itemprop="name"]//text()')))#location name
    street = validate(store.xpath('.//span[@class="c-address-street-1"]//text()'))
    street2 = validate(store.xpath('.//span[@class="c-address-street-2"]//text()'))
    if street2 != '':
        street = street + ', ' + street2
    output.append(get_value(street)) #address    
    output.append(get_value(store.xpath('.//span[@class="c-address-city"]//text()')).replace(',', '')) #city
    output.append(get_value(store.xpath('.//abbr[@class="c-address-state"]//text()'))) #state
    output.append(get_value(store.xpath('.//span[@class="c-address-postal-code"]//text()'))) #zipcode
    output.append('US') #country code
    output.append("<MISSING>") #store_number
    output.append(get_value(store.xpath('.//span[@itemprop="telephone"]//text()'))) #phone
    output.append("Find an Insurance Agent | Farmers") #location type
    geo = validate(store.xpath('.//meta[@name="geo.position"]//@content')).split(';')
    if len(geo) > 0:
        output.append(geo[0]) #latitude
        output.append(geo[1]) #longitude
    output.append(get_value(eliminate_space(store.xpath('.//table[@class="c-location-hours-details"]//tbody//text()')))) #opening hours        
    return output

def fetch_data():
    output_list = []
    url = "https://agents.farmers.com"
    session = requests.Session()
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        'cookie': '__cfduid=d00d17a8b572dd6e05a0d700cfbb290681571517150; searchParams=%7B%22name%22%3A%22%22%2C%22state%22%3A%22AL%22%7D; searchResultOrder=%5B1547296%2C1551554%2C1547953%2C1548336%2C1552349%2C1551957%2C1546856%2C1548435%2C1553503%2C1546733%2C1552049%2C1550642%2C1551879%2C1549624%2C1549906%2C1549923%2C1551480%2C1549108%5D; rawSearchResults=%5B1547296%2C1551554%2C1547953%2C1548336%2C1552349%2C1551957%2C1546856%2C1548435%2C1553503%2C1546733%2C1552049%2C1550642%2C1551879%2C1549624%2C1549906%2C1549923%2C1551480%2C1549108%2C1546478%2C1546500%2C1546925%2C1547086%2C1547472%2C1547546%2C1547628%2C1547736%2C1547883%2C1547942%2C1548184%2C1548332%2C1548757%2C1549050%2C1549218%2C1549353%2C1551312%2C1551576%2C1551598%2C1551614%2C1551796%2C1552245%2C1552257%2C1552489%2C1552579%2C1552752%2C1552916%2C1553032%2C1553034%2C1553374%2C1553456%2C1553574%5D; lastVisitedAgent=9444986; query_params=%7B%22Source_Indicator%22%3A%22AP%22%7D; bm_sz=88E6765E5403B98B4E25C8C8306E060B~YAAQPJTerWbyT8htAQAAXNa+5QX6v17A9sSiOL0YdseiG13nfL27bJNGBo0QfSSY3xC+jJANBbBYOTIwbAw7WqKx4yPGZf0G6gFPQNN/eHk+mY91pmIXLE5cykRrM3jGnNH8sTr5+mg7zArHZhS7HHBpibUgkQ4mA2Q4/KuhKR0nDkgZrfYj0ZGGFwlIFBJYRQ==; AKA_A2=A; ak_bmsc=5B548AD4A81D3B31D79B3DE4A322BFBDADDE943CC36500007074AB5DA9604B6E~plAJ6mByz5D23TXYThzy7KhtCAcQGeLYMzUGumcCDLCdxbpX28r0/f9esvItDvlfTzrGBmrTTse2g0Nm+t1FrLIZBV1NfqTZQgsCUgPi5r1z5Bdx4wYPEezWglRAMHIOpZAOgZ8ECWHog9ugYTBYSefglKD5PxvKLOu76wV29xkovpnpEWygsOvpNDe4NWv7ZiMiu+QlZsPjG/Newl423zbkHpY2CGXWiM+WWaQg3r6/c=; check=true; mbox=session#b1838e6e99fd4272bc7a6bc116f06cdd#1571519414; bm_mi=4DA50289AB41EB4B74462A8F58E71FAE~73ahq+txiPA8SdpJb+v7zRjxWIF5v6nXhVA/ljw5/DvVxtNVkHYr/z1pMDnwwQQnoM3H5PHee+LSFU6DThbzby5ZYSSSG/X1E/uJSEuUv7R9MbCqhvlc68xP00LUo6aS63kSvJLd1yTtAeBVhogrMC4WukhrLVTaIGZ/tjQOOSM49rSrZ8zLBYQF0ET50rADIOSV0H94Le2eyGZ68JU38rkh4W3ubvbRUpwSiwVoa9Q=; bm_sv=A9A19BFD24AC2E2B3E67B6FF9F40AD34~wWdDckPUeshMIlU6sfaKRZAG7+AKMH16wQjzdXcqomJdYNKa5w/LbLDXjsmuo8kYtDmb+RAgJ0CLBhT1kHXQKeG4znn0wMYYMvy9mhQiatBj63qBTvNd53Lrg2wqMvv2yrccAXAp58p/hAZIK2pNchR1Vudcq1iUizei7H7805s=; _abck=BF4787D5C03AF1406E19A196E4652D62~0~YAAQPJTerWvyT8htAQAA+ee+5QKToH6nUWEuag/048Gm1g/trpW7lRjFkuKF4UFTFWdx58A1xrHrcE4YC3UHDK++ZVXUuosFqWmMJ4LR8ouyqrihgMv7LOyJFyg48ZanqwGyKQsChhNs2uGh7Po9z/DRjllaV9CMCYKVu+xkAXsZiAq4DSyDD+BVdHW63JYmU21i1UPJIey57SyJ2bZ/N+zUEsMhkNImFyTlhD/1LKDzqS7LSP2urLLsy+i3c5PTvMiWfyzOd1+TPZwnTbpPvynANY0SgCgkxiyUj7oH6i88S6o=~-1~-1~-1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36'
    }
    request = session.get(url, headers=headers)
    response = etree.HTML(request.text)    
    state_list = response.xpath('//a[@class="Directory-listLink"]/@href')
    for state in state_list:
        state = url + '/' + state
        state_response = etree.HTML(session.get(state, headers=headers).text)
        if state_response is not None:
            city_list = state_response.xpath('//a[@class="Directory-listLink"]/@href')
            store_list = state_response.xpath('//a[@class="location-title-link"]/@href')
            if len(city_list) > 0:
                for city in city_list:
                    city = url + '/' + city
                    city_response = etree.HTML(session.get(city, headers=headers).text)
                    if city_response is not None:
                        store_list = city_response.xpath('//a[@class="location-title-link"]/@href')
                        if len(store_list) > 0:
                            for store in store_list:
                                store = url + store[2:]
                                store_response = etree.HTML(session.get(store, headers=headers).text)
                                if store_response is not None:
                                    output_list.append(parse_detail(store_response, store))
                        else:
                            output_list.append(parse_detail(city_response, city))
            elif len(store_list) > 0:
                for store in store_list:
                    store = url + store[2:]
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

import csv
import re
import pdb
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from lxml import etree
import json
import time
from random import randint
from sglogging import sglog

log = sglog.SgLogSetup().get_logger(logger_name="blomedry.com")

base_url = 'https://blomedry.com'

def validate(item):    
    if type(item) == list:
        item = ' '.join(item)
    while True:
        if item[-1:] == ' ':
            item = item[:-1]
        else:
            break
    return item.replace(u'\u2013', '-').strip()

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

def replace_last(source_string, replace_what, replace_with):
    head, _sep, tail = source_string.rpartition(replace_what)
    return head + replace_with + tail

def fetch_data():

    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
    headers = {'User-Agent' : user_agent}

    session = SgRequests()
    output_list = []
    countries = ["US","CA"]
    for country in countries:
        url = "https://blomedry.com/locations/?country=" + country
        request = session.get(url, headers=headers)
        response = etree.HTML(request.text)
        store_list = response.xpath('//li[contains(@class, "article-location")]')
        log.info(url)
        for i, store in enumerate(store_list):
            # print("Link %s of %s" %(i+1,len(store_list)))
            detail_url = store.xpath(".//h2/a/@href")[0]
            # print(detail_url)
            latitude = store.xpath("@data-lat")[0]
            longitude = store.xpath("@data-lng")[0]

            title = store.xpath(".//h2/a/text()")[0]
            address = store.xpath(".//p/text()")
            if not address[-1].strip():
                address.pop(-1)
            try:
                street_address = get_value(address[-3]).replace(","," ").strip() + " " + get_value(address[-2]).replace(","," ").strip()
            except:
                street_address = get_value(address[-2]).replace(","," ").strip()
            city_state = validate(address[-1])
            city = city_state.split(",")[0]
            if country == "US":                
                state = city_state.split(",")[1][:-6].strip()
            else:
                state = city_state.split(",")[1][:-7].strip()
            if country == "US":
                zipcode = city_state.split(",")[1][-6:].strip()
                if zipcode == "90595" and city == "Torrance":
                    zipcode = "90505"
            else:
                zipcode = city_state.split(",")[1][-7:].strip()
            try:
                phone = store.xpath(".//p/a/text()")[0]
            except:
                continue

            try:
                req = session.get(detail_url, headers = headers)
                base = BeautifulSoup(req.text,"lxml")
                hours = base.find(class_="schedule__body").ul.text.replace("\n"," ").strip()
            except:
                hours = "<INACCESSIBLE>"

            output = []
            output.append(base_url) # url
            output.append(detail_url) # page_url
            output.append(title) #location name
            output.append(street_address) #address
            output.append(city) #city
            output.append(state) #state
            output.append(zipcode) #zipcode
            output.append(country) #country code
            output.append("<MISSING>") #store_number
            output.append(phone) #phone
            output.append("<MISSING>") #location type
            output.append(latitude) #latitude
            output.append(longitude) #longitude
            output.append(hours) #opening hours
            output_list.append(output)
        
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()

import csv
import requests
from bs4 import BeautifulSoup
import re
import http.client
import json
import  pprint
import phonenumbers 


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    base_url = "https://www.biggby.com/"
    conn = http.client.HTTPSConnection("guess.radius8.com")

    addresses = []
 
    header = {'User-agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.9.1.5) Gecko/20091102 Firefox/3.5.5',
              'Content-type': 'application/x-www-form-urlencoded'}






    data = "https://www.biggby.com/locations/"
    r = requests.get(data, headers=header)
    soup = BeautifulSoup(r.text, "lxml")
    for val in soup.find('div',{'id':'loc-list'}).find_all('marker'):
        phone =''
        data ="action=biggby_get_location_data&security=5ebc69a720&post_id="+val['pid']
        loc = requests.post("https://biggby.com/wp-admin/admin-ajax.php", headers=header,data=data).json()
        if loc['phone-number'] != None:
            phone1 = loc['phone-number'].replace("not available",'').replace("unavailable",'').replace("TBD","")
        
        if phone1:
            phone = phonenumbers.format_number(phonenumbers.parse(str(phone1).replace("-",''), 'US'), phonenumbers.PhoneNumberFormat.NATIONAL)
            # print(phone)

        locator_domain = base_url
        location_name =  val['name']
        street_address = val['address-one'] +" "+val['address-two']
        city = val['city']
        state =  val['state']
        zip =  val['zip']
        country_code = val['country']
        store_number = val['id']
        location_type = 'biggby'
        latitude = val['lat']
        longitude = val['lng']
        hours_of_operation = ' mon-thurs-open-hour ' + val['mon-thurs-open-hour']+" mon-thurs-close-hour "+val['mon-thurs-close-hour']+" fri-open-hour "+val['fri-open-hour']+" fri-close-hour "+val['fri-close-hour']+" sat-open-hour "+val['sat-open-hour']+" sat-close-hour "+val['sat-close-hour']+" sun-open-hour "+val['sun-open-hour']+" sun-close-hour "+val['sun-close-hour']
        page_url = 'https://www.biggby.com/locations/'
        if street_address in addresses:
            continue
        addresses.append(street_address)
        store = []
        store.append(locator_domain if locator_domain else '<MISSING>')
        store.append(location_name if location_name else '<MISSING>')
        store.append(street_address if street_address else '<MISSING>')
        store.append(city if city else '<MISSING>')
        store.append(state if state else '<MISSING>')
        store.append(zip if zip else '<MISSING>')
        store.append(country_code if country_code else '<MISSING>')
        store.append(store_number if store_number else '<MISSING>')
        store.append(phone if phone else '<MISSING>')
        store.append('<MISSING>')
        store.append(latitude if latitude else '<MISSING>')
        store.append(longitude if longitude else '<MISSING>')
        store.append(hours_of_operation if hours_of_operation else '<MISSING>')
        store.append(page_url if page_url else '<MISSING>')
        # print("===", str(store))
        yield  store


def scrape():
    data = fetch_data()
    write_output(data)

scrape()    

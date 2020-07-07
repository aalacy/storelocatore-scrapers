import csv
import re
import requests
import json
import csv
import requests
from bs4 import BeautifulSoup

base_url = 'https://marriott.com/'

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
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    output_list = []
    url = "https://pacsys.marriott.com/data/marriott_properties_LC_en-US.json"
    session = requests.Session()
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36'
    }
    request = session.get(url, headers=headers)
    soup = BeautifulSoup(request.text,"lxml")
    data = (soup.text)
    store_list = json.loads(data)
    data_8 = (store_list['regions'])
    for i in data_8:
        for j in i['region_countries']:
            for k in j['country_states']:
                for h in k['state_cities']:
                    for g in (h['city_properties']):
                        if "USA" in (g['country_name']) or "CA" in (g['country_name']):
                            zipp = (g['postal_code'])
                            location_name = (g['name'])
                            street_address = (g['address'])
                            city = (g['city'])
                            state = (g['state_name'])
                            country_code = (g['country_name'])
                            phone = (g['phone'])
                            latitude = (g['latitude'])
                            longitude = (g['longitude'])
                            key = (g['marsha_code'])
                            page_url = "https://www.marriott.com/hotels/travel/"+str(key)
                            #print(page_url)
                            output = []
                            output.append(base_url) # url
                            output.append(location_name) #location name
                            output.append(street_address) #address
                            output.append(city)#city
                            output.append(state) #state
                            output.append(zipp) #zipcode
                            output.append(country_code) #country code
                            output.append("<MISSING>") #store_number
                            output.append(phone) #phone
                            output.append("<MISSING>") #location type
                            output.append(latitude) #latitude
                            output.append(longitude) #longitude
                            output.append("<MISSING>") 
                            output.append(page_url)#opening hours            
                            yield output
def scrape():
    data = fetch_data()
    write_output(data)
scrape()

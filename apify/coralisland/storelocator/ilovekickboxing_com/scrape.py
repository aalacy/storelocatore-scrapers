import csv
import re
import pdb
import requests
from lxml import etree
import json
import usaddress


base_url = 'https://www.ilovekickboxing.com'


def validate(item):    
    if item == None:
        item = ''
    if type(item) == int or type(item) == float:
        item = str(item)
    if type(item) == list:
        item = ' '.join(item)
    return item.replace('\u2013', '-').strip()

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
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    output_list = []
    history = []
    with open('cities.json') as data_file:    
        city_list = json.load(data_file)  
    url = "https://api.ilovekickboxing.com/api/v1"
    page_url = ''
    session = requests.Session()
    headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Authorization': 'bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImp0aSI6ImM2NjFkOTY4YjAyMTY0ZmQ2NmE1ZjVjZTcwZTQyNjY4NWQzNDczYmNkMjhhNDE2ZWViZTE0MTY0N2U2NDVlMGUxZmFiOWJhNmRjYTM3NjA3In0.eyJhdWQiOiIxIiwianRpIjoiYzY2MWQ5NjhiMDIxNjRmZDY2YTVmNWNlNzBlNDI2Njg1ZDM0NzNiY2QyOGE0MTZlZWJlMTQxNjQ3ZTY0NWUwZTFmYWI5YmE2ZGNhMzc2MDciLCJpYXQiOjE1NTA2MTE5ODUsIm5iZiI6MTU1MDYxMTk4NSwiZXhwIjoxNTgyMTQ3OTg1LCJzdWIiOiIxIiwic2NvcGVzIjpbXX0.PpnxXee7PdBtqXvWqXPHCA65_xH7O2JkwxrNyWoFsOvpq-nxCJkOgjLCd79jcHKQmOy4I_SWw1A65ZTW4kocOoblhoz3EF-tb-wyjPszMKVrhIrlBrenlpuoggYxRNolCtdq0sAisjkhrsIoPnv6J-eLi95VsQ5ZQdrrffcQb93ur45PY2-omgOfUrmsfytC5ab2vFgp11vAONd_s-rxgQ60helB5pTPbpatyiFxaBa6cfUYUqcyT1sEgG0eRVixqXdnmCu7gG8st91hWw0LHODYgyESh50Swc_Y35Bto2fyxzcuPJwSDcaNaQdW2cfCyUPTbVjUEjGMKB8qopTlGZwlKqCadQ8ctzlY5qQShtsiBsxuqxej8KILyGnOD2Q4WvJkz5LdDztl7SpKTEPGrucnVKvo6Vvw3fg9b7omcYnyx8J7iAW-M5UufQKE8ZIgQCYUxsHilsC8OhmMyyRul7zBlLTUkNX-2HR0NSxxfgfcuwwaZwjKdMO6LigqPSREZqo1MekhSR7vkfs3my9eG9fx3tGZ3wswRoX50Fx0h-l2UaekNnvLz0wkJoYNoqIO1l1y1uThioIxJK03g0GspYedizc3G7WadP_2-axFNSDpvqcD8mXOwmZnsUg3Bshbc1Iyq3eiTf805Bewt7Pr0iEfhOTKzJEy0ubT3A03ECM',
        'Content-Type': 'application/json',
        'Sec-Fetch-Mode': 'cors',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',
    }
    for city in city_list:
        payload = {
            'query' : '''query
               {
               zipLocations
                  (
                  lat : "'''+str(city['latitude'])+'''"
                  long : "'''+str(city['longitude'])+'''"
                  amount :100
                  active : true
                  )
                  {ID
                   Name
                   City
                   lat
                   lng
                   Line1
                   ZipCode
                   distance
                   phone
                   state
                      {
                      ID
                      Code
                      }
                   url_slug
                   phone
                  }
               }'''
        }
        request = session.post(url, headers=headers, data=json.dumps(payload))
        source = json.loads(request.text)
        if 'data' in source:
            store_list = source['data']['zipLocations']            
            for store in store_list:
                if get_value(store['ID']) not in history:
                    history.append(get_value(store['ID']))
                    output = []
                    output.append(base_url) # url
                    page_url = base_url + '/' + get_value(store['url_slug'])
                    output.append(page_url) # page url
                    output.append(get_value(store['Name'])) #location name
                    output.append(get_value(store['Line1'])) #address
                    output.append(get_value(store['City'])) #city
                    output.append(get_value(store['state']['Code'])) #state
                    output.append(get_value(store['ZipCode'])) #zipcode
                    zip_len = len(get_value(store['ZipCode']).split(' '))
                    canada = ['SK','AB','BC','ON','QC','PE','YK','NL','NS','PEI']
                    state = get_value(store['state']['Code'])
                    #if zip_len > 1:
                        #output.append('CA') #country code
                    #else:
                        #output.append('US') #country code
                    if state in canada:
                        output.append('CA')
                    else:
                        output.append('US')
                    output.append(get_value(store['ID'])) #store_number
                    output.append(get_value(store['phone'])) #phone
                    output.append('iLoveKickboxing') #location type
                    output.append(get_value(store['lat'])) #latitude
                    output.append(get_value(store['lng'])) #longitude
                    store_hours = []
                    output.append(get_value(store_hours)) #opening hours
                    output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()

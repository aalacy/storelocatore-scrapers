import csv
import re
import pdb
import requests
from lxml import etree
import json


base_url = 'https://www.homehardware.ca'


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
    url = "https://www.homehardware.ca/api/content/documentlists/store-templates-hh-boh@HomeH/views/default/documents?filter=properties.displayOnline%20eq%20true%20and%20properties.storeType%20in[%27Home%20Hardware%27,%27Home%20Building%20Centre%27,%27Home%20Hardware%20Building%20Centre%27]&pageSize=1100"
    session = requests.Session()
    headers = {
        'Accept': 'application/json',
        'Content-type': 'application/json',
        'cookie': '_mzvr=A_DnVvEW10W_IPL03B4AeQ; hhLanguage=en; _mzvs=nn; _mzvt=sRWZAt7ZoECT0XXBbzb3Xg; sb-sf-at-prod-s=pt=&at=MdlFwKGDYJ5HUmhtqfZijQpXXMJE1PX3OKSF4/frTq/yens/zgvYd+MBerjMG0s/oHojEFwBQxechFQ54+Sjpl00pT24ci9wUJt1ULb8GsDK0hQF6n1JvDnFeNMRei77e99/BvDsGGorMSqBK9U8Zs5VdvBaR+vO7b14G4LrtZV//hNSj0Mzew7kn85XY3HJ8Xi7mRA0A25+r92V2TkxB1cRpHndCgyYYELfHzcFIeDq+t4FhlnWWFzj35y2RKnjSrauROkol6GH3LOegevClNmTyoBHkW/yC7xmsZjYwOY0lbXsP5UzCyqMqqoa5igL/aFB2bOxtgS46VwV9dkdpg==&dt=2019-09-02T17:20:12.7247459Z; sb-sf-at-prod=pt=&at=MdlFwKGDYJ5HUmhtqfZijQpXXMJE1PX3OKSF4/frTq/yens/zgvYd+MBerjMG0s/oHojEFwBQxechFQ54+Sjpl00pT24ci9wUJt1ULb8GsDK0hQF6n1JvDnFeNMRei77e99/BvDsGGorMSqBK9U8Zs5VdvBaR+vO7b14G4LrtZV//hNSj0Mzew7kn85XY3HJ8Xi7mRA0A25+r92V2TkxB1cRpHndCgyYYELfHzcFIeDq+t4FhlnWWFzj35y2RKnjSrauROkol6GH3LOegevClNmTyoBHkW/yC7xmsZjYwOY0lbXsP5UzCyqMqqoa5igL/aFB2bOxtgS46VwV9dkdpg==; mozucartcount=%7B%22be9da37b74d642e69f0d75040708a04b%22%3A0%7D; _mzPc=eyJjb3JyZWxhdGlvbklkIjoiMmUyZDBkYzNkNGJhNGI1YjhkM2I4YzlmOTllYmJhM2YiLCJpcEFkZHJlc3MiOiIxMDMuOS4xOTEuMTg5IiwiaXNEZWJ1Z01vZGUiOmZhbHNlLCJpc0NyYXdsZXIiOmZhbHNlLCJpc01vYmlsZSI6ZmFsc2UsImlzVGFibGV0IjpmYWxzZSwiaXNEZXNrdG9wIjp0cnVlLCJ2aXNpdCI6eyJ2aXNpdElkIjoic1JXWkF0N1pvRUNUMFhYQmJ6YjNYZyIsInZpc2l0b3JJZCI6IkFfRG5WdkVXMTBXX0lQTDAzQjRBZVEiLCJpc1RyYWNrZWQiOmZhbHNlLCJpc1VzZXJUcmFja2VkIjpmYWxzZX0sInVzZXIiOnsiaXNBdXRoZW50aWNhdGVkIjpmYWxzZSwidXNlcklkIjoiYmU5ZGEzN2I3NGQ2NDJlNjlmMGQ3NTA0MDcwOGEwNGIiLCJmaXJzdE5hbWUiOiIiLCJsYXN0TmFtZSI6IiIsImVtYWlsIjoiIiwiaXNBbm9ueW1vdXMiOnRydWUsImJlaGF2aW9ycyI6WzEwMTQsMjIyXX0sInVzZXJQcm9maWxlIjp7InVzZXJJZCI6ImJlOWRhMzdiNzRkNjQyZTY5ZjBkNzUwNDA3MDhhMDRiIiwiZmlyc3ROYW1lIjoiIiwibGFzdE5hbWUiOiIiLCJlbWFpbEFkZHJlc3MiOiIiLCJ1c2VyTmFtZSI6IiJ9LCJpc0VkaXRNb2RlIjpmYWxzZSwiaXNBZG1pbk1vZGUiOmZhbHNlLCJub3ciOiIyMDE5LTA5LTAyVDE3OjQxOjIzLjU0NjkxOTRaIiwiY3Jhd2xlckluZm8iOnsiaXNDcmF3bGVyIjpmYWxzZSwiY2Fub25pY2FsVXJsIjoiL3N0b3JlLWxvY2F0b3IifSwiY3VycmVuY3lSYXRlSW5mbyI6e319',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36',
    }
    request = session.get(url, headers=headers)
    store_list = json.loads(request.text)['items']
    for store in store_list:        
        output = []
        store = store['properties']
        output.append(base_url) # url
        output.append(get_value(store['storeName'])) #location name
        output.append(get_value(store['address1'] + ' ' + store['address2']).replace('N/A', '').strip()) #address
        output.append(get_value(store['city'])) #city
        output.append(get_value(store['province'])) #state
        output.append(get_value(store['postalCode'])) #zipcode
        output.append('CA') #country code
        output.append(get_value(store['documentKey'])) #store_number
        output.append(get_value(store['phone'])) #phone
        output.append(get_value(store['storeType'])) #location type
        output.append(get_value(store['latitude'])) #latitude
        output.append(get_value(store['longitude'])) #longitude
        day_of_week = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        store_hours = []
        for day in day_of_week:
            if day+'Hours' in store:
                store_hours.append(validate(day + ' ' + store[day+'Hours']))
        output.append(', '.join(store_hours)) #opening hours
        output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()

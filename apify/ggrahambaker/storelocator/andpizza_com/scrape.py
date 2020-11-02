import csv
from sgrequests import SgRequests
import json

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    locator_domain = 'https://andpizza.com/' 
    ext = 'https://api.andpizza.com/webapi/v100/shops'
    session = SgRequests()

    HEADERS = {'Host': 'api.andpizza.com',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
    'Referer': 'https://order.andpizza.com/',
    'Api-Token': 'SrM8gqYvLYOowhu0deSheJxCuWBX',
    'X-Client': 'NextGenOnline',
    'X-Referrer': 'https://order.andpizza.com/#/locations',
    'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJLeUZXTW9nUm5EN1BCbTU4MTU4MTA0NDM0OCIsImF1ZCI6Imd1ZXN0dXNlciIsImNsaWVudCI6Ik5leHRHZW5PbmxpbmUiLCJpc3MiOiJodHRwczovL2FwaS5hbmRwaXp6YS5jb20vd2ViYXBpL3YxMDAvdXNlci9ndWVzdC10b2tlbiIsImlhdCI6MTU4MTA0NDM0OCwiZXhwIjoxODk2NDA0MzQ4LCJuYmYiOjE1ODEwNDQzNDgsImp0aSI6IlEzdnpKSzBWVFFIZXZ0NHgifQ.6opbg1ZfFaCmkXjTbzYvoSMDZwztA0ulQIxYnVS4E4Q',
    'Origin': 'https://order.andpizza.com',
    'DNT': '1',
    'Connection': 'keep-alive',
    'Cache-Control': 'max-age=0',
    'TE': 'Trailers'}

    r = session.get(ext, headers = HEADERS)
    
    loc_data = json.loads(r.content)
    all_store_data = []
    for loc in loc_data['data']:    
        location_name = loc['name']
        addy = loc['location']
        street_address = addy['address1']
        if addy['address2'] != None:
            street_address += ' ' + addy['address2']
            
        city = addy['city']
        state = addy['state']
        zip_code = addy['zipcode']
        phone_number = addy['phone']
        
        lat = addy['latitude']
        longit = addy['longitude']
        hours = ''
        
        for day in loc['service_schedule']['general']:
            hours += day['label'] + ' ' + day['value'] + ' '
            
        country_code = 'US'
        page_url = '<MISSING>'
        store_number = loc['id']
        location_type = '<MISSING>'
        
        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code, 
                    store_number, phone_number, location_type, lat, longit, hours, page_url]
        all_store_data.append(store_data)

    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()

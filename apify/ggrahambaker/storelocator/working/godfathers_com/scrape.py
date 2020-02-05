import csv
from sgrequests import SgRequests
import json
session = SgRequests()


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def hours_ingest(loc_type):
    hours_json = loc_type

    mon = 'Monday ' + hours_json['monday']['openTime']['timeString'].split(',')[0]
    mon += ' - ' + hours_json['monday']['closeTime']['timeString'].split(',')[0]

    tues = 'Tuesday ' + hours_json['tuesday']['openTime']['timeString'].split(',')[0]
    tues += ' - ' + hours_json['tuesday']['closeTime']['timeString'].split(',')[0]

    wed = 'Wednesday ' + hours_json['wednesday']['openTime']['timeString'].split(',')[0]
    wed += ' - ' + hours_json['wednesday']['closeTime']['timeString'].split(',')[0]


    thur = 'Thursday ' + hours_json['thursday']['openTime']['timeString'].split(',')[0]
    thur += ' - ' + hours_json['thursday']['closeTime']['timeString'].split(',')[0]


    fri = 'Friday ' + hours_json['friday']['openTime']['timeString'].split(',')[0]
    fri += ' - ' + hours_json['friday']['closeTime']['timeString'].split(',')[0]


    sat = 'Saturday ' + hours_json['saturday']['openTime']['timeString'].split(',')[0]
    sat += ' - ' + hours_json['saturday']['closeTime']['timeString'].split(',')[0]


    sun = 'Sunday ' + hours_json['sunday']['openTime']['timeString'].split(',')[0]
    sun += ' - ' + hours_json['sunday']['closeTime']['timeString'].split(',')[0]



    hours = mon + ' ' + tues + ' ' + wed + ' ' + thur + ' ' + fri + ' ' + sat + ' ' + sun     

    return hours

def fetch_data():
    # Your scraper here
    HEADERS = { 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36' }

    locator_domain = 'https://godfathers.com/' 

    session = SgRequests()

    url = 'https://api-prod-gfp-us-a.tillster.com/mobilem8-web-service/rest/storeinfo/distance?_=1580869219683&disposition=DINE_IN&latitude=39.75&longitude=-104.99000000000001&maxResults=1000&radius=6000&statuses=ACTIVE,TEMP-INACTIVE,ORDERING-DISABLED&tenant=gfp-us'

    r = session.get(url, headers = HEADERS)


    all_stores = json.loads(r.content)['getStoresResult']['stores']
    all_store_data = []

    for store in all_stores:
        
        if store['status'] == 'TEMP-INACTIVE':
            continue
        
        location_name = store['storeName']
        street_address = store['street']
        state = store['state']
        city = store['city']
        zip_code = store['zipCode']
        
        country_code = store['country']
       
            
        
        store_number = store['storeName'].replace('GFP-', '').strip()
        
        lat = store['latitude']
        longit = store['longitude']
        
        phone_number = store['phoneNumber']

        
        hours = ''
        location_type = ''
        dine_in = -1
        pick_up = -1
        delvery = -1


        if 'storeHours' not in store:
            hours = '<MISSING>'
        else:
            for i, loc_type in enumerate(store['storeHours']):
                location_type += loc_type['disposition'].replace('_', ' ') + ' '

                if 'DINE_IN' in loc_type['disposition']:
                    ## hours
                    dine_in = i
                if 'PICKUP' in loc_type['disposition']:
                    pick_up = i
                
                if 'DELIVERY' in loc_type['disposition']:
                    delvery = i
                    

                
   
        if dine_in != -1:
            hours = hours_ingest(store['storeHours'][dine_in])
        elif pick_up != -1:
            hours = hours_ingest(store['storeHours'][pick_up])
        elif delvery != -1:
            hours = hours_ingest(store['storeHours'][delvery])
        else:
            hours = '<MISSING>'
            location_type = '<MISSING>'


                
        if hours == '':
            print(store)
            print()
            print()
            print()
            print()
            print()
            
        location_type = location_type.strip()
        hours = hours.strip()
        
    
        page_url = '<MISSING>'
        
        
        
        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code, 
                    store_number, phone_number, location_type, lat, longit, hours, page_url]

        all_store_data.append(store_data)

        
        





    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()

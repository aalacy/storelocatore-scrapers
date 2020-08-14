import csv
from sgrequests import SgRequests
import sgzip 

session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def parse_hours(store):
    days = ['mon', 'tues', 'wed', 'thurs', 'fri', 'sat', 'sun']
    hours = []
    for day in days:
        start = store['{}Open'.format(day)]
        end = store['{}Close'.format(day)]
        hours.append('{}: {}-{}'.format(day, start, end))
    return ', '.join(hours)

def fetch_data():    
    headers ={
        'authority': 'www.crateandbarrel.com',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'content-type': 'application/x-www-form-urlencoded',
        'origin': 'https://www.crateandbarrel.com',
        'referer': 'https://www.crateandbarrel.com/stores/list-state/retail-stores',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36',     
    }
    base_url = "https://www.crateandbarrel.com/"
    search = sgzip.ClosestNSearch()
    search.initialize(country_codes = ['us', 'ca'])
    keys = set()
    zip_code = search.next_zip()
    while zip_code:
        response = session.post("https://www.crateandbarrel.com/stores/locator", headers=headers, data="SearchKeyword={}&hdnHostUrl=https%3A%2F%2Fwww.crateandbarrel.com".format(zip_code)).json()
        stores = response['storeList']
        result_coords = []
        for i in stores:
            location_name = i['storeName']
            store_number = i['storeNumber']
            if store_number in keys:
                continue
            else:
                keys.add(store_number)
            street_address = i['address1']+" "+i['address2']
            city = i['city']
            state = i['state']
            zipp = i['zip']
            if 'USA' not in i['country']:
                continue
            country_code = i['country'].replace("USA","US").replace("CAN","CA")
            phone = "("+i['phoneAreaCode']+")"+" "+i['phonePrefix']+"-"+i['phoneSuffix']
            location_type = 'Store'
            if i['distributionCenter']:
                location_type = 'Distribution Center'
            elif i['outlet']:
                location_type = 'Outlet'
            elif i['corporate']:
                location_type = 'Corporate'
            if location_type not in ['Store', 'Outlet']:
                continue
            latitude = i['storeLat']
            longitude = i['storeLong']
            result_coords.append((latitude, longitude))
            page_url = "https://www.crateandbarrel.com/stores/"+str(location_name.lower().replace(',','').replace(' ','-'))+"/str"+str(store_number)
            hours = parse_hours(i)
            store = []
            store.append(base_url)
            store.append(location_name if location_name else "<MISSING>")
            store.append(street_address if street_address else "<MISSING>")
            store.append(city if city else "<MISSING>")
            store.append(state if state else "<MISSING>")
            store.append(zipp if zipp else "<MISSING>")
            store.append(country_code if country_code else "<MISSING>")
            store.append(store_number if store_number else "<MISSING>")
            store.append(phone if phone else "<MISSING>")
            store.append(location_type if location_type else "<MISSING>")
            store.append(latitude if latitude else "<MISSING>")
            store.append(longitude if longitude else "<MISSING>")
            store.append(hours if hours else "<MISSING>")
            store.append(page_url.replace("-/","/").replace("---","-") if page_url else "<MISSING>")
            yield store
        if len(result_coords) > 0:
            search.max_count_update(result_coords)
        else:
            search.max_distance_update(100)
        zip_code = search.next_zip()

def scrape():
    data = fetch_data()
    write_output(data)

scrape()

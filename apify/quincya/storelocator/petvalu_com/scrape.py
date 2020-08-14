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
    hrs = store['op']
    days = ['mon', 'tues', 'wed', 'thurs', 'fri', 'sat', 'sun']
    hours = []
    for dayidx in range(len(days)):
        day = days[dayidx]
        start = hrs[str(dayidx*2)] 
        end = hrs[str(dayidx*2 + 1)] 
        hours.append('{}: {}-{}'.format(day, start, end))
    return ', '.join(hours)

def fetch_data():    
    headers ={
        'authority': 'store.petvalu.com',
        'accept': 'application/json, text/javascript, */*; q=0.01',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'origin': 'https://store.petvalu.com',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36',     
    }
    base_url = "petvalu.com"
    keys = set()
    for ctry in ['us', 'ca']:
        search = sgzip.ClosestNSearch()
        search.initialize(country_codes = [ctry])
        coord = search.next_coord()
        while coord:
            lat, lng = coord[0], coord[1]
            stores = session.post("https://store.petvalu.com/{}/wp-admin/admin-ajax.php".format(ctry), headers=headers, data="action=get_stores&lat={}&lng={}&radius=100&store=&states=&cities=&adds=&zip=".format(lat, lng)).json().values()
            result_coords = []
            for store in stores:
                location_name = store['na']
                store_number = store['ID']
                if store_number in keys:
                    continue
                else:
                    keys.add(store_number)
                street_address = store['st']
                if '<' in street_address:
                    street_address = street_address.split('<')[0].strip()
                city = store['ct'].strip()
                state = store['rg'].strip()
                zipp = store['zp'].strip()
                country_code = store['co'].strip()
                if country_code.lower() not in ['us', 'ca']:
                    continue
                phone = store['te'] if 'te' in store else '<MISSING>' 
                location_type = '<MISSING>'
                latitude = store['lat']
                longitude = store['lng']
                result_coords.append((latitude, longitude))
                page_url = store['gu']
                hours = parse_hours(store)
                res = [base_url]
                res.append(location_name if location_name else "<MISSING>")
                res.append(street_address if street_address else "<MISSING>")
                res.append(city if city else "<MISSING>")
                res.append(state if state else "<MISSING>")
                res.append(zipp if zipp else "<MISSING>")
                res.append(country_code if country_code else "<MISSING>")
                res.append(store_number if store_number else "<MISSING>")
                res.append(phone if phone else "<MISSING>")
                res.append(location_type if location_type else "<MISSING>")
                res.append(latitude if latitude else "<MISSING>")
                res.append(longitude if longitude else "<MISSING>")
                res.append(hours if hours else "<MISSING>")
                res.append(page_url.replace("-/","/").replace("---","-") if page_url else "<MISSING>")
                yield res
            if len(result_coords) > 0:
                search.max_count_update(result_coords)
            else:
                search.max_distance_update(100)
            coord = search.next_coord()

def scrape():
    data = fetch_data()
    write_output(data)

scrape()

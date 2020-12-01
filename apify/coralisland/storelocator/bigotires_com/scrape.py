import csv
from sgrequests import SgRequests
import sgzip
from sgzip import SearchableCountries


base_url = 'https://www.bigotires.com'

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

def fetch_data():
    output_list = []
    store_ids = []

    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36'
    HEADERS = {'User-Agent' : user_agent}

    session = SgRequests()
    url = "https://www.bigotires.com/restApi/dp/v1/store/storesByAddress"

    zips = sgzip.for_radius(radius=200, country_code=SearchableCountries.USA)
    for zip in zips:
        # query the store locator using zip

        data = {
            "address": zip,
            "distanceInMiles": "200"
        }

        source = session.post(url, json=data).json()

        if 'storesType' not in list(source.keys()):
            continue

        store_list = source['storesType']

        if 'stores' not in list(store_list.keys()):
            continue

        store_list = store_list['stores']
        for store in store_list:
            store_id = validate(store['storeId'])
            if store_id in store_ids:
                continue
            store_ids.append(store_id)
            store_hours = store['workingHours']
            hours = ""
            for x in store_hours:
                if validate(x['openingHour']) == 'Closed ':
                    hours += x['day'] + ' ' + x['openingHour'] + ' '
                else:
                    hours += x['day'] + ' ' + x['openingHour'] + '-' + x['closingHour'] + ' '
            storeClosedHours = store['storeClosedHours']
            for x in storeClosedHours:
                hours += validate(x['date'] + ': ' + x['workingHours'] + ' ')
            hours = hours.replace("Closed-Closed","Closed").strip()
            output = []
            output.append(base_url) # url
            output.append(base_url + store['storeDetailsUrl'])
            output.append(validate(store['address']['address1'])) #location name
            output.append(validate(store['address']['address1'])) #address
            output.append(validate(store['address']['city'])) #city
            output.append(validate(store['address']['state'])) #state
            output.append(validate(store['address']['zipcode'])) #zipcode
            output.append("US") #country code
            output.append(store_id) #store_number
            output.append(validate(store['phoneNumbers'][0])) #phone
            output.append("<MISSING>") #location type
            output.append(store['mapCenter']['latitude']) #latitude
            output.append(store['mapCenter']['longitude']) #longitude
            output.append(get_value(hours)) #opening hours
            output_list.append(output)

    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()

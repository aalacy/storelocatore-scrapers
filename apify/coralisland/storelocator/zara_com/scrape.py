import csv
import re
from sgrequests import SgRequests
import json
import usaddress
import sgzip
from sgzip import DynamicGeoSearch, SearchableCountries

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


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

def fetch_data():
    output_list = []
    history = []

    session = SgRequests()
    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36'
    headers = {'User-Agent' : user_agent}

    search = sgzip.DynamicGeoSearch(country_codes=[SearchableCountries.USA, SearchableCountries.CANADA])

    search.initialize()

    coord = search.next()

    while coord:
        x = coord[0]
        y = coord[1]

        url = "https://www.zara.com/us/en/stores-locator/search?lat="+str(x)+"&lng="+str(y)+"&isGlobalSearch=true&showOnlyPickup=false&isDonationOnly=false&ajax=true"
        
        result_coords = []
        result_coords.append([x, y])
    
        request = session.get(url, headers=headers)
        store_list = json.loads(request.text)
        for store in store_list:
            store_id = validate(store.get('id'))
            if store_id not in history:
                history.append(store_id)
                output = []
                output.append("zara.com") # url
                output.append("<MISSING>") # page url
                output.append(get_value(store.get('name'))) #location name
                output.append(get_value(store.get('addressLines'))) #address
                output.append(get_value(store.get('city'))) #city
                output.append(get_value(store.get('state'))) #state
                output.append(get_value(store.get('zipCode'))) #zipcode
                country = get_value(store.get('countryCode'))
                if country not in ["US","CA"]:
                    continue
                output.append(country) #country code
                output.append(get_value(store_id)) #store_number
                output.append(get_value(store.get('phones')).replace('+', '')) #phone
                output.append("<MISSING>") #location type

                lat = get_value(store.get('latitude'))
                longit = get_value(store.get('longitude'))
                output.append(lat) #latitude
                output.append(longit) #longitude

                result_coords.append([lat, longit])
                search.update_with(result_coords)

                days_of_week = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
                store_hours = []
                if len(store.get(('openingHours'))) > 0:
                    for hour in store.get('openingHours'):
                        if hour['openingHoursInterval']:
                            store_hours.append(days_of_week[hour['weekDay']-1] + ' ' + hour['openingHoursInterval'][0]['openTime'] + '-' + hour['openingHoursInterval'][0]['closeTime'])    
                        else:
                            store_hours.append(days_of_week[hour['weekDay']-1] + ' closed')

                output.append(get_value(store_hours)) #opening hours
                output_list.append(output)
            
        if len(store_list) == 0:
            search.update_with(result_coords)
        coord = search.next()

    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()

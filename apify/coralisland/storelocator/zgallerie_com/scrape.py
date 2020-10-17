import csv
from sgrequests import SgRequests

base_url = 'https://www.zgallerie.com'

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():

    session = SgRequests()

    output_list = []
    url = "https://prod-parky.zgallerie.com/sf/stores/?zipcode=78256&distance=10000"
    
    headers = {
        'authority': 'prod-parky.zgallerie.com',
        'method': 'GET',
        'path': '/sf/stores/?zipcode=70810&distance=100',
        'scheme': 'https',
        'accept': '*/*',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9',
        'origin': 'https://www.zgallerie.com',
        'referer': 'https://www.zgallerie.com/t-store-locations',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36'
    }

    store_list = session.get(url, headers=headers).json()

    locs = []
    for state_row in store_list:
        cities = store_list[state_row]
        for city_row in cities:
            locs.append(cities[city_row])

    for info in locs:
        info = info[0]
        hours = "Mon - Thurs " + info['hrs_mon_thur'] + " Fri " + info['hrs_fri'] + " Sat " + info['hrs_sat'] + " Sun " + info['hrs_sun']
        if info['store_info']:
            hours = hours + ". " + info['store_info']
        output = []
        output.append(base_url) # url
        output.append("https://www.zgallerie.com/t-store-locations")
        output.append(info['name']) #location name
        output.append(info['street'].strip()) #address
        output.append(info['city']) #city
        output.append(info['state']) #state
        output.append(info['zip']) #zipcode
        output.append('US') #country code
        output.append(info['number']) #store_number
        output.append(info['phone']) #phone
        output.append('<MISSING>') #location type
        output.append(info['lat']) #latitude
        output.append(info['lng']) #longitude
        output.append(hours) #opening hours
        output_list.append(output)

    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()

import csv
from sgrequests import SgRequests
import json

session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def hours_maker(obj):
    day_dict = {'1': 'Monday', '2': 'Tuesday', '3': 'Wednesday', '4': 'Thursday', '5': 'Friday', '6': 'Saturday', '7': 'Friday'}
    hours = ''
    for key in obj:
        hours += day_dict[key] + ' ' + str(int(obj[key]['from'][0]) % 12) + 'am - ' +  str(int(obj[key]['to'][0]) % 12) + 'pm '
    return hours

def fetch_data():
    locator_domain_json = 'https://www.pharmaca.com/amlocator/index/ajax/'

    an_obj = session.get(locator_domain_json)
    # driver = get_driver()
    # driver.get(locator_domain + ext)
    json_ob = json.loads(an_obj.content)

    all_store_data = []
    for obj in json_ob['items']:
        store_number = '<MISSING>'
        location_name = obj['name']
        country_code = obj['country']
        city = obj['city']
        zip_code = obj['zip']
        if 'Santa' in zip_code:
            zip_code = '<MISSING>'
        state = obj['state']
        street_address = obj['address']
        lat = obj['lat']
        longit = obj['lng']
        phone_number = obj['phone']
        location_type = '<MISSING>'
        to_make = json.loads(obj['schedule'])
        hours = hours_maker(to_make)
        locator_domain = 'https://www.pharmaca.com/'

        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                      store_number, phone_number, location_type, lat, longit, hours]
        all_store_data.append(store_data)
        
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()

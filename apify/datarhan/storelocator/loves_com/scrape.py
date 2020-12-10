import csv
import json
import usaddress
from lxml import etree

from sgrequests import SgRequests

DOMAIN = 'loves.com'


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    # Your scraper here
    session = SgRequests()

    items = []
    
    allpoints_response = session.get('https://www.loves.com/api/sitecore/StoreSearch/SearchStores')
    all_data = json.loads(allpoints_response.text)
    
    for point_data in all_data[0]['Points']:
        store_url = point_data['StoreUrl']
        location_name = point_data['Name']
        location_name = location_name if location_name else '<MISSING>'
        street_address = point_data['Address1']
        if point_data['Address2']:
            street_address += ' ' + point_data['Address2']
        street_address = street_address if street_address else '<MISSING>'
        city = point_data['City']
        city = city if city else '<MISSING>'
        state = point_data['State']
        state = state if state else '<MISSING>'
        zip_code = point_data['Zip']
        zip_code = zip_code if zip_code else '<MISSING>'
        country_code = point_data['County']
        country_code = country_code if country_code else '<MISSING>'
        store_number = point_data['FacilityId']
        phone = point_data['PhoneNumber']
        phone = phone if phone else '<MISSING>'
        location_type = point_data['Name'].split()[0]
        latitude = point_data['Latitude']
        latitude = latitude if latitude else '<MISSING>'
        longitude = point_data['Longitude']
        longitude = longitude if longitude else '<MISSING>'
        hours_of_operation = '<MISSING>'
        
        item = [
            DOMAIN,
            store_url,
            location_name,
            street_address,
            city,
            state,
            zip_code,
            country_code,
            store_number,
            phone,
            location_type,
            latitude,
            longitude,
            hours_of_operation
        ]

        items.append(item)
        
    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()

import csv
from sgrequests import SgRequests
import xml.etree.ElementTree as ET
import usaddress

session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    locator_domain = 'https://yumyumdonuts.com/'
    dest = 'https://yumyumdonuts.com/maps_xml'
    page = session.get(dest)
    assert page.status_code == 200

    tree = ET.fromstring(page.content)

    # get root element
    all_store_data = []
    switch = False
    for child in tree:
        store_number = child.attrib['uuid']
        addy = child.attrib['Address']

        parsed_add = usaddress.tag(addy)[0]

        street_address = ''

        if 'AddressNumber' in parsed_add:
            street_address += parsed_add['AddressNumber'] + ' '
        if 'StreetNamePreDirectional' in parsed_add:
            street_address += parsed_add['StreetNamePreDirectional'] + ' '
        if 'StreetName' in parsed_add:
            street_address += parsed_add['StreetName'] + ' '
        if 'StreetNamePostType' in parsed_add:
            street_address += parsed_add['StreetNamePostType'] + ' '
        if 'OccupancyType' in parsed_add:
            street_address += parsed_add['OccupancyType'] + ' '
        if 'OccupancyIdentifier' in parsed_add:
            street_address += parsed_add['OccupancyIdentifier'] + ' '
        city = parsed_add['PlaceName']
        state = parsed_add['StateName']
        zip_code = parsed_add['ZipCode']

        hours = child.attrib['Desc']
        phone_number = child.attrib['Phone']
        lat = child.attrib['Xcoord']
        longit = child.attrib['Ycoord']

        country_code = 'US'
        location_name = '<MISSING>'
        location_type = '<MISSING>'
        if '5833 Kanan Rd' in street_address:
            if not switch:
                switch = True
            else:
                continue

        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                      store_number, phone_number, location_type, lat, longit, hours]
        all_store_data.append(store_data)

    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()

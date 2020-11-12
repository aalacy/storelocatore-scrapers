import csv
from lxml import etree
from w3lib.url import add_or_replace_parameter

from sgrequests import SgRequests

DOMAIN = 'americasbest.com'


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
    gathered_poi = []
    
    states = [
        "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DC", "DE", "FL", "GA", 
        "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", 
        "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", 
        "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", 
        "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"
    ]

    for state_code in states:
        url = 'https://maps.americasbest.com/ajax?'
        parameter = '<request><appkey>112FD85A-20C7-11E9-9FDF-56218E89CD5A</appkey><formdata id="locatorsearch"><dataview>store_default</dataview><limit>25000</limit><geolocs><geoloc><addressline>{}</addressline><longitude></longitude><latitude></latitude></geoloc></geolocs><searchradius>50|100|250|500|750</searchradius><where><and><entityid><eq>9</eq></entityid><showinlocatoryn><eq>Y</eq></showinlocatoryn></and></where></formdata></request>'
        url = add_or_replace_parameter(url, 'xml_request', parameter.format(state_code))
        response = session.get(url)
        dom = etree.XML(response.text.replace('<?xml version="1.0" encoding="UTF-8"?>', ''))
        root = etree.fromstring(etree.tostring(dom))

        for point_data in root.findall('.//poi'):
            if point_data.find('comingsoon').text == 'Y':
                continue
            store_url = point_data.find('storepageurl').text
            location_name = point_data.find('name').text
            location_name = location_name if location_name else '<MISSING>'
            street_address = point_data.find('address1').text
            if point_data.find('address2').text:
                street_address += ', ' + point_data.find('address2').text
            street_address = street_address if street_address else '<MISSING>'
            city = point_data.find('city').text
            city = city if city else '<MISSING>'
            state = point_data.find('state').text
            state = state if state else '<MISSING>'
            zip_code = point_data.find('postalcode').text
            zip_code = zip_code if zip_code else '<MISSING>'
            country_code = point_data.find('country').text
            country_code = country_code if country_code else '<MISSING>'
            store_number = point_data.find('clientkey').text
            phone = point_data.find('phone').text
            phone = phone if phone else '<MISSING>'
            location_type = '<MISSING>'
            latitude = point_data.find('latitude').text
            latitude = latitude if latitude else '<MISSING>'
            longitude = point_data.find('longitude').text
            longitude = longitude if longitude else '<MISSING>'
    
            open_hours = []
            close_hours = []
            for elem in point_data:
                if 'open' in etree.tostring(elem).decode("utf-8"):
                    if elem.tag not in ['openline', 'openyn', 'reopen_date', 'opendate']:
                        open_hours.append('{} {}'.format(elem.tag, elem.text))
            for elem in point_data:
                if 'close' in etree.tostring(elem).decode("utf-8"):
                    if elem.tag not in ['closeline', 'closeyn', 'temp_closed']:
                        close_hours.append('{} {}'.format(elem.tag, elem.text))
            hours_of_operation = ', '.join(list(map(lambda o, c: o+ ' ' +c, open_hours, close_hours)))

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
            
            if store_number not in gathered_poi:
                gathered_poi.append(store_number)
                items.append(item)

        
    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()

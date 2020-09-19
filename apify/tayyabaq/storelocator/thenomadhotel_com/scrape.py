import csv
import re, time
from sgrequests import SgRequests
from lxml import etree

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain", "page_url","location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            if row:
                writer.writerow(row)

def fetch_data():
    session = SgRequests()
    response = etree.HTML(session.get('https://www.thenomadhotel.com').text)
    urls = response.xpath("//div[contains(@class, 'nav-bar')]/nav/a/@href")
    contact_response = etree.HTML(session.get('https://www.thenomadhotel.com/contact/').text)
    locations = contact_response.xpath('//div[@id="all"]//section[@class="contact-info"]')
    for i in range(len(locations)):
        location = locations[i]
        name = location.xpath(".//h2/text()")[0].strip()
        print(name)
        phone = location.xpath(".//p/a[contains(@href, 'tel:')]/@href")[0].strip().split("tel:")[1]
        street_1 = location.xpath(".//address//a/text()")
        street_2 = location.xpath(".//div//a/text()")
        street = street_1[0].strip() if street_1 else street_2[0].strip()
        csz_1 = location.xpath(".//address/text()")
        csz_2 = location.xpath(".//div/p/text()")
        if '+44' in phone:
            csz = csz_1[0].strip()
            city = csz.split(',')[0].strip()
            state = '<MISSING>' 
            zipcode = csz.split(',')[1].strip()
            country = 'GB'
        else:
            csz = csz_1[0].strip() if csz_1 else csz_2[0].strip()
            city = csz.split(',')[0].strip()
            state = csz.split(',')[1].strip().split(' ', 1)[0].strip()
            zipcode = csz.split(',')[1].strip().split(' ', 1)[1].strip()
            country = 'US'
        yield [
            'https://www.thenomadhotel.com',
            urls[i],
            name,
            street,
            city,
            state,
            zipcode,
            country,
            '<MISSING>',
            phone,
            '<MISSING>',
            '<MISSING>',
            '<MISSING>',
            '<MISSING>'
        ]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()

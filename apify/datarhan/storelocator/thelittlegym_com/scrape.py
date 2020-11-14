import csv
from lxml import etree

from sgrequests import SgRequests

DOMAIN = 'thelittlegym.com'


def write_output(data):
    with open('data.csv', mode='w', encoding='utf-8') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    # Your scraper here
    items = []
    
    session = SgRequests()
    response = session.get('https://www.thelittlegym.com/find-a-gym/')
    dom = etree.HTML(response.text)
    all_urls = []
    allstates_codes = dom.xpath('//select[@id="ddlStates"]/option/@value')
    for state_code in allstates_codes:
        full_state_url = 'https://www.thelittlegym.com/find-a-gym?geoaction=3&param={}'.format(state_code)
        all_urls.append(full_state_url)
    canada_provinces = dom.xpath('//select[@id="ddlProv"]/option/@value')
    for province in canada_provinces:
        full_province_url = 'https://www.thelittlegym.com/find-a-gym?geoaction=4&param={}'.format(province)
        all_urls.append(full_province_url)
        
    for url in all_urls:
        state_response = session.get(url)
        state_dom = etree.HTML(state_response.text)
        all_locations_data = state_dom.xpath('//div[@id="find-a-gym"]//section[@class="location-listing"]')
        for location_data in all_locations_data:
            location_url = location_data.xpath('.//a[contains(text(), "Visit our local site")]/@href')
            store_url = '<MISSING>'
            if location_url:
                store_url = 'https://www.thelittlegym.com' + location_url[0]
            location_name = location_data.xpath('.//h3/text()')[0]
            location_name = location_name if location_name else '<MISSING>'
            street_address = location_data.xpath('.//span[@class="street-address"]/text()')[0].strip()
            if 'soon' in street_address.lower():
                continue
            street_address = street_address if street_address else '<MISSING>'
            state_data = location_data.xpath('.//span[@class="region"]/text()')[0].strip()
            state_data = ' '.join([elem.strip() for elem in state_data.split()])
            city = state_data.split(',')[0]
            city = city if city else '<MISSING>'
            state = state_data.split(',')[-1].split()[0]
            state = state if state else '<MISSING>'
            zip_code = state_data.split(',')[-1].split()[1:]
            zip_code = ' '.join(zip_code) if zip_code else '<MISSING>'
            country_code = '<MISSING>'
            store_number = '<MISSING>'
            phone = location_data.xpath('.//p[@class="tel"]/text()')
            phone = phone[0] if phone else '<MISSING>'
            location_type = '<MISSING>'
            location_type = location_type if location_type else '<MISSING>'
            coordinates = location_data.xpath('.//a[contains(@href, "google.com/maps")]/@href')[0].split('@')[-1]
            latitude = coordinates.split(',')[0]
            latitude = latitude if latitude else '<MISSING>'
            longitude = coordinates.split(',')[-1]
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

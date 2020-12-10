import re
import csv
import json
import zipcodes
import urllib.parse
from lxml import etree

from sgrequests import SgRequests


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
    session = SgRequests()

    items = []
    scraped_items = []

    DOMAIN = 'armstrongmccall.com'

    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Content-Type': 'application/x-www-form-urlencoded',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.193 Safari/537.36'
    }

    us_state_abbrev = {
        'Alabama': 'AL',
        'Alaska': 'AK',
        'American Samoa': 'AS',
        'Arizona': 'AZ',
        'Arkansas': 'AR',
        'California': 'CA',
        'Colorado': 'CO',
        'Connecticut': 'CT',
        'Delaware': 'DE',
        'District of Columbia': 'DC',
        'Florida': 'FL',
        'Georgia': 'GA',
        'Guam': 'GU',
        'Hawaii': 'HI',
        'Idaho': 'ID',
        'Illinois': 'IL',
        'Indiana': 'IN',
        'Iowa': 'IA',
        'Kansas': 'KS',
        'Kentucky': 'KY',
        'Louisiana': 'LA',
        'Maine': 'ME',
        'Maryland': 'MD',
        'Massachusetts': 'MA',
        'Michigan': 'MI',
        'Minnesota': 'MN',
        'Mississippi': 'MS',
        'Missouri': 'MO',
        'Montana': 'MT',
        'Nebraska': 'NE',
        'Nevada': 'NV',
        'New Hampshire': 'NH',
        'New Jersey': 'NJ',
        'New Mexico': 'NM',
        'New York': 'NY',
        'North Carolina': 'NC',
        'North Dakota': 'ND',
        'Northern Mariana Islands': 'MP',
        'Ohio': 'OH',
        'Oklahoma': 'OK',
        'Oregon': 'OR',
        'Pennsylvania': 'PA',
        'Puerto Rico': 'PR',
        'Rhode Island': 'RI',
        'South Carolina': 'SC',
        'South Dakota': 'SD',
        'Tennessee': 'TN',
        'Texas': 'TX',
        'Utah': 'UT',
        'Vermont': 'VT',
        'Virgin Islands': 'VI',
        'Virginia': 'VA',
        'Washington': 'WA',
        'West Virginia': 'WV',
        'Wisconsin': 'WI',
        'Wyoming': 'WY'
    }

    start_url = 'https://stores.armstrongmccall.com/'
    response = session.get(start_url)
    dom = etree.HTML(response.text)
    
    view_state = dom.xpath('//input[@id="__VIEWSTATE"]/@value')[0]
    state_generator = dom.xpath('//input[@id="__VIEWSTATEGENERATOR"]/@value')[0]
    event_validation = dom.xpath('//input[@id="__EVENTVALIDATION"]/@value')[0]

    states_html = dom.xpath('//select[@id="ctl00_MainContent_ddlState"]/option')[1:]
    for state_html in states_html:
        if not us_state_abbrev.get(state_html.xpath('text()')[0]):
            continue
        state_code = us_state_abbrev[state_html.xpath('text()')[0]]
        all_codes = zipcodes.filter_by(state="{}".format(state_code))[::10]
        for zip_code in all_codes:
            formdata = {
                '__EVENTTARGET': '',
                '__EVENTARGUMENT': '',
                '__LASTFOCUS': '',
                '__VIEWSTATE': view_state,
                '__VIEWSTATEGENERATOR': state_generator,
                '__EVENTVALIDATION': event_validation,
                'ctl00$MainContent$hdnLat': '',
                'ctl00$MainContent$hdnLon': '',
                'ctl00$MainContent$hdnAddress': '',
                'ctl00$MainContent$hdnTitle': '',
                'ctl00$MainContent$hdnPhone': '',
                'ctl00$MainContent$ddlCountry': 'US',
                'ctl00$MainContent$ddlState': state_html.xpath('@value')[0],
                'ctl00$MainContent$txtAddress': '',
                'ctl00$MainContent$txtCity': '',
                'ctl00$MainContent$txtZip': zip_code['zip_code'],
                'ctl00$MainContent$ddlDist': '200',
                'ctl00$MainContent$btnFind': 'Find it'
            }
            
            code_response = session.post(start_url, data=formdata, headers=headers)
            code_dom = etree.HTML(code_response.text)

            view_state = code_dom.xpath('//input[@id="__VIEWSTATE"]/@value')[0]
            state_generator = code_dom.xpath('//input[@id="__VIEWSTATEGENERATOR"]/@value')[0]
            event_validation = code_dom.xpath('//input[@id="__EVENTVALIDATION"]/@value')[0]

            all_poi = code_dom.xpath('//div[@id="DesktopResults"]//tr[td[@class="mapaddress"]]')
            for poi in all_poi:
                store_url = '<MISSING>'
                location_name = poi.xpath('.//td[@class="mapaddress"]/a/@id')[0]
                location_name = location_name if location_name else '<MISSING>'
                address_data = poi.xpath('.//td[@class="mapaddress"]/a/@onclick')[0]
                address_data = re.findall("javascript:ShowInfoBox\('(.+)'\)", address_data)[0].split('##')
                street_address = address_data[1]
                street_address = street_address if street_address else '<MISSING>'
                city = address_data[2].split(',')[0]
                city = city if city else '<MISSING>'
                state = address_data[2].split(',')[-1].strip().split()[0]
                state = state if state else '<MISSING>'
                zip_code = address_data[2].split(',')[-1].strip().split()[-1]
                zip_code = zip_code if zip_code else '<MISSING>'
                country_code = '<MISSING>'
                country_code = country_code if country_code else '<MISSING>'
                store_number = location_name.split('#')[-1]
                store_number = store_number if store_number else '<MISSING>'
                phone = poi.xpath('.//td[@class="mapphone"]/text()')[0]
                phone = phone if phone else '<MISSING>'
                location_type = '<MISSING>'
                location_type = location_type if location_type else '<MISSING>'
                latitude = address_data[-1].split(',')[0]
                latitude = latitude if latitude else '<MISSING>'
                longitude = address_data[-1].split(',')[-1]
                longitude = longitude if longitude else '<MISSING>'
                hours_of_operation = []
                hours_html = poi.xpath('.//td[@class="maphours"]//tr')
                for elem in hours_html:
                    day = elem.xpath('./td[1]/text()')[0]
                    hours = elem.xpath('./td[2]/text()')[0]
                    hours_of_operation.append('{} {}'.format(day, hours))
                hours_of_operation = ', '.join(hours_of_operation)
                
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

                if location_name not in scraped_items:
                    scraped_items.append(location_name)
                    items.append(item)
        
    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()

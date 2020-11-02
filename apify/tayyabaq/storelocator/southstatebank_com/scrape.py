import csv
from sgrequests import SgRequests
from lxml import etree
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('southstatebank_com')



def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

endprint = []

def format_hours(json_hours):
    hours = []
    for day_hours in json_hours:
        day = day_hours['day']
        intervals = day_hours['intervals']
        if not intervals:
            hours.append("{}: closed".format(day))
        else:
            interval = intervals[0]
            hours.append("{}: {}-{}".format(day, interval['start'], interval['end']))
    return ', '.join(hours)

def fetch_data():
    data = []
    store_links =[]
    c=0
    t=0;m=0
    session = SgRequests()
    url = 'https://locations.southstatebank.com/'
    page = etree.HTML(session.get(url).text)
    links = [url + x for x in page.xpath("//a[@class='c-directory-list-content-item-link']/@href")]
    page_urls = []
    for link in links:
        response = etree.HTML(session.get(link).text)
        store_links = response.xpath('//li[@class="c-LocationGridList-item"]//a[@class="Teaser-titleLink"]/@href')
        if store_links:
            page_urls += [url + l.split('/', 1)[1] for l in store_links]
        else:
            page_urls.append(link)
    for page_url in page_urls:
        logger.info(page_url)
        response = etree.HTML(session.get(page_url).text)
        name = response.xpath('//div[@class="Nap-geomodifier"]/text()')[0].strip()
        street = response.xpath('//span[@class="c-address-street-1"]/text()')[0].strip()
        city = response.xpath('//span[@class="c-address-city"]/text()')[0].strip()
        state = response.xpath('//abbr[@class="c-address-state"]/text()')[0].strip()
        zipcode = response.xpath('//span[@class="c-address-postal-code"]/text()')[0].strip()
        phone = response.xpath('//span[@id="telephone"]/text()')[0].strip()
        json_hours = json.loads(response.xpath('//div[@class="c-location-hours"]/div[contains(@class, "js-location-hours")]/@data-days')[0])
        hours = format_hours(json_hours)
        lat = response.xpath('//meta[@itemprop="latitude"]/@content')[0]
        lng = response.xpath('//meta[@itemprop="longitude"]/@content')[0]
        location_type = '<MISSING>'
        store_number = '<MISSING>'
        country = 'US'
        yield [url, page_url, name, street, city, state, zipcode, country, store_number, phone, location_type, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()

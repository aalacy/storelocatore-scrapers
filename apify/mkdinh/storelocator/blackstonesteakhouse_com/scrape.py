import json
from sgrequests import SgRequests
from bs4 import BeautifulSoup
from sglogging import sglog
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

def fetch_data():
    with SgRequests() as session:
        page_url = 'https://www.blackstonesteakhouse.com/location/blackstone-steakhouse/'
        response = session.get(page_url)
        soup = BeautifulSoup(response.text)
        scripts = soup.find('script', { 'type': 'application/ld+json' })

        script = json.loads(scripts.text)
        data = script['subOrganization'][0]
        locator_domain = 'blackstonesteakhouse.com'
        location_type = data['@type']
        location_name = data['name']

        address = data['address']
        street_address = address['streetAddress']
        city = address['addressLocality']
        state = address['addressRegion']
        zip = address['postalCode']

        map = soup.find('div', { 'class': 'gmaps' })
        lat = map.attrs['data-gmaps-lat']
        lng = map.attrs['data-gmaps-lng']

        phone = data['telephone']

        hours = []
        schedules = soup.find('section', { 'id': 'intro' }).find_all('p')
        for i, el in enumerate(schedules):
            if i:
                cleaned_hour = [item for item in el.text.split('\xa0') if item]
                hours.append(': push'.join(cleaned_hour))
        hours_of_operation = ', '.join(hours)

        yield SgRecord(
            page_url=page_url,
            locator_domain= locator_domain,
            location_type= location_type,
            location_name= location_name,
            street_address= street_address,
            city= city,
            state= state,
            zip_postal= zip,
            country_code= 'US',
            phone= phone,
            latitude= lat,
            longitude= lng,
            hours_of_operation= hours_of_operation,
        )

def write_output(data):
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        for row in fetch_data():
            writer.write_row(row)

if __name__ == '__main__':
    data = fetch_data()
    write_output(data)
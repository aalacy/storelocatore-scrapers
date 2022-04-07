import re
from bs4 import BeautifulSoup
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgpostal import parse_address, International_Parser
from sglogging import SgLogSetup
from sgrequests import SgRequests

logger = SgLogSetup().get_logger("questdiagonstics.com")

session = SgRequests()

def get_csrf_token():
    html = session.get('https://www.auchan.ro/store/home')
    soup = BeautifulSoup(html, 'html.parser')
    return soup.find('input', {"name":'CSRFToken'}).attrs['value']
    
def fetch_locations(token, query=""):
    data = {
        "locationQuery": re.sub(r'\(.*\)', '', query),
        "CSRFToken": token
    }
    html = session.post('https://www.auchan.ro/store/store-pickup/pointOfServices', data=data).text
    soup = BeautifulSoup(html, 'html.parser')

    cities = [item.text.strip() for item in soup.find('div', id='pos-list-localities').find_all('div', id='pos-list')]
    locations = soup.find_all('li', class_='searchPOSResult')

    return locations, cities

def fetch_data():
    token = get_csrf_token()
    locations, cities = fetch_locations(token)

    locator_domain = 'auchan.ro'
    page_url = 'https://www.auchan.ro/store/home'
    for city in cities:
        locations, _ = fetch_locations(token, city)

        for location in locations:
            store_number = location.find('button', id='changePickupStoreButton').attrs['data-store']
            latitude = location.attrs['data-latitude']
            longitude = location.attrs['data-longitude']

            location_name = location.find('span', class_='resultName').text.strip()
            address = location.find('div', class_='resultLine1').text
            parsed = parse_address(International_Parser(), address)

            street_address = parsed.street_address_1
            city = parsed.city
            postal = parsed.postcode
            state = parsed.state
            country_code = parsed.country

            yield SgRecord(
                locator_domain=locator_domain,
                page_url=page_url,
                store_number=store_number,
                location_name=location_name,
                latitude=latitude,
                longitude=longitude,
                street_address=street_address,
                city = city,
                zip_postal=postal,
                state=state,
                country_code=country_code,
            )



if __name__ == "__main__":
    data = fetch_data()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        for row in data:
            writer.write_row(row)

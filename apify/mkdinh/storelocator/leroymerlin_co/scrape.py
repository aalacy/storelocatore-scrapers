import re
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from bs4 import BeautifulSoup

from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgpostal import parse_address, International_Parser

domain = "leroymerlin.ro"
headers = {
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:92.0) Gecko/20100101 Firefox/92.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
}

local = threading.local()


def get_session(refresh=False):
    if not hasattr(local, "session") or refresh:
        local.session = SgRequests(proxy_country="ro")

    return local.session


def get_cities(county, retry=0):
    try:
        response = get_session(retry).get(
            "https://www.leroymerlin.ro/xhr/nomenclature/city",
            params={"countyId": county["id"]},
            headers=headers,
        )
        return [(county, city) for city in response.json()]
    except:
        if retry < 10:
            return get_cities(county, retry + 1)


def fetch_counties(retry=0):
    try:
        response = get_session().get("https://www.leroymerlin.ro", headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")
        select = soup.find("select", {"id": "contextualization-county"})
        options = select.find_all("option")
        counties = []
        for option in options:
            county_name = option.text.strip()
            county_id = option.attrs.get("value")
            if county_id:
                counties.append(
                    {
                        "id": county_id,
                        "name": county_name,
                    }
                )

        return counties
    except:
        if retry < 10:
            return fetch_counties(retry)


def fetch_locations(county, city):
    try:
        response = get_session().get(
            "https://www.leroymerlin.ro/xhr/contextualization/store",
            params={"cityId": city["id"]},
            headers=headers,
        )
        return [(county, city, location) for location in response.json()]
    except:
        return []


def fetch_details(county, city, location, retry=0):
    try:
        page_url = f'https://www.leroymerlin.ro/magazine/{location["slug"]}'
        response = get_session(retry).get(page_url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")
        name_dom, address_dom = soup.find("li", {"class": "row address"}).find_all("p")

        location_name = name_dom.get_text()

        _, hours = soup.find("li", {"class": "row shedule"}).find_all("p")
        hours_of_operation = []
        for el in hours:
            if isinstance(el, str):
                hours_of_operation.append(el.text)

        location_name = name_dom.text.strip()
        address = address_dom.text.strip()
        parsed = parse_address(International_Parser(), address)

        street_address = parsed.street_address_1
        state = county["name"]
        city = city["title"]

        phone = re.search(r"(\d+)", soup.find("li", {"class": "row phone"}).text).group(
            1
        )

        return SgRecord(
            locator_domain="leroymerlin.ro",
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            country_code="ro",
            phone=phone,
            hours_of_operation=hours_of_operation,
            raw_address=address,
        )
    except:
        if retry < 3:
            return fetch_details(county, city, location, retry + 1)

        print(response)


def fetch_data():
    with ThreadPoolExecutor() as executor:
        county_cities = []
        counties = fetch_counties()
        futures = [executor.submit(get_cities, county) for county in counties]
        for future in as_completed(futures):
            county_cities.extend(future.result())

        locations = []
        futures = [
            executor.submit(fetch_locations, county, city)
            for county, city in county_cities
        ]
        for future in as_completed(futures):
            locations.extend(future.result())

        pois = []
        futures = [
            executor.submit(fetch_details, county, city, location)
            for county, city, location in locations
        ]
        for future in as_completed(futures):
            poi = future.result()
            if poi:
                pois.append(poi)

        return pois


def scrape():
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.STREET_ADDRESS}
            )
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()

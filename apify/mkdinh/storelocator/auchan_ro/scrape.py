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
    html = session.get("https://www.auchan.ro/store/home")
    soup = BeautifulSoup(html, "html.parser")
    return soup.find("input", {"name": "CSRFToken"}).attrs["value"]


def fetch_locations(pageNum=0, locations=None):
    if not locations:
        locations = []

    page = session.get(
        f"https://www.auchan.ro/store/store-finder?page={pageNum}&view=&pageSize=7"
    ).text
    soup = BeautifulSoup(page, "html.parser")
    items = [
        f'https://www.auchan.ro{item.find("form")["action"]}'
        for item in soup.find_all("div", class_="storeItem")
    ]
    locations.extend(items)

    if len(items):
        fetch_locations(pageNum + 1, locations)

    return locations


def fetch_data():

    for page_url in fetch_locations():
        page = session.get(page_url).text
        soup = BeautifulSoup(page, "html.parser")

        locator_domain = "auchan.ro"
        location_name = soup.find("div", class_="store-name").getText(strip=True)
        store_number = re.split("/", page_url)[-1]
        hours, address, phone, *other = soup.find_all("div", class_="detailSection")
        hours_of_operation = re.sub(r"\s\s+", "", re.sub(r"\n", "", hours.text.strip()))

        parsed = parse_address(International_Parser(), address.getText())
        street_address = parsed.street_address_1
        city = parsed.city
        state = parsed.state
        postcode = parsed.postcode
        country = parsed.country

        canvas = soup.find("div", id="map_canvas")
        latitude = canvas["data-latitude"]
        longitude = canvas["data-longitude"]

        phone = re.sub(r"Telefon:", "", phone.getText(strip=True))

        yield SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            store_number=store_number,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postcode,
            country_code=country,
            latitude=latitude,
            longitude=longitude,
            phone=phone,
            hours_of_operation=hours_of_operation,
        )


if __name__ == "__main__":
    data = fetch_data()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        for row in data:
            writer.write_row(row)

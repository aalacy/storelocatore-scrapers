import re
import json
import threading
from sgselenium import SgChrome
from bs4 import BeautifulSoup

from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("wawa.com")

local = threading.local()


def fetch_store_numbers():
    store_numbers = []
    with SgChrome(is_headless=True).driver() as driver:
        driver.get("https://www.wawa.com/site-map")
        soup = BeautifulSoup(driver.page_source)
        links = soup.find_all("a", class_="CMSSiteMapLink")
        for link in links:
            matched = re.search(r"\/store\/(\d+)\/.*", link["href"])
            if matched:
                store_numbers.append(matched.group(1))

    return store_numbers


def get(obj, key, default=SgRecord.MISSING):
    return obj.get(key, default) or default


def find_address_by_context(context, addresses):
    for address in addresses:
        if address["context"] == context:
            return address


def format_hours(start, end):
    if not start and not end:
        return SgRecord.MISSING

    return f"{start}-{end}" if end else start


def fetch_location(id, retry_count=0):
    try:
        url = (
            f"https://www.wawa.com/Handlers/LocationByStoreNumber.ashx?storeNumber={id}"
        )

        with SgChrome(is_headless=True).driver() as driver:
            driver.get(url)
            soup = BeautifulSoup(driver.page_source, "html.parser")

            result = json.loads(soup.pre.text)

            store_number = get(result, "locationID")
            page_url = f"https://www.wawa.com/Handlers/LocationByStoreNumber.ashx?storeNumber={store_number}"
            location_name = get(result, "storeName")

            addresses = result.get("addresses", [])
            if not len(addresses):
                return None

            address = find_address_by_context("friendly", addresses)

            street_address = re.sub(
                r"\s*\(.*\)?\s*|\s*@.*\s*", "", get(address, "address")
            )
            city = get(address, "city")
            state = get(address, "state")
            zip_postal = get(address, "zip")
            country_code = "US"

            geo = find_address_by_context("physical", addresses)
            latitude, longitude = get(geo, "loc", [SgRecord.MISSING, SgRecord.MISSING])

            hours_of_operation = format_hours(
                get(result, "storeOpen"), get(result, "storeClose")
            )
            phone = get(result, "telephone")

            return SgRecord(
                locator_domain="wawa.com",
                page_url=page_url,
                store_number=store_number,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_postal,
                country_code=country_code,
                latitude=str(latitude),
                longitude=str(longitude),
                hours_of_operation=hours_of_operation,
                phone=phone,
            )
    except Exception as e:
        logger.error(e)
        if retry_count < 5:
            return fetch_location(id, retry_count + 1)
        else:
            return None


def write_data(data):
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.STREET_ADDRESS}
            )
        )
    ) as writer:
        for item in data:
            writer.write_row(item)


def fetch_data():
    store_numbers = fetch_store_numbers()
    for num in store_numbers:
        location = fetch_location(num)
        if location:
            yield location


if __name__ == "__main__":
    data = fetch_data()
    write_data(data)

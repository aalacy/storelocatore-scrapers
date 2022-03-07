from sgpostal.sgpostal import parse_address_intl
import time
from lxml import html
from sglogging import sglog
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

from sgrequests import SgRequests


website = "unode50.com"
api_url = "https://www.unode50.com/as/amlocator/index/ajax/"

MISSING = SgRecord.MISSING
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()


def stringify_nodes(body, xpath):
    nodes = body.xpath(xpath)
    values = []
    for node in nodes:
        for text in node.itertext():
            text = text.strip()
            if text:
                values.append(text)
    if len(values) == 0:
        return MISSING
    return " ".join((" ".join(values)).split())


def get_address(raw_address):
    try:
        if raw_address is not None and raw_address != MISSING:
            data = parse_address_intl(raw_address)
            street_address = data.street_address_1
            if data.street_address_2 is not None:
                street_address = street_address + " " + data.street_address_2
            city = data.city
            state = data.state
            zip_postal = data.postcode

            if street_address is None or len(street_address) == 0:
                street_address = MISSING
            if city is None or len(city) == 0:
                city = MISSING
            if state is None or len(state) == 0:
                state = MISSING
            if zip_postal is None or len(zip_postal) == 0:
                zip_postal = MISSING
            return street_address, city, state, zip_postal
    except Exception as e:
        log.info(f"Missing address: {e}")
        pass
    return MISSING, MISSING, MISSING, MISSING


def fetch_data():

    data = session.get(api_url).json()

    stores = data["items"]

    log.info(f"Total stores = {len(stores)}")
    for store in stores:
        country_code = MISSING
        phone = MISSING
        location_type = MISSING
        hours_of_operation = MISSING

        pophtml = html.fromstring(store["popup_html"], "lxml")

        location_name = pophtml.xpath("//div[@class='amlocator-title']/text()")[0]

        raw_address = (
            stringify_nodes(pophtml, '//div[contains(@class, "amlocator-info-popup")]')
            .replace(location_name, "", 1)
            .strip()
        )

        store_number = store["id"]

        street_address, city, state, zip_postal = get_address(raw_address)
        latitude = store["lat"]
        longitude = store["lng"]
        page_url = f"https://www.unode50.com/en/int/stores#{latitude},{longitude}"

        yield SgRecord(
            locator_domain=website,
            store_number=store_number,
            page_url=page_url,
            location_name=location_name,
            location_type=location_type,
            street_address=street_address,
            city=city,
            zip_postal=zip_postal,
            state=state,
            country_code=country_code,
            phone=phone,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
            raw_address=raw_address,
        )
    return []


def scrape():
    log.info(f"Start scrapping {website} ...")
    start = time.time()
    with SgWriter(
        deduper=SgRecordDeduper(RecommendedRecordIds.StoreNumberId)
    ) as writer:
        for rec in fetch_data():
            writer.write_row(rec)
    end = time.time()
    log.info(f"Scrape took {end-start} seconds.")


if __name__ == "__main__":
    scrape()

from sglogging import SgLogSetup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import parse_address_intl
from urllib.parse import urlparse
from lxml import html
from typing import Iterable


DOMAIN = "papajohns.co.nl"
logger = SgLogSetup().get_logger(logger_name="papajohns_co_nl")
MISSING = SgRecord.MISSING
LOCATION_URLS = [
    "https://www.papajohns.ma/locator",
    "https://www.papajohns.co.nl/locator",
    "https://www.papajohns.fr/locator",
]
HEADERS = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}


def get_clean_data(raw_data):
    clean_data = [" ".join(i.split()) for i in raw_data]
    clean_data = [i for i in clean_data if i]
    return clean_data


def fetch_records(http: SgRequests) -> Iterable[SgRecord]:
    for countrynum, locurl in enumerate(LOCATION_URLS[0:]):
        r = http.get(locurl, headers=HEADERS)
        sel = html.fromstring(r.text, "lxml")
        locator_restaurants = sel.xpath(
            '//div[contains(@class, "locator__restaurants")]/article'
        )
        for idx, lr in enumerate(locator_restaurants[0:]):
            locator_domain = urlparse(locurl).netloc.replace("www.", "")
            logger.info(f"[{idx}] locator_domain: {locator_domain}")

            page_url = locurl
            logger.info(f"[{idx}] Page URL: {page_url}")
            location_name = lr.xpath(
                './/h3[contains(@class, "locator-restaurant__name")]/text()'
            )
            location_name = get_clean_data(location_name)
            location_name = "".join(location_name)
            location_name = location_name if location_name else MISSING
            logger.info(f"[{idx}] location_name: {location_name}")
            cc = urlparse(locurl).netloc.split(".")[-1].upper()

            if cc == "FR":
                location_name = lr.xpath(
                    './/h3/div[contains(@class, "locator-restaurant__name-inside")]/text()'
                )
                location_name = get_clean_data(location_name)
                location_name = "".join(location_name)
                location_name = location_name if location_name else MISSING

            add = lr.xpath(
                './/div[contains(@class, "locator-restaurant__address")]/p/text()'
            )
            logger.info(f"[{idx}] Raw Address: {add}")
            add_parts = get_clean_data(add)
            logger.info(f"[{idx}] Clean Address: {add_parts}")
            add_part2 = add_parts[1:]
            raw_add = ", ".join(add_part2)
            pai = parse_address_intl(raw_add)
            street_address = pai.street_address_1 or MISSING
            logger.info(f"[{idx}] Street Address: {street_address}")

            city = pai.city or MISSING
            logger.info(f"[{idx}] City: {city}")

            state = pai.state or MISSING
            logger.info(f"[{idx}] State: {state}")

            zip_postal = pai.postcode or MISSING
            logger.info(f"[{idx}] Zip Code: {zip_postal}")

            # Country Code
            logger.info(f"[{idx}] Address: {add}")
            country_code = urlparse(locurl).netloc.split(".")[-1].upper()
            logger.info(f"[{idx}] Country Code: {country_code}")

            # Store Number
            store_number = ""
            store_number = store_number if store_number else MISSING
            logger.info(f"[{idx}] Store Number: {store_number}")

            # Phone
            phone = add_parts[0]
            phone = phone if phone else MISSING
            logger.info(f"[{idx}] Phone: {phone}")

            # Location type
            location_type = "Restaurant"
            logger.info(f"[{idx}] location_name: {location_name}")

            # Latitude
            latitude = ""
            latitude = latitude if latitude else MISSING
            logger.info(f"[{idx}] latitude: {latitude}")

            # Longitude
            longitude = ""
            longitude = longitude if longitude else MISSING
            logger.info(f"[{idx}] longitude: {longitude}")

            hoo = lr.xpath(
                './/div[contains(@class, "locator-restaurant__opening-times")]/p//text()'
            )
            hoo = get_clean_data(hoo)
            hours_of_operation = ""
            if hoo:
                hours_of_operation = ", ".join(hoo)
            else:
                hours_of_operation = MISSING

            if country_code == "FR":
                # hours of operation need to clean for the stores in France
                hours_of_operation = (
                    hours_of_operation.split("Zone de Livraison")[0]
                    .rstrip(" ")
                    .rstrip(",")
                )

            logger.info(f"[{idx}] hours_of_operation: {hours_of_operation}")
            raw_address = ""

            if raw_add:
                raw_address = raw_add
            else:
                raw_address = MISSING
            logger.info(f"[{idx}] raw_address: {raw_address}")
            rec = SgRecord(
                locator_domain=locator_domain,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_postal,
                country_code=country_code,
                store_number=store_number,
                phone=phone,
                location_type=location_type,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
                raw_address=raw_address,
            )
            yield rec


def scrape():
    count = 0
    logger.info("Scrape Started")
    with SgWriter(
        SgRecordDeduper(
            SgRecordID({SgRecord.Headers.STREET_ADDRESS, SgRecord.Headers.PAGE_URL})
        )
    ) as writer:
        with SgRequests() as http:
            for rec in fetch_records(http):
                writer.write_row(rec)
                count = count + 1

    logger.info(f"No of records being processed: {count}")
    logger.info("Scrape Finished!")


if __name__ == "__main__":
    scrape()

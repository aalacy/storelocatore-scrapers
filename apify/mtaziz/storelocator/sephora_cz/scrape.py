from urllib.parse import urlparse
from sglogging import SgLogSetup
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgrequests import SgRequests
import json
from lxml import html
import ssl


try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification

DOMAIN = "sephora.cz"
LOCATION_URLS_GRID = [
    "https://www.sephora.cz/prodejny",
    "https://www.sephora.dk/butikker/",
    "https://www.sephora.fr/magasin",
    "https://www.sephora.pt/lojas",
    "https://www.sephora.es/tiendas",
    "https://www.sephora.se/butiker/",
    "https://ch.sephora.fr/ch/fr/magasin",
    "https://www.sephora.ae/en/store",
    "https://www.sephora.de/Stores-Alle",
    "https://www.sephora.it/beauty-store/",
    "https://www.sephora.pl/perfumerie",
]

MISSING = SgRecord.MISSING
logger = SgLogSetup().get_logger("sephora_cz")
headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36",
}


def fetch_records():
    with SgRequests() as http:
        for gunum, gurl in enumerate(LOCATION_URLS_GRID[0:]):
            r = http.get(gurl, headers=headers)
            sel = html.fromstring(r.text, "lxml")
            purls = sel.xpath('//a[contains(@class, "store-name")]/@href')
            logger.info(f"Pulling the store URLs from: {gurl}")
            logger.info(f"{gurl} | Total number of Store URLs: {len(purls)}")
            for idx, store_url in enumerate(purls[0:]):
                logger.info(f"[{idx}] Pulling the data from: {store_url}")
                rcz = http.get(store_url, headers=headers)
                sel_cz = html.fromstring(rcz.text, "lxml")
                dcz = sel_cz.xpath(
                    '//script[contains(@type, "application/ld+json") and contains(text(), "telephone")]/text()'
                )
                dcz1 = "".join(dcz)
                data_json = json.loads(dcz1)
                domain = urlparse(store_url).netloc
                locator_domain = domain.replace("www.", "")
                page_url = store_url
                logger.info(f"[{idx}] page_url: {page_url}")

                location_name = data_json["name"]
                location_name = location_name if location_name else MISSING
                logger.info(f"[{idx}] location_name: {location_name}")

                add = data_json["address"]
                street_address = add["streetAddress"]
                logger.info(f"[{idx}] Street Address: {street_address}")

                city = add["addressLocality"]
                city = city if city else MISSING
                logger.info(f"[{idx}] City: {city}")

                state = ""
                state = state if state else MISSING
                logger.info(f"[{idx}] State: {state}")

                zip_postal = add["postalCode"]
                zip_postal = zip_postal if zip_postal else MISSING
                logger.info(f"[{idx}] Zip Code: {zip_postal}")

                country_code = locator_domain.split(".")[-1].upper()
                logger.info(f"[{idx}] country_code: {country_code}")

                store_number = page_url.split("storeID=")[-1]
                logger.info(f"[{idx}] store_number: {store_number}")

                phone = data_json["telephone"]
                phone = phone if phone else MISSING
                logger.info(f"[{idx}] Phone: {phone}")

                # Location Type
                location_type = data_json["@type"]
                location_type = location_type if location_type else MISSING
                logger.info(f"[{idx}] location_type: {location_type}")

                # Latlng
                latlng = "".join(
                    sel_cz.xpath(
                        '//div[contains(@data-default-coordinates, "longitude")]/@data-default-coordinates'
                    )
                )
                latlng1 = json.loads(latlng)

                # Latitude
                latitude = latlng1["latitude"]
                latitude = latitude if latitude else MISSING
                logger.info(f"[{idx}] lat: {latitude}")

                # Longitude
                longitude = latlng1["longitude"]
                longitude = longitude if longitude else MISSING
                logger.info(f"[{idx}] lng: {longitude}")

                hours_of_operation = ""
                hoo = data_json["openingHours"]
                if isinstance(hoo, list):
                    hours_of_operation = ", ".join(hoo)
                else:
                    hours_of_operation = hoo

                logger.info(f"[{idx}] hours_of_operation: {hours_of_operation}")

                # Raw Address
                raw_address = ""
                raw_address = raw_address if raw_address else MISSING
                idx += 1
                yield SgRecord(
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


def scrape():
    logger.info("Started")
    count = 0
    with SgWriter(
        SgRecordDeduper(
            SgRecordID({SgRecord.Headers.STORE_NUMBER, SgRecord.Headers.PAGE_URL})
        )
    ) as writer:
        records = fetch_records()
        for rec in records:
            writer.write_row(rec)
            count = count + 1
    logger.info(f"No of records being processed: {count}")
    logger.info("Finished")


if __name__ == "__main__":
    scrape()

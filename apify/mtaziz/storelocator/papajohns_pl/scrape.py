from tenacity import retry, stop_after_attempt
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgpostal.sgpostal import parse_address_intl
from typing import Iterable
from urllib.parse import urlparse

logger = SgLogSetup().get_logger("papajohns_pl")
DOMAIN = "papajohns.pl"
MISSING = SgRecord.MISSING
API_ENDPOINT_URLS = [
    "https://api.papajohns.pl/restaurant/list?lang=en&platform=web&city_id=1",
    "https://api.papajohns.ru/restaurant/list?city_id=1&lang=en&platform=web",
    "https://api.papajohns.kz/restaurant/list?lang=en&platform=web&city_id=1",
    "https://api.papajohns.kg/restaurant/list?lang=en&platform=web&city_id=1",
]


HEADERS = {
    "accept": "application/json, text/plain, */*",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36",
}


@retry(stop=stop_after_attempt(5))
def get_store_data(http, url):
    res_data = http.get(url, headers=HEADERS).json()
    return res_data


def fetch_records(http: SgRequests) -> Iterable[SgRecord]:
    for countrynum, api_endpoint_url in enumerate(API_ENDPOINT_URLS[0:]):
        data_json = get_store_data(http, api_endpoint_url)
        aeu_domain = urlparse(api_endpoint_url).netloc
        logger.info(f"API-based domain: {aeu_domain}")
        for idx, _ in enumerate(data_json[0:]):
            locator_domain = aeu_domain.replace("api.new.", "").replace("api.", "")
            logger.info(f"[{idx}] locator_domain: {locator_domain}")

            page_url = api_endpoint_url
            page_url = page_url if page_url else MISSING
            logger.info(f"[{idx}] page_url: {page_url}")

            location_name = _["name"]
            location_name = location_name if location_name else MISSING
            logger.info(f"[{idx}] location_name: {location_name}")

            add = _["address"]
            pai = parse_address_intl(add)
            street_address = pai.street_address_1
            street_address = street_address if street_address else MISSING
            logger.info(f"[{idx}] Street Address: {street_address}")

            city = pai.city
            city = city if city else MISSING
            logger.info(f"[{idx}] City: {city}")

            state = _["metro"]
            state = state if state else MISSING
            logger.info(f"[{idx}] State: {state}")

            zip_postal = pai.postcode
            zip_postal = zip_postal if zip_postal else MISSING
            logger.info(f"[{idx}] Zip Code: {zip_postal}")

            country_code = aeu_domain.split(".")[-1].upper()
            logger.info(f"[{idx}] country_code: {country_code}")

            store_number = _["id"]
            if store_number:
                store_number = str(store_number) + country_code
            logger.info(f"[{idx}] store_number: {store_number}")

            phone = _["phones"]
            phone = phone.split(",")[0].strip()
            phone = phone if phone else MISSING
            logger.info(f"[{idx}] Phone: {phone}")

            # Location Type
            location_type = "Restaurant"
            location_type = location_type if location_type else MISSING
            logger.info(f"[{idx}] location_type: {location_type}")

            # Latitude
            latitude = _["coordinates"][0]
            latitude = latitude if latitude else MISSING
            if latitude == str(0.0):
                latitude = MISSING
            logger.info(f"[{idx}] lat: {latitude}")

            # Longitude
            longitude = _["coordinates"][-1]
            longitude = longitude if longitude else MISSING
            if longitude == str(0.0):
                longitude = MISSING
            logger.info(f"[{idx}] lng: {longitude}")

            hoo = _["open"]

            daytimes = ""
            for k, v in hoo.items():
                daytimes += k + " " + v + "; "

            daytimes = daytimes.rstrip("; ")
            hours_of_operation = daytimes if daytimes else MISSING
            logger.info(f"[{idx}] hours_of_operation: {hours_of_operation}")

            # Raw Address
            raw_address = _["address"]
            raw_address = add
            raw_address = raw_address if raw_address else MISSING
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
    count = 0
    logger.info("Started")
    with SgWriter(
        SgRecordDeduper(
            SgRecordID({SgRecord.Headers.STORE_NUMBER, SgRecord.Headers.STREET_ADDRESS})
        )
    ) as writer:
        with SgRequests() as http:
            results = fetch_records(http)
            for rec in results:
                writer.write_row(rec)
                count = count + 1

    logger.info(f"No of records being processed: {count}")
    logger.info("Finished")


if __name__ == "__main__":
    scrape()

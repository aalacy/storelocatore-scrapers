from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json


logger = SgLogSetup().get_logger("trihealth_com")
MISSING = SgRecord.MISSING
DOMAIN = "trihealth.com"
headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36",
}


def fetch_records(http):
    first_page_num = 1
    api_endpoint_url_custom_page_num = (
        f"https://directory.trihealthpho.com/api/search?sort=name&page={first_page_num}"
    )
    r_page_num = http.get(api_endpoint_url_custom_page_num, headers=headers)
    d_page_num = json.loads(r_page_num.text)
    max_page_num = d_page_num["data"]["total_pages"]
    for page_num in range(1, max_page_num + 1):
        api_endpoint_url_custom = (
            f"https://directory.trihealthpho.com/api/search?sort=name&page={page_num}"
        )
        r3 = http.get(api_endpoint_url_custom, headers=headers)
        d3 = json.loads(r3.text)
        d4 = d3["data"]["providers"]
        for i in d4:
            l = i["locations"]
            for idx, j in enumerate(l):
                locator_domain = DOMAIN
                page_url = api_endpoint_url_custom
                logger.info(f"[{idx}] page_url: {page_url}")

                location_name = j["name"]
                location_name = location_name if location_name else MISSING
                logger.info(f"[{idx}] location_name: {location_name}")

                street_address = j["street1"]
                street_address = street_address if street_address else MISSING
                logger.info(f"[{idx}] Street Address: {street_address}")

                city = j["city"]
                city = city if city else MISSING
                logger.info(f"[{idx}] City: {city}")

                state = j["state"]
                state = state if state else MISSING
                logger.info(f"[{idx}] State: {state}")

                zip_postal = j["zip"]
                zip_postal = zip_postal if zip_postal else MISSING
                logger.info(f"[{idx}] Zip Code: {zip_postal}")

                country_code = "US"
                logger.info(f"[{idx}] country_code: {country_code}")

                store_number = j["id"]
                store_number = store_number if store_number else MISSING
                logger.info(f"[{idx}]  store_number: {store_number}")

                phone = j["phone"]
                phone = phone if phone else MISSING
                logger.info(f"[{idx}]  Phone: {phone}")

                # Location Type
                location_type = j["type"]
                location_type = location_type if location_type else MISSING
                logger.info(f"[{idx}] location_type: {location_type}")

                # Latitude
                latitude = j["coordinates"]["lat"]
                latitude = latitude if latitude else MISSING
                logger.info(f"[{idx}] lat: {latitude}")

                # Longitude
                longitude = j["coordinates"]["lon"]
                longitude = longitude if longitude else MISSING
                logger.info(f"[{idx}] lng: {longitude}")

                hours_of_operation = ""
                hours_of_operation = (
                    hours_of_operation if hours_of_operation else MISSING
                )
                logger.info(f"[{idx}] hours_of_operation: {hours_of_operation}")

                # Raw Address
                raw_address = ""
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
    logger.info("Started")
    count = 0
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STORE_NUMBER}))
    ) as writer:
        with SgRequests() as http:
            records = fetch_records(http)
            for rec in records:
                writer.write_row(rec)
                count = count + 1
    logger.info(f"No of records being processed: {count}")
    logger.info("Finished")


if __name__ == "__main__":
    scrape()

import json
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal import sgpostal as parser

session = SgRequests()
website = "armani.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "authority": "www.armani.com",
    "cache-control": "max-age=0",
    "sec-ch-ua": '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
    "sec-ch-ua-mobile": "?0",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "none",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    stores_req = session.get(
        "https://www.armani.com/experience/us/?yoox_storelocator_action=true&action=yoox_storelocator_get_all_stores",
        headers=headers,
    )

    dict_from_json = json.loads(stores_req.text)
    for store_data in dict_from_json:
        if "location" not in store_data:
            continue

        location_name = store_data["post_title"]
        raw_address = store_data["wpcf-yoox-store-geolocation-address"]
        formatted_addr = parser.parse_address_intl(raw_address)

        street_address = formatted_addr.street_address_1
        if street_address is not None and formatted_addr.street_address_2:
            street_address = street_address + ", " + formatted_addr.street_address_2

        if street_address is None:
            street_address = "<MISSING>"
        state = formatted_addr.state
        if state is None:
            state = "<MISSING>"

        zip = formatted_addr.postcode
        if zip is None:
            zip = "<MISSING>"

        city = store_data["location"]["city"]["name"]
        country_code = store_data["wpcf-yoox-store-country-iso"].upper()
        store_number = store_data["ID"]
        phone = (
            store_data["wpcf-yoox-store-phone"]
            .replace("\xa0", "")
            .split("Suggest")[0]
            .split("|")[0]
            if "wpcf-yoox-store-phone" in store_data
            and store_data["wpcf-yoox-store-phone"]
            else "<MISSING>"
        )
        location_type = store_data["wpcf-store-main-store-brand"]
        latitude = store_data["_yoox-store-lat"]
        longitude = store_data["_yoox-store-lng"]
        hours_of_operation = "<MISSING>"
        page_url = "https://www.armani.com/experience/us/store-locator/#store/" + str(
            store_data["ID"]
        )

        yield SgRecord(
            locator_domain=website,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip,
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
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.StoreNumberId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()

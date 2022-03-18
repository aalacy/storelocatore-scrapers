# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
import json
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal import sgpostal as parser

website = "jeanswest.com.au"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "authority": "www.jeanswest.com.au",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="98", "Google Chrome";v="98"',
    "accept": "application/json, text/javascript, */*; q=0.01",
    "x-requested-with": "XMLHttpRequest",
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.82 Safari/537.36",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "referer": "https://www.jeanswest.com.au/stores?showMap=true",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}

params = (
    ("showMap", "true"),
    ("radius", "300000000"),
    ("lat", "-35.2828"),
    ("long", "149.1283"),
)


def fetch_data():
    # Your scraper here

    with SgRequests() as session:
        stores_req = session.get(
            "https://www.jeanswest.com.au/on/demandware.store/Sites-jeanswest-au-Site/en_AU/Stores-FindStores",
            headers=headers,
            params=params,
        )
        stores = json.loads(stores_req.text)["stores"]

        for store in stores:
            store_number = store["ID"]
            locator_domain = website
            location_name = store["name"]
            page_url = store["url"]
            street_address = store["address1"]
            add_2 = store["address2"]
            if add_2 is not None and len(add_2) > 0:
                street_address = street_address + ", " + add_2

            street_address = street_address.replace(",,", ",").strip()
            raw_address = street_address

            city = store.get("city", "<MISSING>")
            if city and city != "<MISSING>":
                raw_address = raw_address + ", " + city

            state = store.get("stateCode", "<MISSING>")
            if state and state != "<MISSING>":
                raw_address = raw_address + ", " + state

            zip = store.get("postalCode", "<MISSING>")
            if zip and zip != "<MISSING>":
                raw_address = raw_address + ", " + zip

            formatted_addr = parser.parse_address_intl(raw_address)
            street_address = formatted_addr.street_address_1
            if street_address:
                if formatted_addr.street_address_2:
                    street_address = (
                        street_address + ", " + formatted_addr.street_address_2
                    )
            else:
                if formatted_addr.street_address_2:
                    street_address = formatted_addr.street_address_2

            country_code = store["countryCode"]
            phone = store.get("phone", "<MISSING>")

            location_type = "<MISSING>"

            latitude = store["latitude"]
            longitude = store["longitude"]

            hours_of_operation = "; ".join(
                store["storeHours"].split("<br/> \n")
            ).strip()

            yield SgRecord(
                locator_domain=locator_domain,
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

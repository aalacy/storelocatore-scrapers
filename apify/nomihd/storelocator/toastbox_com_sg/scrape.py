# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal import sgpostal as parser
import json

website = "toastbox.com.sg"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Referer": "https://toastbox.com.sg/locations.html",
    "X-Requested-With": "XMLHttpRequest",
    "sec-ch-ua-mobile": "?0",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36",
    "sec-ch-ua-platform": '"Windows"',
}


def fetch_data():
    # Your scraper here
    search_url = "https://toastbox.com.sg/data/location.json"
    with SgRequests() as session:
        stores_req = session.get(search_url, headers=headers)
        regions = json.loads(stores_req.text)["area"]
        for region in regions.keys():
            stores = regions[region]["stores"]
            for store in stores:
                page_url = "https://toastbox.com.sg/locations.html"
                locator_domain = website
                location_name = store["title"]
                raw_address = (
                    store["address"]
                    .replace(" <br>", ", ")
                    .strip()
                    .replace(" <br/>", "; ")
                    .strip()
                    .replace("<br>", ", ")
                    .strip()
                    .replace("<br/>", "; ")
                    .strip()
                )
                raw_address_temp = (
                    raw_address.replace("S(", "Singapore ").replace(")", "").strip()
                )
                formatted_addr = parser.parse_address_intl(raw_address_temp)
                street_address = formatted_addr.street_address_1
                if formatted_addr.street_address_2:
                    street_address = (
                        street_address + ", " + formatted_addr.street_address_2
                    )

                city = formatted_addr.city
                if city and city == "Singapore":
                    city = "<MISSING>"

                state = region
                zip = formatted_addr.postcode
                country_code = "SG"
                store_number = "<MISSING>"
                phone = store["phone"]

                location_type = "<MISSING>"

                hours_of_operation = store["operating"]
                if hours_of_operation:
                    hours_of_operation = (
                        hours_of_operation.replace("<br/>", "; ")
                        .strip()
                        .replace("<br>", ";")
                        .replace("<br />", ";")
                        .strip()
                        .replace(" ;", ";")
                        .strip()
                    )

                latitude, longitude = store["map"]["lat"], store["map"]["lng"]

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
        deduper=SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()

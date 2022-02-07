# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json
import re
from sgpostal import sgpostal as parser
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "infineon.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "authority": "www.infineon.com",
    "cache-control": "max-age=0",
    "sec-ch-ua": '" Not;A Brand";v="99", "Google Chrome";v="97", "Chromium";v="97"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "none",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here

    api_url = "https://www.infineon.com/locationFinder/locations?types=&locale=en&site=ifx&region=&country="
    with SgRequests() as session:
        api_res = session.get(api_url, headers=headers)

        json_res = json.loads(api_res.text)

        stores_list = json_res["locations"]

        for store in stores_list:

            page_url = "https://www.infineon.com/cms/en/about-infineon/company/find-a-location/"
            locator_domain = website

            location_name = store["name"].strip()

            street_address = store["address"].strip()
            if "address2" in store and store["address2"].strip():
                street_address = street_address + " " + store["address2"].strip()

            city = store["city"].strip()
            if "state" in store:
                state = store["state"].strip()
            else:
                state = "<MISSING>"

            country_code = store["country"]
            store_number = store["id"]

            phone = "<MISSING>"

            raw_address = street_address

            if re.search("[0-9]", raw_address[-1]):
                phone = raw_address.split(",")[-1].strip()
                raw_address = ",".join(street_address.split(",")[:-1])

            formatted_addr = parser.parse_address_intl(raw_address)
            street_address = formatted_addr.street_address_1
            if formatted_addr.street_address_2:
                street_address = street_address + ", " + formatted_addr.street_address_2
            zip = formatted_addr.postcode
            if state == "<MISSING>":
                state = formatted_addr.state

            location_type = "<MISSING>"

            hours_of_operation = "<MISSING>"
            latitude = store["latitude"]
            longitude = store["longitude"]

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

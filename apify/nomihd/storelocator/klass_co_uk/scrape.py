# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgpostal import sgpostal as parser
import json
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "klass.co.uk"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "Connection": "keep-alive",
    "sec-ch-ua": '" Not;A Brand";v="99", "Google Chrome";v="97", "Chromium";v="97"',
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Content-Type": "application/json; charset=UTF-8",
    "X-Requested-With": "XMLHttpRequest",
    "sec-ch-ua-mobile": "?0",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36",
    "sec-ch-ua-platform": '"Windows"',
    "Origin": "https://www.klass.co.uk",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Dest": "empty",
    "Referer": "https://www.klass.co.uk/storefinder.html",
    "Accept-Language": "en-US,en;q=0.9,ar;q=0.8",
}

data = '{ "distanceLimit": "99999999", "latitude": "53.59773759999999",  "longittude": "-2.1739569",  "type": "0",  "address": "53.59787386433848, -2.1736965179443"}'


def fetch_data():
    # Your scraper here
    search_url = "https://www.klass.co.uk/storefinder.html"
    api_url = "https://www.klass.co.uk/storefinder.aspx/GetStoresWithinRange"

    with SgRequests() as session:
        api_res = session.post(api_url, headers=headers, data=data)

        json_res = json.loads(api_res.text)

        stores_str = json_res["d"]
        stores = json.loads(stores_str)

        for no, store in enumerate(stores, 1):

            locator_domain = website

            page_url = search_url

            location_name = store["Name"].strip()

            location_type = str(store["Type"])
            if location_type == "0":
                location_type = "Standalone Stores"
            elif location_type == "1":
                location_type = "Klass Concessions"

            raw_address = (
                store["Address"]
                .replace("Address:", "")
                .strip()
                .replace(",,", ",")
                .strip()
            )

            formatted_addr = parser.parse_address_intl(raw_address)
            street_address = formatted_addr.street_address_1
            if formatted_addr.street_address_2:
                street_address = street_address + ", " + formatted_addr.street_address_2

            if street_address is not None:
                street_address = street_address.replace("Ste", "Suite")

            city = formatted_addr.city

            state = formatted_addr.state
            if not state:
                state = raw_address.split(",")[-1].strip()

            zip = store["Postcode"]
            country_code = "GB"

            phone = store["Phone"]

            hour_info = store["OpeningTimes"]

            hours_of_operation = hour_info.replace("|", "; ").strip("; ")

            store_number = store["StoreId"]

            latitude, longitude = store["Latitude"], store["Longitude"]
            if latitude == longitude:
                latitude = longitude = "<MISSING>"

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

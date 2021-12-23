# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json
from sgpostal import sgpostal as parser

website = "pizza-hut.am"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "authority": "apis.bonee.net",
    "sec-ch-ua": '"Google Chrome";v="95", "Chromium";v="95", ";Not A Brand";v="99"',
    "teamreferer": "pizza-hut.am",
    "x-requestid": "2382eff1-5c71-4882-902c-6b1186705e3a",
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
    "accept": "application/json, text/plain, */*",
    "clienttoken": "SpjtW1IZ0HrXkwUvlD1u4IJ245HV5/+rmFkcrHWB7f2b8RbQ4ssev//5UzKx+zUnYjIzYjIwYTJjODMzNDA4NQ==",
    "sec-ch-ua-platform": '"Windows"',
    "origin": "https://pizza-hut.am",
    "sec-fetch-site": "cross-site",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "referer": "https://pizza-hut.am/",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here
    search_url = "https://apis.bonee.net/partner/api/v1/Partner/GetInfo"
    with SgRequests(verify_ssl=False) as session:
        search_res = session.get(search_url, headers=headers)
        json_data = json.loads(search_res.text)
        stores = json_data["relevantLocations"]

        for store in stores:

            page_url = "https://pizza-hut.am/#/about"
            locator_domain = website
            location_name = "PIZZA HUT"
            raw_address = store["relevantText"]
            formatted_addr = parser.parse_address_intl(raw_address)
            street_address = formatted_addr.street_address_1
            if formatted_addr.street_address_2:
                street_address = street_address + ", " + formatted_addr.street_address_2

            city = formatted_addr.city
            state = formatted_addr.state
            zip = formatted_addr.postcode

            country_code = "AM"

            phone = json_data["phoneNumbers"][0]
            store_number = store["$id"]
            location_type = "<MISSING>"
            hours_list = []
            hours = json_data["workDays"]
            for hour in hours:
                day = hour["day"]
                time = hour["start"] + " - " + hour["end"]
                hours_list.append(day + ": " + time)

            hours_of_operation = "; ".join(hours_list).strip()
            latitude, longitude = store["latitude"], store["longitude"]

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

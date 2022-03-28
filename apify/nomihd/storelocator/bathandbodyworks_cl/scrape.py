# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
import json
from sgpostal import sgpostal as parser
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "bathandbodyworks.cl"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "sec-ch-ua": '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
    "sec-ch-ua-mobile": "?0",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
}


def fetch_data():
    # Your scraper here

    search_url = "https://www.bathandbodyworks.cl/tiendas"
    api_url = "https://www.bathandbodyworks.cl/api/dataentities/TV/search?_where=region%20is%20not%20null&_fields=municipality,region,latitude,longitude,schedule,phone,direction,name,regionshortname"

    with SgRequests(dont_retry_status_codes=([404])) as session:
        api_res = session.get(api_url, headers=headers)
        json_res = json.loads(api_res.text)
        stores = json_res

        for store in stores:

            page_url = search_url

            location_name = store["name"]
            location_type = "<MISSING>"

            locator_domain = website
            raw_address = store["direction"]

            formatted_addr = parser.parse_address_intl(raw_address)
            street_address = formatted_addr.street_address_1
            if formatted_addr.street_address_2:
                street_address = street_address + ", " + formatted_addr.street_address_2

            if street_address is not None:
                street_address = street_address.replace("Ste", "Suite")

            city = formatted_addr.city
            if not city:
                city = store["municipality"]
            state = formatted_addr.state
            if not state:
                state = store["region"]
            zip = formatted_addr.postcode

            country_code = "CL"

            store_number = "<MISSING>"

            phone = store["phone"]

            hours_of_operation = store["schedule"].replace(" / ", "; ").strip()
            if "Temporarily Closed" in hours_of_operation:
                location_type = "Temporarily Closed"
                hours_of_operation = "<MISSING>"

            latitude, longitude = (
                store["latitude"],
                store["longitude"],
            )

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
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.GeoSpatialId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()

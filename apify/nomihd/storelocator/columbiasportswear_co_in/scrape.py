# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json
from sgpostal import sgpostal as parser

website = "columbiasportswear.co.in"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "Connection": "keep-alive",
    "sec-ch-ua": '"Google Chrome";v="95", "Chromium";v="95", ";Not A Brand";v="99"',
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "X-Requested-With": "XMLHttpRequest",
    "sec-ch-ua-mobile": "?0",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
    "sec-ch-ua-platform": '"Windows"',
    "Origin": "https://columbiasportswear.co.in",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Dest": "empty",
    "Referer": "https://columbiasportswear.co.in/store-locator",
    "Accept-Language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here

    search_url = "https://columbiasportswear.co.in/store-locator"

    with SgRequests(dont_retry_status_codes=([404])) as session:
        data = {"region": "", "searchtype": "exclusive"}

        search_res = session.post(
            "https://columbiasportswear.co.in/storelocator/storelocator/advancesearch",
            headers=headers,
            data=data,
        )

        stores = json.loads(search_res.text)

        for store in stores:

            page_url = search_url

            locator_domain = website

            location_name = (
                store["store_name"]
                .encode("ascii", "replace")
                .decode("utf-8")
                .replace("?", "-")
                .strip()
            )
            if "," == location_name[-1]:
                location_name = "".join(location_name[:-1]).strip()

            raw_address = (
                store["address"]
                .encode("ascii", "replace")
                .decode("utf-8")
                .replace("?", "-")
                .strip()
            )

            formatted_addr = parser.parse_address_intl(raw_address)
            street_address = formatted_addr.street_address_1
            if formatted_addr.street_address_2:
                street_address = street_address + ", " + formatted_addr.street_address_2

            city = store["city"].split("-")[0].strip()
            if len(city) <= 0:
                if "," in location_name:
                    city = location_name.split(",")[-1].strip()
                elif "-" in location_name:
                    city = location_name.split("-")[-1].strip()

            state = store["region"] + " " + store["state"]
            zip = store["pin_code"]
            if len(zip) <= 0:
                if "-" in raw_address:
                    zip = raw_address.split("-")[-1].strip()
                else:
                    zip = raw_address.split(" ")[-1].strip()

            if not zip.isdigit():
                zip = "<MISSING>"

            country_code = "IN"

            store_number = store["store_id"]

            phone = store["contact_number"]

            location_type = "<MISSING>"
            hours_of_operation = "<MISSING>"
            latitude, longitude = (
                store["lat_long"].split(",")[0].strip(),
                store["lat_long"].split(",")[-1].strip(),
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

# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
import json
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal import sgpostal as parser

website = "jbhifi.com.au"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "Connection": "keep-alive",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="98", "Google Chrome";v="98"',
    "x-algolia-application-id": "VTVKM5URPX",
    "content-type": "application/x-www-form-urlencoded",
    "x-algolia-api-key": "a0c0108d737ad5ab54a0e2da900bf040",
    "sec-ch-ua-mobile": "?0",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.82 Safari/537.36",
    "sec-ch-ua-platform": '"Windows"',
    "Accept": "*/*",
    "Origin": "https://www.jbhifi.com.au",
    "Sec-Fetch-Site": "cross-site",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Dest": "empty",
    "Referer": "https://www.jbhifi.com.au/",
    "Accept-Language": "en-US,en-GB;q=0.9,en;q=0.8",
}

params = (("x-algolia-agent", "Algolia for JavaScript (4.12.0); Browser"),)

data = '{"query":"","hitsPerPage":1000,"filters":"displayOnWeb:p"}'


def fetch_data():
    # Your scraper here
    search_url = (
        "https://vtvkm5urpx-1.algolianet.com/1/indexes/shopify_store_locations/query"
    )
    with SgRequests() as session:
        stores_req = session.post(search_url, headers=headers, params=params, data=data)
        stores = json.loads(stores_req.text)["hits"]

        for store in stores:
            store_number = store["shopId"]
            locator_domain = website
            location_name = store["storeName"].strip()

            page_url = (
                "https://www.jbhifi.com.au/pages/"
                + location_name.replace(" ", "-").strip()
            )

            page_url = page_url.replace("---", "-").strip()
            raw_address = store["storeAddress"]["Line1"]
            add_2 = store["storeAddress"]["Line2"]
            add_3 = store["storeAddress"]["Line3"]

            if add_2 is not None and len(add_2) > 0:
                raw_address = raw_address + ", " + add_2

            if add_3 is not None and len(add_3) > 0:
                raw_address = raw_address + ", " + add_3

            raw_address = raw_address.replace(", ,", ",").strip()

            city = store["storeAddress"]["Suburb"]
            if len(city) > 0:
                raw_address = raw_address + ", " + city

            state = store["storeAddress"]["State"]
            if len(state) > 0:
                raw_address = raw_address + ", " + state

            zip = store["storeAddress"]["Postcode"]
            if len(zip) > 0:
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
            country_code = "AU"
            phone = store.get("phone", "<MISSING>")

            location_type = "<MISSING>"

            latitude = store["_geoloc"]["lat"]
            longitude = store["_geoloc"]["lng"]

            hours_of_operation = "<MISSING>"
            hours = store["normalTradingHours"]
            hours_list = []
            for hour in hours:
                if hour["DayOfWeek"] == 0:
                    day = "Sunday:"
                if hour["DayOfWeek"] == 1:
                    day = "Monday:"
                if hour["DayOfWeek"] == 2:
                    day = "Tuesday:"
                if hour["DayOfWeek"] == 3:
                    day = "Wednesday:"
                if hour["DayOfWeek"] == 4:
                    day = "Thursday:"
                if hour["DayOfWeek"] == 5:
                    day = "Friday:"
                if hour["DayOfWeek"] == 6:
                    day = "Saturday:"

                if hour["IsOpen"] is False:
                    time = "Closed"
                else:
                    time = hour["OpeningTime"] + " - " + hour["ClosingTime"]

                hours_list.append(day + time)

            hours_of_operation = "; ".join(hours_list).strip()

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

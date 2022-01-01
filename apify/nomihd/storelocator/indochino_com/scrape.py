# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json

website = "indochino.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "authority": "www.indochino.com",
    "cache-control": "max-age=0",
    "sec-ch-ua": '"Google Chrome";v="95", "Chromium";v="95", ";Not A Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "none",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here

    with SgRequests(dont_retry_status_codes=([404])) as session:
        search_url = "https://www.indochino.com/showrooms"
        search_res = session.get(search_url, headers=headers)
        stores_dict = json.loads(
            search_res.text.split("var showroomsByState = ")[1]
            .strip()
            .split("}]};")[0]
            .strip()
            + "}]}"
        )

        for state in stores_dict.keys():
            stores = stores_dict[state]
            for store in stores:
                page_url = "https://www.indochino.com/showroom/" + store["UrlKey"]

                locator_domain = website

                location_name = store["Name"]
                if "Virtual" in location_name:
                    continue
                street_address = (
                    store["Address"]["Address1"]
                    .replace("<br>", "")
                    .strip()
                    .replace("\n", ", ")
                    .strip()
                )
                if store["Address"]["Address2"]:
                    street_address = (
                        street_address
                        + ", "
                        + store["Address"]["Address2"]
                        .replace("<br>", "")
                        .strip()
                        .replace("\n", ", ")
                        .strip()
                    )

                city_state = store["Address"]["City"]
                city = city_state.split(",")[0].strip()
                state = store["State"]
                zip = "<MISSING>"

                country_code = store["Country"]
                store_number = store["StoreId"]
                phone = "<MISSING>"
                try:
                    phone = store["Phones"][0]["PhoneNumber"]
                except:
                    pass

                location_type = store["LocationTypeName"]
                hours_of_operation = (
                    store["Hours"]
                    .replace("<br>", "")
                    .strip()
                    .replace("\n", "; ")
                    .strip()
                )

                latitude, longitude = store["Latitude"], store["Longitude"]

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

# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "day-today.co.uk"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "authority": "www.day-today.co.uk",
    "sec-ch-ua": '" Not;A Brand";v="99", "Google Chrome";v="97", "Chromium";v="97"',
    "accept": "*/*",
    "x-requested-with": "XMLHttpRequest",
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "referer": "https://www.day-today.co.uk/shops/",
    "accept-language": "en-US,en;q=0.9,ar;q=0.8",
}

params = (
    ("action", "store_search"),
    ("lat", "55.864237"),
    ("lng", "-4.251806"),
    ("max_results", "25"),
    ("search_radius", "5"),
    ("filter", "26,28,27"),
    ("autoload", "1"),
)


def fetch_data():
    # Your scraper here

    api_url = "https://www.day-today.co.uk/wp-admin/admin-ajax.php"

    with SgRequests() as session:
        api_res = session.get(api_url, headers=headers, params=params)

        json_res = json.loads(api_res.text)
        stores = json_res

        for no, store in enumerate(stores, 1):

            locator_domain = website

            page_url = store["url"]
            if not page_url:
                page_url = "https://www.day-today.co.uk/shops/"

            location_name = store["store"].strip()

            location_type = "<MISSING>"

            raw_address = "<MISSING>"

            street_address = store["address"].strip()
            if store["address2"]:
                street_address = (street_address + ", " + store["address2"]).strip(", ")

            if street_address is not None:
                street_address = street_address.replace("Ste", "Suite")

            city = store["city"]

            state = store["state"]

            zip = store["zip"]

            country_code = store["country"]

            phone = store["phone"]

            hours_str = store["hours"]
            hour_sel = lxml.html.fromstring(hours_str)

            hours = list(
                filter(
                    str,
                    [x.strip() for x in hour_sel.xpath("//table//text()")],
                )
            )
            hours_of_operation = (
                "; ".join(hours)
                .replace("day; ", "day: ")
                .replace("day:;", "day:")
                .replace("OPEN FOR BUSINESS!", "")
                .replace("NOW OPEN!", "")
                .strip(";! ")
            )

            store_number = store["id"]

            latitude, longitude = store["lat"], store["lng"]
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

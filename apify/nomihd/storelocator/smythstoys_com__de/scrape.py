# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
import json
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "smythstoys.com/de"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "authority": "www.smythstoys.com",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
    "accept": "*/*",
    "x-requested-with": "XMLHttpRequest",
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "referer": "https://www.smythstoys.com/de/de-de/store-finder",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.smythstoys.com/de/de-de/store-finder/getAllStores"
    with SgRequests(dont_retry_status_codes=([404])) as session:
        session.get("https://www.smythstoys.com/de/de-de/", headers=headers)
        stores_req = session.get(search_url, headers=headers)
        json_text = stores_req.text.strip()
        regions = json.loads(json_text, strict=False)["data"]
        for region in regions:
            stores = region["regionPos"]
            for store in stores:
                page_url = "https://www.smythstoys.com/de/de-de/store-finder"

                locator_domain = website
                location_name = store["displayName"]
                street_address = store["line1"]
                if store["line2"] is not None:
                    street_address = street_address + ", " + store["line2"]

                if store["line3"] is not None:
                    street_address = street_address + ", " + store["line3"]

                street_address = street_address.replace(", ,", "").strip()
                if "," in street_address[-1]:
                    street_address = "".join(street_address[:-1])
                city = store["town"]
                state = region["regionName"]
                zip = store["postalCode"]

                country_code = store["country"]

                store_number = "<MISSING>"
                phone = store["phone"]

                location_type = "<MISSING>"

                latitude = store["latitude"]
                longitude = store["longitude"]

                hours = store["openings"]
                hours_list = []
                if isinstance(hours, dict):
                    for day in hours.keys():
                        time = hours[day]
                        hours_list.append(day + ":" + time)

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
                )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.CITY,
                    SgRecord.Headers.STATE,
                    SgRecord.Headers.ZIP,
                }
            )
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()

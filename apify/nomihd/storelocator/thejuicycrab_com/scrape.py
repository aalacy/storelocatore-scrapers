# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


website = "thejuicycrab.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "authority": "thejuicycrab.com",
    "sec-ch-ua": '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
    "accept": "application/json, text/javascript, */*; q=0.01",
    "x-requested-with": "XMLHttpRequest",
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36",
    "content-type": "application/json",
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "accept-language": "en-US,en;q=0.9,ar;q=0.8",
}


def fetch_data():
    # Your scraper here

    search_url = "https://thejuicycrab.com/locations/"
    search_res = session.get(search_url, headers=headers)

    json_str = (
        search_res.text.split("var _items = ")[1]
        .split("</script>")[0]
        .strip()
        .strip(";]")
        .strip()
        .strip(",")
        .strip()
    ) + "]"

    json_res = json.loads(json_str)

    store_list = json_res

    for store in store_list:

        page_url = search_url

        locator_domain = website

        street_address = (store["address"] + "," + store["suite"]).strip(", ").strip()

        city = store["city"].strip()
        state = store["state"].strip()
        zip = store["zipCode"].strip()

        country_code = "US"

        location_name = store["name"].strip()

        if "COMING SOON" in location_name:
            continue
        phone = store["phone"]
        if phone and "," in phone:
            phone = phone.split(",")[0].strip()

        store_number = "<MISSING>"

        location_type = "<MISSING>"

        hours_of_operation = "<MISSING>"

        latitude, longitude = (
            store["latitude"],
            store["longitude"],
        )
        raw_address = "<MISSING>"

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

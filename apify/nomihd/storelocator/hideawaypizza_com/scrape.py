# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json

website = "hideawaypizza.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "sec-ch-ua": '"Google Chrome";v="93", " Not;A Brand";v="99", "Chromium";v="93"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36",
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.hideawaypizza.com/locations"
    search_res = session.get(search_url, headers=headers)

    store_list = json.loads(
        search_res.text.split("locations = ")[1].strip().split("}];")[0].strip() + "}]"
    )

    for store in store_list:
        if store["customContent"]["ComingSoon"]:
            continue
        page_url = "https://www.hideawaypizza.com" + store["fullUrl"]
        locator_domain = website
        location_name = store["customContent"]["locationName"]

        street_address = store["location"]["addressLine1"]
        city_state_zip = store["location"]["addressLine2"]
        city = city_state_zip.split(",")[0].strip()
        state = city_state_zip.split(",")[-1].strip().split(" ")[0].strip()
        zip = city_state_zip.split(",")[-1].strip().split(" ")[-1].strip()

        country_code = "US"

        store_number = "<MISSING>"

        location_type = "<MISSING>"
        phone = store["customContent"]["phone"]
        hours_of_operation = ""
        hours_list = []
        if (
            store["customContent"]["weekdayHours"]
            and len(store["customContent"]["weekdayHours"]) > 0
        ):
            hours_list.append("Sun - Thur: " + store["customContent"]["weekdayHours"])

        if (
            store["customContent"]["weekendHours"]
            and len(store["customContent"]["weekendHours"]) > 0
        ):
            hours_list.append("Fri & Sat: " + store["customContent"]["weekendHours"])

        hours_of_operation = "; ".join(hours_list).strip()
        latitude, longitude = (
            str(store["location"]["markerLat"]),
            str(store["location"]["markerLng"]),
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
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PageUrlId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()

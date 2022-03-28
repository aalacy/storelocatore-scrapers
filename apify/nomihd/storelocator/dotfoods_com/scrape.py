# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json

website = "dotfoods.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()

headers = {
    "authority": "www.dotfoods.com",
    "cache-control": "max-age=0",
    "sec-ch-ua": '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
    "sec-ch-ua-mobile": "?0",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "cross-site",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here

    search_url = "https://www.dotfoods.com/about/locations/"
    stores_req = session.get(search_url, headers=headers)
    stores = json.loads(
        stores_req.text.split('<interactive-map :model="')[1]
        .strip()
        .split('"></interactive-map>')[0]
        .strip()
        .replace("&quot;", '"')
        .strip()
    )["PoiList"]

    for store in stores:

        page_url = search_url

        location_name = store["Title"]
        log.info(location_name)
        location_type = store["Subtitle"]
        locator_domain = website

        if "Coming Soon" in store["DescLine1"]:
            continue
        if "Canada" in location_type:
            street_address = store["DescLine1"]
            city_state = store["DescLine2"]
            city = city_state.strip().split(",")[0].strip()
            state = city_state.split(",")[-1].strip()
            zip = store["DescLine3"]
            phone = store["DescLine4"].replace("Phone:", "").strip()
            country_code = "CA"

        else:
            street_address = store["DescLine1"]
            city_state_zip = store["DescLine2"]
            city = city_state_zip.strip().split(",")[0].strip()
            state = city_state_zip.split(",")[-1].strip().split(" ")[0].strip()
            zip = city_state_zip.split(",")[-1].strip().split(" ")[-1].strip()
            phone = store["DescLine3"].replace("Phone:", "").strip()

            country_code = "US"

        store_number = "<MISSING>"

        hours_of_operation = "<MISSING>"

        latitude = store["Latitude"]
        longitude = store["Longitude"]

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

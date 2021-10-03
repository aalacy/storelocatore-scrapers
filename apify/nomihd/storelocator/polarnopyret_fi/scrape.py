# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "polarnopyret.fi"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "authority": "www.polarnopyret.fi",
    "sec-ch-ua": '"Chromium";v="94", "Google Chrome";v="94", ";Not A Brand";v="99"',
    "x-client-version": "44.10.0",
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36",
    "content-type": "application/json",
    "x-includeappshelldata": "true",
    "x-requested-with": "XMLHttpRequest",
    "x-resolvedynamicdata": "true",
    "sec-ch-ua-platform": '"Windows"',
    "accept": "*/*",
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "referer": "https://www.polarnopyret.fi/myymalat",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here

    with SgRequests(dont_retry_status_codes=([404])) as session:
        stores_req = session.get(
            "https://www.polarnopyret.fi/myymalat", headers=headers
        )
        stores = stores_req.json()["stores"]
        for store in stores:
            page_url = "https://www.polarnopyret.fi/myymalat"
            locator_domain = website
            location_name = store["name"]

            phone = store["phoneNumber"]
            street_address = store["street"]
            city = store["city"]
            state = "<MISSING>"
            zip = store["postalCode"]
            country_code = "FI"

            store_number = "<MISSING>"
            location_type = "<MISSING>"
            hours_list = []
            if store["openingHoursMonThruFri"]:
                hours_list.append("Mon - Fri: " + store["openingHoursMonThruFri"])

            if store["openingHoursSat"]:
                hours_list.append("Sat: " + store["openingHoursMonThruFri"])

            if store["openingHoursSun"]:
                hours_list.append("Sun: " + store["openingHoursMonThruFri"])

            hours_of_operation = "; ".join(hours_list).strip()

            latitude = store["latitude"]
            longitude = store["longitude"]

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

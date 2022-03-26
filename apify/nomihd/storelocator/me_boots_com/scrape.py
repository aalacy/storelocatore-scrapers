# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json

website = "me.boots.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "authority": "me.boots.com",
    "sec-ch-ua": '"Chromium";v="94", "Google Chrome";v="94", ";Not A Brand";v="99"',
    "accept": "application/json",
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}

params = (
    ("country", "OM"),
    ("qp", ""),
    ("l", "en"),
)


def fetch_data():
    # Your scraper here

    stores_req = session.get(
        "https://me.boots.com/search", headers=headers, params=params
    )
    stores = json.loads(stores_req.text)["response"]["entities"]
    for store in stores:
        store_number = "<MISSING>"
        location_name = "Boots " + store["profile"]["address"]["line1"]
        page_url = store["profile"]["c_baseURL"]

        location_type = "<MISSING>"
        locator_domain = website

        street_address = store["profile"]["address"]["line2"]
        city = store["profile"]["address"]["city"]
        state = store["profile"]["address"]["region"]
        zip = store["profile"]["address"]["postalCode"]
        country_code = store["profile"]["address"]["countryCode"]

        phone = store["profile"]["mainPhone"]["display"]

        hours_list = []
        hours = store["profile"]["hours"]["normalHours"]
        for hour in hours:
            day = hour["day"]
            start = str(hour["intervals"][0]["start"])
            end = str(hour["intervals"][0]["end"])
            if hour["isClosed"] is False:
                time = start[:2] + ":" + start[2:] + " - " + end[:2] + ":" + end[2:]
            else:
                time = "Closed"

            hours_list.append(day + ":" + time)

        hours_of_operation = "; ".join(hours_list).strip()

        latitude = store["profile"]["yextDisplayCoordinate"]["lat"]
        longitude = store["profile"]["yextDisplayCoordinate"]["long"]

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

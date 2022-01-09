# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json
import lxml.html

website = "pizzahut.co.th"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()


def fetch_data():
    # Your scraper here
    csrf_token = "".join(
        lxml.html.fromstring(
            session.get("https://www.pizzahut.co.th/location").text
        ).xpath('//meta[@name="csrf-token"]/@content')
    ).strip()
    headers = {
        "authority": "www.pizzahut.co.th",
        "sec-ch-ua": '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
        "accept": "*/*",
        "x-csrf-token": csrf_token,
        "x-requested-with": "XMLHttpRequest",
        "sec-ch-ua-mobile": "?0",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        "sec-fetch-site": "same-origin",
        "sec-fetch-mode": "cors",
        "sec-fetch-dest": "empty",
        "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
    }

    data = {"store_location": ""}

    stores_req = session.post(
        "https://www.pizzahut.co.th/location-get-stores-by-search",
        headers=headers,
        data=data,
    )

    data = json.loads(stores_req.text)["data"].replace('"', '"').replace("\\\\u", "\\u")
    stores = json.loads(data)
    for store in stores:
        page_url = "<MISSING>"
        location_name = store["store_name"]
        location_type = "<MISSING>"
        locator_domain = website
        city = store["store_district"]
        state = store["store_province"]
        zip = store["postcode"]
        street_address = store["store_address"]
        if zip:
            street_address = street_address.replace(zip, "").strip()

        if state:
            street_address = street_address.replace(state, "").strip()

        if city:
            street_address = street_address.replace(city, "").strip()

        country_code = "TH"
        store_number = store["store_code"]
        phone = store["phone"]

        hours_of_operation = "<MISSING>"
        if store["delivery_start"] and store["delivery_end"]:
            hours_of_operation = store["delivery_start"] + " - " + store["delivery_end"]

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

# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json

website = "rodeomexicangrill.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "authority": "www.rodeomexicangrill.com",
    "sec-ch-ua": '"Chromium";v="88", "Google Chrome";v="88", ";Not A Brand";v="99"',
    "accept": "*/*",
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36",
    "content-type": "application/json",
    "origin": "https://www.rodeomexicangrill.com",
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "referer": "https://www.rodeomexicangrill.com/",
    "accept-language": "en-US,en;q=0.9",
}


def fetch_data():
    # Your scraper here

    data = '{"operationName":"restaurantWithLocations","variables":{"restaurantId":4328},"extensions":{"operationId":"PopmenuClient/1314972022f7e2b12673700232e6be54"}}'

    stores_req = session.post(
        "https://www.rodeomexicangrill.com/graphql", headers=headers, data=data
    )
    stores = json.loads(stores_req.text)["data"]["restaurant"]["locations"]

    for store in stores:
        page_url = "https://www.rodeomexicangrill.com/"
        location_type = "<MISSING>"
        if store["isLocationClosed"] is True:
            location_type = "Closed"
        locator_domain = website
        location_name = store["name"]
        street_address = store["streetAddress"]
        city = store["city"]
        state = store["state"]
        zip = store["postalCode"]
        country_code = store["country"]
        phone = store["phone"]
        hours_of_operation = "<MISSING>"
        if store["schemaHours"] is not None:
            hours_of_operation = "; ".join(store["schemaHours"])

        store_number = str(store["restaurantId"])

        latitude = store["lat"]
        longitude = store["lng"]

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
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()

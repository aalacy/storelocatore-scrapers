# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
import json
import lxml.html
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import us

website = "americansale.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.americansale.com/apps/store-locator/stores-api"
    stores_req = session.get(search_url, headers=headers)
    stores = json.loads(stores_req.text)["data"]

    for store in stores:
        page_url = "https://www.americansale.com/pages/" + store["shopify_handle"]
        locator_domain = website
        location_name = store["name"]
        if location_name == "CORPORATE OFFICE" or location_name == "WEBSITE":
            continue
        street_address = store["address1"]
        if store["address2"] is not None and len(store["address2"]) > 0:
            street_address = street_address + ", " + store["address2"]

        city = store["city"]
        state = store["state"]
        zip = store["zipcode"]

        country_code = "<MISSING>"
        if us.states.lookup(state):
            country_code = "US"

        store_number = str(store["id"])
        phone = store["phone_number"]

        location_type = "<MISSING>"
        hours_list = []
        if store["store_hours"] is not None and len(store["store_hours"]) > 0:
            hours = (
                "".join(lxml.html.fromstring(store["store_hours"]).xpath("//p//text()"))
                .strip()
                .split("\n")
            )
            hours_list = []
            hours_of_operation = ""
            for hour in hours:
                if len("".join(hour).strip()) > 0:
                    hours_list.append("".join(hour).strip())

        hours_of_operation = "; ".join(hours_list).strip()
        if "Customer Service Hours" in hours_of_operation:
            hours_of_operation = (
                hours_of_operation.split("Customer Service Hours")[1]
                .strip()
                .replace("; Closed on major holidays", "")
                .strip()
            )

        if "Any time, anywhere!" in hours_of_operation:
            hours_of_operation = "<MISSING>"

        latitude = store["latitude"]
        longitude = store["longtitude"]

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

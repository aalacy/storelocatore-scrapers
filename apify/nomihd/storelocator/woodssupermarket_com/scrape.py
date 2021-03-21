# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
import json
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter

website = "woodssupermarket.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    # Your scraper here
    search_url = "https://api.freshop.com/1/stores?app_key=woods"
    stores_req = session.get(search_url, headers=headers)
    stores = json.loads(stores_req.text)["items"]

    for index in range(1, len(stores) - 1):
        page_url = "<MISSING>"
        if "url" in stores[index]:
            page_url = stores[index]["url"]
        locator_domain = website
        location_name = stores[index]["name"]
        street_address = stores[index]["address_1"]

        city = stores[index]["city"]
        state = stores[index]["state"]
        zip = stores[index]["postal_code"]

        country_code = "US"

        store_number = "<MISSING>"
        if "store_number" in stores[index]:
            store_number = stores[index]["store_number"]

        phone = "<MISSING>"
        if "phone" in stores[index]:
            phone = stores[index]["phone"]
            if "- Main" in phone:
                phone = phone.split("- Main")[0].strip()

        location_type = stores[index]["legal_name"]

        hours_of_operation = "<MISSING>"
        if "hours" in stores[index]:
            if stores[index]["hours"] is not None and len(stores[index]["hours"]) > 0:
                hours_of_operation = stores[index]["hours"]
                if "*Pharmacy*" in hours_of_operation:
                    hours_of_operation = hours_of_operation.split("*Pharmacy*")[
                        0
                    ].strip()

        else:
            if "hours_md" in stores[index]:
                if (
                    stores[index]["hours_md"] is not None
                    and len(stores[index]["hours_md"]) > 0
                ):
                    hours_of_operation = stores[index]["hours_md"]
                    if "*Pharmacy*" in hours_of_operation:
                        hours_of_operation = hours_of_operation.split("*Pharmacy*")[
                            0
                        ].strip()

        hours_of_operation = "; ".join(hours_of_operation.split("\n")).strip()

        latitude = stores[index]["latitude"]
        longitude = stores[index]["longitude"]

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

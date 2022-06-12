# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
import json
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html

website = "mitchellsfishmarket.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.mitchellsfishmarket.com/locations-and-menus/"
    stores_req = session.get(search_url, headers=headers)
    stores = json.loads(
        "["
        + stores_req.text.split("locations: [")[1].strip().split("}}],")[0].strip()
        + "}}]"
    )

    for store in stores:
        page_url = "https://www.mitchellsfishmarket.com" + store["url"]
        locator_domain = website
        location_name = store["name"]
        street_address = store["street"]
        city = store["city"]
        state = store["state"]
        zip = store["postal_code"]

        country_code = "US"

        store_number = store["id"]
        phone = store["phone_number"]
        location_type = "<MISSING>"

        hours_list = []
        hours_sel = lxml.html.fromstring(store["hours"])
        hours = hours_sel.xpath("//p[1]/text()")
        for hour in hours:
            if len("".join(hour).strip()) > 0:
                hours_list.append("".join(hour).strip())

        hours_of_operation = (
            "; ".join(hours_list)
            .strip()
            .encode("ascii", "replace")
            .decode("utf-8")
            .replace("?", "-")
            .strip()
        )

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

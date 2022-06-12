# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json


website = "viefit.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "accept": "application/json, text/plain, */*",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36",
}


def fetch_data():
    # Your scraper here

    search_url = "https://viefit.com/contact-vie/"
    search_res = session.get(search_url, headers=headers)

    json_res = json.loads(
        search_res.text.split('<script type="application/ld+json">')[1]
        .split("</script>")[0]
        .strip()
    )

    stores_list = json_res["@graph"]

    for store in stores_list:

        if store["@type"] == "Organization":
            continue

        page_url = "https://viefit.com/contact-vie/"
        locator_domain = website

        location_name = (
            store["description"].split(" location")[0].split(" is located")[0].strip()
        )

        street_address = store["address"]["streetAddress"].strip()

        city = store["address"]["addressLocality"].strip()
        state = store["address"]["addressRegion"].strip()

        zip = store["address"]["postalCode"].strip()

        country_code = "US"
        store_number = "<MISSING>"

        phone = store["address"]["telephone"].strip()

        location_type = "<MISSING>"

        hours = store["openingHours"]
        hours_of_operation = "; ".join(hours).strip()
        latitude = store["geo"]["latitude"]
        longitude = store["geo"]["longitude"]

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
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()

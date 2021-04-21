# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json
import lxml.html

website = "fajitapetes.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    # Your scraper here
    search_url = "https://fajitapetes.com/wp-admin/admin-ajax.php?action=store_search&lat=29.76043&lng=-95.3698&max_results=50000&search_radius=50000&autoload=1"
    stores_req = session.get(search_url, headers=headers)
    stores = json.loads(stores_req.text)
    for store in stores:
        page_url = store["permalink"]
        if store["coming_soon"] == "1":
            continue
        locator_domain = website
        location_name = store["store"]
        street_address = store["address"]
        if (
            "address2" in store
            and store["address2"] is not None
            and len(store["address2"]) > 0
        ):
            street_address = street_address + ", " + store["address2"]

        city = store["city"]
        if city[-1] == ",":
            city = "".join(city[:-1]).strip()

        state = store["state"]
        zip = store["zip"]
        country_code = store["country"]

        phone = store["phone"]

        store_number = store["id"]
        location_type = "<MISSING>"

        log.info(page_url)
        store_req = session.get(page_url, headers=headers)
        hours_of_operation = ""
        try:
            hours_sel = lxml.html.fromstring(
                store_req.text.split("<h2>HOURS</h2>")[1]
                .strip()
                .split("<hr")[0]
                .strip()
            )
            hours_of_operation = (
                " ".join(" ".join(hours_sel.xpath("//p//text()")).strip().split("\n"))
                .strip()
                .replace("Starting Tuesday, March 23, 2021:", "")
                .strip()
            )
            try:
                hours_of_operation = hours_of_operation.split("913-361-7700")[0].strip()
            except:
                pass
        except:
            pass

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

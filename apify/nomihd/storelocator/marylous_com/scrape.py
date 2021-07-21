# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json
import lxml.html

website = "marylous.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "accept": "application/json, text/plain, */*",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36",
}


def fetch_data():
    # Your scraper here
    api_url = "https://marylous.com/wp-admin/admin-ajax.php?action=store_search&lat=42.24182&lng=-70.88976&max_results=1000&search_radius=50000&autoload=1"
    api_res = session.get(api_url, headers=headers)
    json_res = json.loads(api_res.text)

    stores_list = json_res
    for store in stores_list:

        page_url = "https://marylous.com/find-a-marylous/"

        locator_domain = website
        location_name = store["store"].strip().replace("&#8211;", "-").strip()
        street_address = store["address"].strip()
        city = store["city"].strip()
        state = store["state"].strip()
        zip = store["zip"].strip()
        country_code = "US"

        store_number = store["id"]
        phone = store["phone"].strip()

        location_type = "<MISSING>"

        store_hours = store["hours"]
        if store_hours:
            hours_list = []

            hours_sel = lxml.html.fromstring(store_hours)

            day_time_list = hours_sel.xpath("//tr")

            for day_time in day_time_list:
                hours_list.append(": ".join(day_time.xpath(".//text()")))

            hours_of_operation = "; ".join(hours_list)
        else:
            hours_of_operation = "<MISSING>"

        latitude = store["lat"]
        longitude = store["lng"]

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

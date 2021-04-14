# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
import json


website = "creamnation.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "accept": "application/json, text/plain, */*",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36",
}


def fetch_data():
    # Your scraper here
    api_url = "https://creamnation.com/wp-admin/admin-ajax.php?action=store_search&lat=37.09024&lng=-95.712891&max_results=1000&search_radius=5000&autoload=1"
    api_res = session.get(api_url, headers=headers)

    json_res = json.loads(api_res.text)

    stores_list = json_res

    for store in stores_list:

        page_url = store["permalink"].strip()
        locator_domain = website

        location_name = store["store"].strip()

        street_address = store["address"].strip()
        if "address2" in store and store["address2"].strip():
            street_address = street_address + " " + store["address2"].strip()

        city = store["city"].strip()
        state = store["state"].strip()
        zip = store["zip"].strip()

        country_code = "US"
        store_number = store["id"].strip()

        phone = store["phone"].strip()

        location_type = "<MISSING>"

        if store["hours"]:
            hours = store["hours"]

            hours_list = []
            hours_sel = lxml.html.fromstring(hours).xpath("//tr")
            for hour in hours_sel:
                hour_info = list(filter(str, hour.xpath(".//text()")))
                day = hour_info[0].strip()
                hrs = (
                    "".join(hour_info[1:]).replace("\n", " ").replace("  ", " ").strip()
                )
                hours_list.append(f"{day}: {hrs}")

            hours_of_operation = "; ".join(hours_list)
        else:
            hours_of_operation = "<MISSING>"
        latitude = store["lat"].strip()
        longitude = store["lng"].strip()

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

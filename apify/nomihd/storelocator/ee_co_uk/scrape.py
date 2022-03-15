# -*- coding: utf-8 -*-
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sglogging import sglog
import json

website = "ee.co.uk"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests(retry_behavior=None, proxy_rotation_failure_threshold=0)
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    # Your scraper here
    search_url = "https://ee.co.uk/stores/england.stores.html"
    stores_req = session.get(search_url, headers=headers)
    stores = json.loads(stores_req.text)["storesJson"]

    for store in stores:
        page_url = (
            "https://ee.co.uk"
            + store["path"].replace("/content/ee-web/en_GB", "").strip()
        )

        log.info(page_url)
        store_req = session.get(
            "https://storefinder.ee.co.uk/rest/v1/shops/" + store["rsid"],
            headers=headers,
        )
        if store_req.status_code == 200:
            store_json = json.loads(store_req.text)["locations"]
            if len(store_json) > 0:
                store_json = store_json[0]["retailshop"]
                locator_domain = website
                location_name = store_json["storename"]
                street_address = store_json["street1"]
                if (
                    "street2" in store_json
                    and store_json["street2"] is not None
                    and len(store_json["street2"]) > 0
                    and store_json["street2"] != "0"
                ):
                    street_address = street_address + ", " + store_json["street2"]

                city = ""
                state = ""
                zip = ""
                country_code = ""

                try:
                    city = store_json["locality1"].strip()
                except:
                    pass
                try:
                    state = store_json["county"].strip()
                except:
                    pass
                try:
                    zip = store_json["postcode"].strip()
                except:
                    pass
                try:
                    country_code = store_json["region"].strip()
                except:
                    pass

                store_number = store_json["rsid"]
                phone = store_json["phone"].strip()

                location_type = store_json["storetype"]

                latitude = store_json["lat"]
                longitude = store_json["lng"]

                hours_of_operation = (
                    store_json["openinghours"]
                    .replace("<b>", "")
                    .replace("</b> ", ":")
                    .replace("<br/>", "; ")
                    .strip()
                    .replace("::", ":")
                    .strip()
                )

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

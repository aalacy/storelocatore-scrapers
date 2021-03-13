# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json

website = "10fitness.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    # Your scraper here

    search_url = "https://www.juicegeneration.com/locations/"
    stores_req = session.get(search_url, headers=headers)
    stores = json.loads(
        stores_req.text.split("locationsJSON = ")[1].strip().split("}};")[0].strip()
        + "}}"
    )

    for store_id in stores.keys():
        page_url = (
            "https://www.juicegeneration.com/locations/" + stores[store_id]["url_path"]
        )
        location_type = "<MISSING>"
        locator_domain = website
        location_name = stores[store_id]["name"]

        street_address = stores[store_id]["address1"]
        if (
            stores[store_id]["address2"] is not None
            and len(stores[store_id]["address2"]) > 0
        ):
            street_address = street_address + ", " + stores[store_id]["address2"]

        city = stores[store_id]["map_location"]
        state = "<MISSING>"
        zip = stores[store_id]["zipcode"]
        country_code = "US"
        phone = stores[store_id]["phone"]
        hours_of_operation = "<MISSING>"
        hours = stores[store_id]["work_hours"]
        hours_list = []
        for key in hours.keys():
            day = hours[key]["day_name"]
            time = hours[key]["start"] + "-" + hours[key]["end"]
            hours_list.append(day + ":" + time)

        hours_of_operation = "; ".join(hours_list).strip()
        store_number = stores[store_id]["location_id"]

        latitude = "<MISSING>"
        longitude = "<MISSING>"

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

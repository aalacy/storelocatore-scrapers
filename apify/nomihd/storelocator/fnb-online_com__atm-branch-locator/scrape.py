# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json

website = "fnb-online.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    # Your scraper here
    search_url = "https://code.metalocator.com/index.php?option=com_locator&view=directory&force_link=1&tmpl=component&task=search_zip&framed=1&format=raw&no_html=1&templ[]=address_format&layout=_jsonfast&postal_code=37.562,-79.069&radius=719&interface_revision=929&user_lat=0&user_lng=0&tags[]=7&Itemid=12578&preview=0&parent_table=&parent_id=0&search_type=point&_opt_out=&ml_location_override=&reset=true&nearest=undefined&national=false&callback=handleJSONPResults"
    stores_req = session.get(search_url, headers=headers)
    stores = json.loads(stores_req.text.split("handleJSONPResults(")[1][0:-2])[
        "results"
    ]
    for store in stores:
        page_url = "https://code.metalocator.com/index.php?option=com_locator&view=location&tmpl=component&task=load&framed=1&format=json&templ[]=map_address_template&sample_data=undefined&lang=&_opt_out=&Itemid=12578&number=432&id={}&distance=&_urlparams="

        store_req = session.get(page_url.format(store["id"]), headers=headers)
        store_json = json.loads(store_req.text)[0]
        locator_domain = website
        location_name = store_json["name"]
        street_address = store_json["address"]
        if (
            "address2" in store_json
            and store_json["address2"] is not None
            and len(store_json["address2"]) > 0
        ):
            street_address = street_address + ", " + store_json["address2"]

        city = store_json["city"]
        state = store_json["state"]
        zip = store_json["postalcode"]
        country_code = store_json["country"]

        phone = store_json["phone"]

        store_number = store_json["id"]
        log.info(f"Fetching data for storeID:{store_number}")
        location_type = store_json["locationtype"]

        hours_of_operation = ""
        if "atmhours" in store_json:
            hours_of_operation = store_json["atmhours"]

        latitude = store_json["lat"]
        longitude = store_json["lng"]

        page_url = store_json["link"]
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

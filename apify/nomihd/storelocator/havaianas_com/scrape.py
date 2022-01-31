# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "havaianas.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36",
}


def fetch_data():
    # Your scraper here

    search_url = "https://us.havaianas.com/on/demandware.store/Sites-Havaianas-US-Site/default/Stores-FindStores?showMap=true&radius=300000000&postalCode="
    search_res = session.get(search_url, headers=headers)

    stores_list = json.loads(search_res.text)["stores"]

    for store in stores_list:

        page_url = "https://us.havaianas.com/store-locator/?showMap=true&horizontalView=true&isForm=true"
        locator_domain = website

        location_name = store["name"]

        street_address = store["address1"]

        if (
            "address2" in store
            and store["address2"] is not None
            and len(store["address2"]) > 0
        ):
            street_address = street_address + ", " + store["address2"]
        if (
            "address3" in store
            and store["address3"] is not None
            and len(store["address3"]) > 0
        ):
            street_address = street_address + ", " + store["address3"]

        city = store["city"]
        state = store["stateCode"]
        zip = store["postalCode"]

        country_code = store["countryCode"]

        store_number = store["ID"]

        phone = store.get("phone", "<MISSING>")

        location_type = "<MISSING>"

        hours_of_operation = ""
        hours_list = []
        if "storeHours" in store:
            hours_sel = lxml.html.fromstring(store["storeHours"])
            hours = hours_sel.xpath("//p/text()")
            for hour in hours:
                if len("".join(hour).strip()) > 0:
                    hours_list.append("".join(hour).strip())

        hours_of_operation = "; ".join(hours_list).strip()
        latitude = store["latitude"]
        longitude = store["longitude"]

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
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.StoreNumberId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()

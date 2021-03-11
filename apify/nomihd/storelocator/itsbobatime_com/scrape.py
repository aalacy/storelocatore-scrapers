# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json
from sgscrape import sgpostal as parser

website = "itsbobatime.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    # Your scraper here

    search_url = "https://itsbobatime.com/store-locations/"
    stores_req = session.get(search_url, headers=headers)
    stores = json.loads(
        stores_req.text.split('"#map1").maps(')[1].strip().split(").data")[0].strip()
    )["places"]

    for store in stores:
        page_url = search_url
        location_type = (
            store["location"]["extra_fields"]["taxonomy=dt_portfolio_category"]
            .replace(", New", "")
            .strip()
        )
        locator_domain = website
        location_name = store["title"]

        raw_address = ""
        if "address" in store:
            raw_address = store["address"].replace("USA", "").strip()
        else:
            raw_address = store["content"].replace("USA", "").strip()

        formatted_addr = parser.parse_address_usa(raw_address)
        street_address = formatted_addr.street_address_1
        if formatted_addr.street_address_2:
            street_address = street_address + ", " + formatted_addr.street_address_2

        city = formatted_addr.city
        if city == "Tbd":
            city = "<MISSING>"
        state = formatted_addr.state
        zip = formatted_addr.postcode
        country_code = formatted_addr.country
        phone = store["location"]["extra_fields"]["%h_phone%"]
        hours_of_operation = "<MISSING>"
        hours_list = []
        for key in store["location"]["extra_fields"].keys():
            if (
                "%h_mon%" == key
                or "%h_tue%" == key
                or "%h_wed%" == key
                or "%h_thu%" == key
                or "%h_fri%" == key
                or "%h_sat%" == key
                or "%h_sun%" == key
            ):
                if len(store["location"]["extra_fields"][key]) > 0:
                    hours_list.append(store["location"]["extra_fields"][key])

        hours_of_operation = "; ".join(hours_list).strip()
        if "TBD" == hours_of_operation:
            hours_of_operation = "<MISSING>"

        store_number = store["id"]

        latitude = store["location"]["lat"]
        longitude = store["location"]["lng"]

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

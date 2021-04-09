# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json
from sgscrape import sgpostal as parser

website = "superstarcarwashaz.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "accept": "application/json, text/plain, */*",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36",
}


def fetch_data():
    # Your scraper here
    api_url = "https://api2.storepoint.co/v1/15b74b43a2d40a/locations?lat=37.09024&long=-95.712891&radius=5000"
    api_res = session.get(api_url, headers=headers)
    json_res = json.loads(api_res.text)

    stores_list = json_res["results"]["locations"]
    for store in stores_list:
        if "coming soon" not in store["tags"].strip():
            page_url = "https://www.superstarcarwashaz.com/locations/"

            locator_domain = website
            location_name = store["name"].strip()
            raw_address = store["streetaddress"]

            formatted_addr = parser.parse_address_intl(raw_address)
            street_address = formatted_addr.street_address_1
            if formatted_addr.street_address_2:
                street_address = street_address + ", " + formatted_addr.street_address_2

            city = formatted_addr.city
            state = formatted_addr.state
            zip = formatted_addr.postcode

            country = "US"
            country_code = country

            store_number = store["id"]
            phone = store["phone"].strip()

            location_type = "<MISSING>"

            day_tags = [
                "monday",
                "tuesday",
                "wednesday",
                "thursday",
                "friday",
                "saturday",
                "sunday",
            ]
            hour_list = []
            for day in day_tags:
                time = store[day]
                if time:
                    hour_list.append(f"{day}: {time}")
                else:
                    hour_list.append(f"{day}: closed")

            hours_of_operation = "; ".join(hour_list)

            latitude = store["loc_lat"]
            longitude = store["loc_long"]

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

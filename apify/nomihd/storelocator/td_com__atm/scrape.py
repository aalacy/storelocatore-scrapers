# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json

website = "td.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    # Your scraper here
    url_list = [
        "https://www.tdbank.com/net/get12.ashx?longitude=-74.005972&latitude=40.7127753&country=US&locationtypes=3&json=y&searchradius=50000&searchunit=km&numresults=100000",
        "https://www.tdbank.com/net/get12.ashx?longitude=-79.3831843&latitude=43.653226&country=CA&locationtypes=3&json=y&searchradius=50000&searchunit=km&numresults=100000",
    ]
    for search_url in url_list:
        stores_req = session.get(search_url, headers=headers)
        stores = json.loads(stores_req.text)["markers"]["marker"]
        for store in stores:
            page_url = "<MISSING>"
            locator_domain = website
            location_name = "TD BANK"
            address = store["address"]
            street_address = ", ".join(address.split(",")[:-3]).strip()
            city = address.split(",")[-3].strip()
            state = address.split(",")[-2].strip()
            zip = address.split(",")[-1].strip()

            country_code = store["coun"].upper()
            if (
                zip.isdigit() is False
                and "," in street_address
                and country_code == "US"
            ):
                zip = state
                state = city
                city = street_address.split(",")[1].strip()
                street_address = street_address.split(",")[0].strip()

            phone = store["phoneNo"]

            store_number = store["id"]
            location_type = store["type"]

            if location_type == "1":
                location_type = "ATM"
            elif location_type == "3":
                location_type = "Branch and ATM"
            elif location_type == "2":
                continue

            hours_list = []
            if "hours" in store:
                hours = store["hours"]
                for day in hours.keys():
                    time = hours[day]
                    hours_list.append(day + ":" + time)

            hours_of_operation = "; ".join(hours_list).strip()
            latitude = store["lat"]
            longitude = store["lng"]
            if longitude == "N":
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

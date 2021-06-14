# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json
import lxml.html


website = "fmbnc.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "accept": "application/json, text/plain, */*",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36",
}


def fetch_data():
    # Your scraper here

    search_url = "https://www.fmbnc.com/connect/locate-branch-atm"
    locationtypes = ["atms", "branches"]
    for locationtype in locationtypes:

        api_url = f"https://www.fmbnc.com/_/api/{locationtype}/35.67061959999999/-80.4662429/25"

        api_res = session.get(api_url, headers=headers)

        json_res = json.loads(api_res.text)

        stores_list = json_res[locationtype]

        for store in stores_list:
            if not store["active"]:
                continue

            page_url = search_url
            locator_domain = website

            location_name = store["name"].strip()

            street_address = store["address"].strip()

            city = store["city"].strip()
            state = store["state"].strip()
            zip = store["zip"].strip()
            country_code = "US"
            store_number = "<MISSING>"

            phone = (
                store["phone"].strip() if locationtype == "branches" else "<MISSING>"
            )

            location_type = "ATM" if locationtype == "atms" else "Branch"
            if locationtype == "atms":
                hours_of_operation = "<MISSING>"
            else:
                hours_html = store["description"]
                hours_sel = lxml.html.fromstring(hours_html)
                hours_info = ("; ").join(
                    hours_sel.xpath(
                        '//i[text()="Drive-Thru:"]/preceding::div[contains(text(),"Mon") or contains(text(),"Fri")]/text()'
                    )
                )
                hours_of_operation = (
                    hours_info.replace("\n", "")
                    .replace("Friday", "Friday: ")
                    .replace("Thurs", "Thurs: ")
                )

            latitude = store["lat"]
            longitude = store["long"]

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

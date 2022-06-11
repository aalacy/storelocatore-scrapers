# -*- coding: utf-8 -*-
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json
import re
from sgpostal import sgpostal as parser
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgselenium import SgChrome
import time
import ssl
import lxml.html

ssl._create_default_https_context = ssl._create_unverified_context

website = "infineon.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

user_agent = (
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0"
)


def fetch_data():
    # Your scraper here

    api_url = "https://www.infineon.com/locationFinder/locations?types=&locale=en&site=ifx&region=&country="
    with SgChrome(user_agent=user_agent) as driver:

        driver.get(api_url)
        time.sleep(10)
        stores_sel = lxml.html.fromstring(driver.page_source)
        json_str = "".join(stores_sel.xpath("//body//text()")).strip()
        json_res = json.loads(json_str)

        stores_list = json_res["locations"]

        for store in stores_list:

            page_url = "https://www.infineon.com/cms/en/about-infineon/company/find-a-location/"
            locator_domain = website

            location_name = store["name"].strip()

            street_address = store["address"].strip()
            if "address2" in store and store["address2"].strip():
                street_address = street_address + " " + store["address2"].strip()

            city = store["city"].strip()
            if "state" in store:
                state = store["state"].strip()
            else:
                state = "<MISSING>"

            country_code = store["country"]
            store_number = store["id"]

            phone = "<MISSING>"

            raw_address = street_address

            if re.search("[0-9]", raw_address[-1]):
                phone = raw_address.split(",")[-1].strip()
                raw_address = ",".join(street_address.split(",")[:-1])

            formatted_addr = parser.parse_address_intl(raw_address)
            street_address = formatted_addr.street_address_1
            if formatted_addr.street_address_2:
                street_address = street_address + ", " + formatted_addr.street_address_2
            zip = formatted_addr.postcode
            if zip:
                zip = zip.replace("B-1011 34742", "34742").strip()
                zip = zip.replace("D-73431", "73431").strip()

            if state == "<MISSING>":
                state = formatted_addr.state

            location_type = "<MISSING>"

            hours_of_operation = "<MISSING>"
            latitude = store["latitude"]
            longitude = store["longitude"]

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

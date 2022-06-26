# -*- coding: utf-8 -*-
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json
from sgselenium import SgFirefox
import ssl
import lxml.html

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification


website = "myrustybucket.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)


def fetch_data():
    # Your scraper here

    search_url = "https://www.myrustybucket.com/wp-json/wp/v2/locations/?status=publish&per_page=100"
    with SgFirefox(block_third_parties=True) as driver:
        driver.get(search_url)
        log.info(driver.page_source)
        html_sel = lxml.html.fromstring(driver.page_source)
        stores = json.loads("".join(html_sel.xpath("//body//text()")).strip())

        for store in stores:
            page_url = store["link"]
            location_type = "<MISSING>"
            location_name = store["title"]["rendered"]
            locator_domain = website

            store_json = store["location_info"]

            street_address = (
                store_json["address"]["street_number"]
                + ", "
                + store_json["address"]["street_name"]
            )

            city = store_json["address"].get("city", "<MISSING>")
            if city == "<MISSING>":
                city = store_json["address"]["address"].split(",")[1].strip()

            state = store_json["address"].get("state_short", "<MISSING>")
            zip = store_json["address"].get("post_code", "<MISSING>")
            country_code = store_json["address"].get("country_short", "<MISSING>")

            phone = store_json.get("phone_number", "<MISSING>")
            location_type = "<MISSING>"

            hour_list = []

            hours = store_json["hours"]["days"]
            for day, hour in hours.items():
                hour_list.append(f'{day}: {hours[day]["open"]} - {hours[day]["close"]}')

            hours_of_operation = (
                "; ".join(hour_list)
                .strip()
                .encode("ascii", "replace")
                .decode("utf-8")
                .replace("?", "-")
                .strip()
            )

            store_number = store["id"]

            latitude = store_json["address"]["lat"]
            longitude = store_json["address"]["lng"]

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

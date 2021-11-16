# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "whitespot.ca"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "accept": "application/json, text/plain, */*",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36",
}


def fetch_data():
    # Your scraper here
    api_url = "https://www.whitespot.ca/wp/wp-admin/admin-ajax.php?action=getLocations&start_location=(57.4859%2C+-124.3735)&offset=0&bounds=&maxMatches=-1&radius=-1"
    api_res = session.get(api_url, headers=headers)

    json_res = json.loads(api_res.text)

    stores_list = json_res["data"]["locations"]

    for store in stores_list:

        page_url = store["location_permalink"]

        locator_domain = website
        location_name = store["location_name"].replace("amp;", "").strip()

        street_address = store["address_1"].strip()
        if (
            "address_2" in store
            and store["address_2"] is not None
            and store["address_2"].strip()
        ):
            street_address = street_address + ", " + store["address_2"].strip()

        city = store["region"].replace("-", " ").capitalize()
        state = "<MISSING>"
        zip = store["postal_code"].strip()

        if zip == "n/a" or zip == "Permanently Closed":
            # page not available
            continue
        elif zip == "Temporarily Closed":
            location_type = "Temporarily Closed"
            zip = "<MISSING>"
        else:
            location_type = "<MISSING>"

        country_code = "CA"

        store_number = store["location_id"]
        phone = store["phone_number"]

        log.info(page_url)
        page_res = session.get(page_url, headers=headers)
        page_sel = lxml.html.fromstring(page_res.text)
        if len(street_address) <= 0:
            street_address = (
                "".join(page_sel.xpath('//*[@class="location__address"]/text()'))
                .strip()
                .split(",")[0]
                .strip()
            )

        if len(zip) <= 0:
            zip = (
                "".join(page_sel.xpath('//*[@class="location__address"]/text()'))
                .strip()
                .split(",")[-1]
                .strip()
            )

        if len(phone) <= 0:
            phone = "".join(
                page_sel.xpath('//div[@class="location__phone"]/a/text()')
            ).strip()

        hours_list = list(
            filter(str, page_sel.xpath('//table[@class="location__hours"]//tr//text()'))
        )

        hours_list = list(filter(str, [x.strip() for x in hours_list]))
        hours_of_operation = (
            "; ".join(hours_list)
            .replace("\n", " ")
            .replace("  ", " ")
            .replace("day; ", "day: ")
            .strip(" ;")
        )

        if (
            "decision to temporarily close" in store["special_notice"]
            or "location is temporarily close" in store["special_notice"]
            or "temporarily closed for" in store["special_notice"]
        ):
            hours_of_operation = "<MISSING>"
            location_type = "Temporarily Closed"

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
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PageUrlId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()

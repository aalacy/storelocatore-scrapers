# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
import json
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import us

website = "pumpandpantry.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    # Your scraper here
    search_url = "https://pumpandpantry.com/wp-admin/admin-ajax.php"

    data = {"action": "get_all_stores", "lat": "", "lng": ""}

    stores_req = session.post(search_url, data=data, headers=headers)
    stores = json.loads(stores_req.text)

    for key in stores.keys():
        location_type = "<MISSING>"
        latitude = stores[key]["lat"]
        longitude = stores[key]["lng"]
        page_url = stores[key]["gu"]

        locator_domain = website
        location_name = stores[key]["na"]
        if location_name == "":
            location_name = "<MISSING>"

        street_address = stores[key]["st"]
        city = stores[key]["ct"].strip()
        state = stores[key]["rg"].strip()
        phone = stores[key]["te"].strip()
        hours_sel = lxml.html.fromstring(stores[key]["de"])
        hours = hours_sel.xpath('//div[./h3[contains(text(),"HOURS")]]/div/p//text()')
        if len(hours) <= 0:
            hours = hours_sel.xpath(
                '//div[./h3[contains(text(),"HOURS")]]/div/b//text()'
            )

        if len(hours) <= 0:
            log.info(page_url)
            store_req = session.get(page_url, headers=headers)
            store_sel = lxml.html.fromstring(store_req.text)
            hours = store_sel.xpath(
                '//div[./h3[contains(text(),"HOURS")]]/div/b//text()'
            )
            if len(hours) <= 0:
                hours = store_sel.xpath(
                    '//div[./h3[contains(text(),"HOURS")]]/div//text()'
                )

        zip = stores[key]["zp"]

        country_code = "<MISSING>"
        if us.states.lookup(state):
            country_code = "US"

        store_number = ""
        if "#" in location_name:
            store_number = location_name.split("#")[1].strip()
        hours_list = []
        for hour in hours:
            if len("".join(hour).strip()) > 0:
                hours_list.append("".join(hour).strip())

        hours_of_operation = (
            "; ".join(hours_list)
            .strip()
            .encode("ascii", "replace")
            .decode("utf-8")
            .replace("?", "-")
            .strip()
        )

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

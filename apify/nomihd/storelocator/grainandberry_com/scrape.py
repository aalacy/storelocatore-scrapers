# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "grainandberry.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    # Your scraper here
    search_url = "https://grainandberry.com/locations/"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    stores = stores_sel.xpath('//div[contains(@class,"x-column x-sm x-1-4")]')

    for store in stores:
        page_url = search_url

        locator_domain = website
        location_name = "".join(store.xpath("div[1]//text()")).strip()
        if len(location_name) <= 0:
            continue
        add_list = store.xpath("div[2]/p[1]/text()")
        if "Location TBD" in "".join(add_list).strip():
            continue
        street_address = add_list[0].strip()
        city = add_list[-1].strip().split(",")[0].strip()
        state = add_list[-1].strip().split(",")[1].strip()
        if len(state.split(" ")) > 1:
            zip = state.split(" ")[-1].strip()
        else:
            zip = "<MISSING>"
        country_code = "US"

        phone = "".join(store.xpath("div[2]/p[contains(text(),'(')]//text()")).strip()
        if len(phone) <= 0:
            phone = "".join(
                store.xpath("div[2]/p/strong[contains(text(),'(')]//text()")
            ).strip()
        store_number = "<MISSING>"
        location_type = "<MISSING>"

        hours_of_operation = "".join(store.xpath("div[2]/p[2]//text()")).strip()

        if "Coming" in hours_of_operation:
            continue
        latitude = "<MISSING>"
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
    with SgWriter(
        deduper=SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.LOCATION_NAME,
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.CITY,
                    SgRecord.Headers.STATE,
                }
            )
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()

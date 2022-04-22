# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "horizonbankne.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests(dont_retry_status_codes=([404]), proxy_country="us")
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36",
}


def fetch_data():
    # Your scraper here

    search_url = "https://www.horizonbankne.com/"
    search_res = session.get(search_url, headers=headers)
    search_sel = lxml.html.fromstring(search_res.text)

    stores = search_sel.xpath("//fluid-columns-repeater/div")
    for store in stores:

        page_url = "".join(
            store.xpath('.//a[./span[contains(text(),"Learn More")]]/@href')
        ).strip()
        locator_domain = website
        store_info = list(filter(str, [x.strip() for x in store.xpath(".//text()")]))
        location_name = store_info[0].strip()

        street_address = store_info[1].strip()

        city = store_info[2].split(",")[0].strip()
        state = store_info[2].split(",")[-1].strip().split(" ")[0].strip()
        zip = store_info[2].split(",")[-1].strip().split(" ")[-1].strip()

        country_code = "US"

        store_number = "<MISSING>"
        location_type = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"

        phone = store_info[3].strip()
        hours_of_operation = "<MISSING>"
        for index in range(0, len(store_info)):
            if "Lobby" in store_info[index]:
                hours_of_operation = (
                    "; ".join(store_info[index + 1 : -1])
                    .strip()
                    .encode("ascii", "replace")
                    .decode("utf-8")
                    .replace("?", "")
                    .strip()
                )

        if len(hours_of_operation) > 0 and hours_of_operation[-1] == ";":
            hours_of_operation = "".join(hours_of_operation[:-1]).strip()

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
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PhoneNumberId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()

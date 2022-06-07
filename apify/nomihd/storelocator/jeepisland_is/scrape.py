# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "jeepisland.is"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.jeep.is/dealer-locator/"

    with SgRequests() as session:
        search_res = session.get(search_url, headers=headers)

        search_sel = lxml.html.fromstring(search_res.text)

        locator_domain = website

        location_name = "Jeep Islanda"
        page_url = search_url

        location_type = "<MISSING>"
        store_info = search_sel.xpath(
            '//h4[./strong[contains(text(),"SÖLUDEILD OG SKRIFSTOFA:")]]/following-sibling::p[1]/text()'
        )

        street_address = "".join(store_info[1]).strip().split(",")[0].strip()
        city = (
            "".join(store_info[1])
            .strip()
            .split(",")[-1]
            .strip()
            .split(" ", 1)[-1]
            .strip()
        )
        state = "<MISSING>"
        zip = (
            "".join(store_info[1])
            .strip()
            .split(",")[-1]
            .strip()
            .strip()
            .split(" ", 1)[0]
            .strip()
        )

        country_code = "IS"
        phone = store_info[0].replace("Sími:", "").strip()

        hours = search_sel.xpath('//h4[./strong[contains(text(),"AFGREIÐSLUTÍMI")]]')
        hours_of_operation = "<MISSING>"
        if len(hours) > 0:
            hours_of_operation = "; ".join(
                hours[0].xpath("following-sibling::p[1]/text()")
            ).strip()

        store_number = "<MISSING>"

        latitude, longitude = "<MISSING>", "<MISSING>"

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
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.CITY,
                    SgRecord.Headers.ZIP,
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

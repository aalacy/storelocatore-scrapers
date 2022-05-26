# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "novaninja.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "authority": "novaninja.com",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
    "cache-control": "max-age=0",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="101", "Google Chrome";v="101"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "cross-site",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.67 Safari/537.36",
}


def fetch_data():
    # Your scraper here
    search_url = "https://novaninja.com/"

    with SgRequests(verify_ssl=False) as session:
        search_res = session.get(search_url, headers=headers)

        search_sel = lxml.html.fromstring(search_res.text)

        stores = search_sel.xpath(
            "//div[@class='textwidget']/p[./a[contains(text(),'map')]]"
        )

        for store in stores:

            locator_domain = website

            page_url = search_url
            location_name = "".join(store.xpath("strong/text()")).strip()

            store_info = list(
                filter(
                    str,
                    [x.strip() for x in store.xpath("text()")],
                )
            )
            log.info(store_info)
            location_type = "<MISSING>"

            street_address = ", ".join(store_info[:-2]).strip()
            city = store_info[-2].strip().split("(")[0].strip().split(",")[0].strip()

            state = (
                store_info[-2]
                .strip()
                .split("(")[0]
                .strip()
                .split(",")[-1]
                .strip()
                .split(" ")[0]
                .strip()
            )
            zip = (
                store_info[-2]
                .strip()
                .split("(")[0]
                .strip()
                .split(",")[-1]
                .strip()
                .split(" ")[-1]
                .strip()
            )

            country_code = "US"

            store_number = "<MISSING>"

            phone = store.xpath('//li/a[contains(@href,"tel:")]/text()')
            if len(phone) > 0:
                phone = phone[0].strip()
            else:
                phone = "<MISSING>"

            hours_of_operation = "<MISSING>"

            latitude = longitude = "<MISSING>"

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
                    SgRecord.Headers.STATE,
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

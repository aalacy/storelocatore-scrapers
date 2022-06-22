# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "thevarsity.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "authority": "thevarsity.com",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
    "referer": "https://thevarsity.com/",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="102", "Google Chrome";v="102"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "same-origin",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36",
}


def fetch_data():
    # Your scraper here

    search_url = "https://thevarsity.com/pages/locations"

    with SgRequests() as session:
        stores_req = session.get(search_url, headers=headers)
        stores_sel = lxml.html.fromstring(stores_req.text)
        stores = stores_sel.xpath(
            "//main[@id='MainContent']//div[contains(@class,'grid__item medium-up--one-')]"
        )

        for store in stores:

            locator_domain = website

            location_name = "".join(store.xpath("h3/text()")).strip()
            page_url = (
                "https://thevarsity.com" + "".join(store.xpath("a/@href")).strip()
            )
            log.info(page_url)
            store_req = session.get(page_url, headers=headers)
            store_sel = lxml.html.fromstring(store_req.text)

            location_type = "<MISSING>"

            raw_address = store.xpath(
                "div[@class='rte-setting text-spacing']/p[1]/text()"
            )

            street_address = raw_address[0].strip()
            city = raw_address[-1].strip().split(",")[0].strip()
            state = raw_address[-1].strip().split(",")[-1].strip().split(" ")[0].strip()
            zip = raw_address[-1].strip().split(",")[-1].strip().split(" ")[-1].strip()

            country_code = "US"

            phone = "".join(
                store.xpath(".//p/a[contains(@href,'tel:')]/text()")
            ).strip()

            hours = store_sel.xpath(
                '//p[./strong[contains(text(),"HOURS OF OPERATION:")]]/following-sibling::p'
            )
            hours_list = []
            if (
                len(hours) <= 0
                or "We are located" in "".join(hours[0].xpath("text()")).strip()
            ):
                hours = store_sel.xpath(
                    '//p[./strong[contains(text(),"HOURS OF OPERATION:")]]'
                )
            if len(hours) > 0:
                hours = hours[0].xpath("text()")
                for hour in hours:
                    if hour[0] == "-":
                        hours_list.append("".join(hour[1:]).strip())
                    else:
                        hours_list.append("".join(hour).strip())

            hours_of_operation = (
                "; ".join(hours_list)
                .strip()
                .split("; Closed on")[0]
                .strip()
                .split("(")[0]
                .strip()
            )

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

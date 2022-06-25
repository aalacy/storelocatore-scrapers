# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "shrimphouse.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36",
}


def fetch_data():
    # Your scraper here
    with SgRequests() as session:
        search_res = session.get(
            "https://www.shrimphouse.com/locations/", headers=headers
        )

        stores_sel = lxml.html.fromstring(search_res.text)

        stores = stores_sel.xpath(
            "//div[@class='locationsRowItemDetailsContent']/a/@href"
        )

        for store_url in stores:
            page_url = store_url
            log.info(page_url)

            page_res = session.get(page_url, headers=headers)

            store_sel = lxml.html.fromstring(page_res.text)

            locator_domain = website

            location_name = "".join(
                store_sel.xpath('//div[@class="entry-header-menu"]/h1/text()')
            ).strip()

            raw_info = list(
                filter(
                    str,
                    [
                        x.strip()
                        for x in store_sel.xpath(
                            '//div[@class="entry-content"]//div[@class="wpb_wrapper"]//p//text()'
                        )
                    ],
                )
            )
            raw_address = raw_info[:2]

            street_address = raw_address[0].strip()
            if len(street_address) > 0 and street_address[-1] == ",":
                street_address = "".join(street_address[:-1]).strip()

            city = raw_address[-1].strip().split(",")[0].strip()
            state = raw_address[-1].strip().split(",")[-1].strip().split(" ")[0].strip()
            zip = raw_address[-1].strip().split(",")[-1].strip().split(" ")[-1].strip()

            country_code = "US"

            phone = raw_info[2].strip()
            store_number = "<MISSING>"

            location_type = "<MISSING>"

            hours_of_operation = "<MISSING>"
            for index in range(0, len(raw_info)):
                if "Hours:" == raw_info[index]:
                    hours_of_operation = (
                        "; ".join(raw_info[index + 1 :])
                        .strip()
                        .replace(":;", ":")
                        .strip()
                    )

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

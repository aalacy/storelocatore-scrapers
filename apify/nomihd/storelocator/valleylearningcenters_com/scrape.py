# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
import json

website = "valleylearningcenters.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    # Your scraper here
    search_url = "https://valleylearningcenters.com/wp-json/wpgmza/v1/markers/"
    stores_req = session.get(search_url, headers=headers)
    stores = json.loads(stores_req.text)

    for store in stores:
        if store["link"] is not None and len(store["link"]) > 0:
            page_url = store["link"]
            log.info(page_url)
            store_req = session.get(page_url, headers=headers)
            store_sel = lxml.html.fromstring(store_req.text)

            locator_domain = website
            location_name = store["title"]

            raw_info = store_sel.xpath('//div[@class=" n2-ow n2-ow-all"]/p/text()')
            raw_list = []
            for raw in raw_info:
                if len("".join(raw).strip()) > 0:
                    raw_list.append("".join(raw).strip())

            street_address = ", ".join(raw_list[:-1])
            city_state_zip = raw_list[-1]
            city = city_state_zip.split(",")[0].strip()
            state = city_state_zip.split(",")[1].strip().split(" ")[0].strip()
            zip = city_state_zip.split(",")[1].strip().split(" ")[1].strip()

            country_code = "US"

            store_number = "<MISSING>"
            phone = "".join(
                store_sel.xpath(
                    '//div[@class=" n2-ow n2-ow-all"]/p/a[contains(@href,"tel:")]/text()'
                )
            ).strip()

            location_type = "<MISSING>"

            hours_list = []
            hours_of_operation = (
                ":".join(
                    store_sel.xpath(
                        '//div[@class="wp-block-media-text__content"]/p//text()'
                    )
                )
                .strip()
                .encode("ascii", "replace")
                .decode("utf-8")
                .replace("?", "-")
                .strip()
            )

            latitude = store["lat"]
            longitude = store["lng"]

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
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()

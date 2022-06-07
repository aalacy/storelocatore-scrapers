# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
import json
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "beckershoes.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
}


def fetch_data():
    # Your scraper here

    search_url = "https://www.beckershoes.com/locations/"

    with SgRequests() as session:
        search_res = session.get(search_url, headers=headers)

        search_sel = lxml.html.fromstring(search_res.text)

        json_str = (
            search_res.text.split("jsonLocations:")[1]
            .split("imageLocations:")[0]
            .strip()
            .strip(", ")
        )
        json_obj = json.loads(json_str)

        stores = json_obj["items"]

        for no, store in enumerate(stores, 1):

            locator_domain = website
            store_number = store["id"]

            store_sel = search_sel.xpath(
                f'//div[@class="amlocator-stores-wrapper"]/div[@data-amid="{store_number}"]'
            )[0]

            page_url = "".join(
                store_sel.xpath('.//div[@class="amlocator-title"]/a/@href')
            ).strip()

            location_name = "".join(
                store_sel.xpath('.//div[@class="amlocator-title"]/a//text()')
            ).strip()
            location_type = "<MISSING>"

            store_info = list(
                filter(
                    str,
                    [
                        x.strip()
                        for x in store_sel.xpath(
                            './/div[@class="amlocator-store-information"]/text()'
                        )
                    ],
                )
            )
            raw_address = "<MISSING>"

            street_address = (
                store_info[-2]
                .split(":")[1]
                .strip()
                .replace("Georgian Mall", "")
                .replace(", Mountainview Plaza Midland", "")
                .replace("The Quinte Mall", "")
                .replace("The Huntsville Place Mall", "")
                .strip()
            )
            if street_address[-1] == ",":
                street_address = "".join(street_address[:-1]).strip()

            city = store_info[0].split(":")[1].strip()

            state = store_info[-3].split(":")[1].strip()
            zip = store_info[1].split(":")[1].strip()

            country_code = "CA"

            phone = store_info[-1].split(":")[1].strip()

            hours = list(
                filter(
                    str,
                    [
                        x.strip()
                        for x in store_sel.xpath(
                            './/div[@class="amlocator-week"]//span//text()'
                        )
                    ],
                )
            )
            hours_of_operation = "; ".join(hours).replace("day; ", "day: ")

            latitude, longitude = store["lat"], store["lng"]

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

# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgpostal import sgpostal as parser
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "www.scrubadub.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36",
}


def fetch_data():
    # Your scraper here

    search_url = "https://www.scrubadub.com/#"

    with SgRequests() as session:
        search_res = session.get(search_url, headers=headers)
        search_sel = lxml.html.fromstring(search_res.text)

        stores = search_sel.xpath(
            '//li[contains(a/text(),"Find Us")]//li/a[not(@href="#")]'
        )

        for store in stores:

            page_url = "".join(store.xpath("./@href"))
            log.info(page_url)
            store_res = session.get(page_url, headers=headers)
            store_sel = lxml.html.fromstring(store_res.text)

            locator_domain = website

            location_name = "".join(store_sel.xpath("//title//text()")).strip()

            store_info = list(
                filter(
                    str,
                    [
                        x.strip()
                        for x in store_sel.xpath(
                            '//div[contains(./strong/text(),"Address") or contains(./p//text(),"Address")]/..//text()'
                        )
                    ],
                )
            )
            raw_address = (
                " ".join(store_info[1:])
                .strip()
                .split("Phone")[0]
                .strip()
                .replace(
                    "(Our old address at 235 Market St will no longer have an entrance to the property.)",
                    "",
                )
                .strip()
            )
            formatted_addr = parser.parse_address_intl(raw_address)
            street_address = formatted_addr.street_address_1
            if formatted_addr.street_address_2:
                street_address = street_address + ", " + formatted_addr.street_address_2

            if street_address is not None:
                street_address = (
                    street_address.replace("Ste", "Suite")
                    .strip()
                    .replace("At The Maine Mall", "")
                    .strip()
                )
            city = formatted_addr.city
            state = formatted_addr.state
            zip = formatted_addr.postcode

            country_code = "US"

            store_number = "<MISSING>"

            phone = (
                " ".join(store_info[1:])
                .strip()
                .split("Phone:")[1]
                .split("Hours of Operation")[0]
                .strip()
            )

            location_type = "<MISSING>"

            hours_of_operation = (
                "; ".join(store_info[1:])
                .strip()
                .split("Hours of Operation")[1]
                .strip()
                .split("* We try")[0]
                .strip(";: ")
                .replace("Weather Permitting", "")
                .strip("()*;: ")
                .strip()
                .replace("(* Weather Permitting);", "")
                .strip()
                .replace("; .", "")
                .strip()
                .replace("(*);", "")
                .strip()
            )
            if "Car Wash:" in hours_of_operation:
                hours_of_operation = hours_of_operation.split("Car Wash:")[1].strip()
            latitude, longitude = (
                store_res.text.split('data-map-lat="')[-1].split('"')[0],
                store_res.text.split('data-map-lng="')[-1].split('"')[0],
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

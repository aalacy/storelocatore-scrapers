# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgpostal import sgpostal as parser
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "mintvelvet.co.uk"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
}


def fetch_data():
    # Your scraper here
    base = "http://www.mintvelvet.co.uk"
    search_url = "https://www.mintvelvet.co.uk/store-locator"

    with SgRequests() as session:
        search_res = session.get(search_url, headers=headers)

        search_sel = lxml.html.fromstring(search_res.text)

        stores = search_sel.xpath('//ul[@class="mv__stores-list"]/li[a]')
        for no, store in enumerate(stores, 1):

            locator_domain = website

            page_url = "".join(store.xpath("./a/@href"))
            if "mintvelvet" not in page_url:
                page_url = base + page_url
            log.info(page_url)

            store_res = session.get(page_url, headers=headers)
            store_sel = lxml.html.fromstring(store_res.text)

            store_number = page_url.split("/")[-1]

            location_name = "".join(store.xpath("./a/text()")).strip()

            location_type = "<MISSING>"

            store_info = list(
                filter(
                    str,
                    [x.strip() for x in store_sel.xpath("//address/p//text()")],
                )
            )

            phone = (
                "".join(store_sel.xpath('//a[contains(@href,"tel:")]//text()'))
                .strip()
                .strip(".mv-mob-phone{fill:#58595b;} ")
                .strip()
            )

            raw_address = ", ".join(store_info).strip()

            formatted_addr = parser.parse_address_intl(raw_address)
            street_address = formatted_addr.street_address_1
            if formatted_addr.street_address_2:
                street_address = street_address + ", " + formatted_addr.street_address_2

            if street_address is not None:
                street_address = street_address.replace("Ste", "Suite")

            city = formatted_addr.city

            state = formatted_addr.state

            zip = formatted_addr.postcode
            if not zip:
                zip = raw_address.split(",")[-1].strip()

            country_code = "GB"
            if zip == "Ireland":
                zip = "<MISSING>"
                country_code = "IE"

            hours = list(
                filter(
                    str,
                    [
                        x.strip()
                        for x in store_sel.xpath(
                            '//div[h4="Opening times"]//li//text()'
                        )
                    ],
                )
            )

            hours_of_operation = (
                "; ".join(hours)
                .replace("day; ", "day: ")
                .replace("Mon; ", "Mon: ")
                .replace("Tue; ", "Tue: ")
                .replace("Wed; ", "Wed: ")
                .replace("Thu; ", "Thu: ")
                .replace("Fri; ", "Fri: ")
                .replace("Sat; ", "Sat: ")
                .replace("Sun; ", "Sun: ")
                .replace("day:;", "day:")
                .replace("OPEN FOR BUSINESS!", "")
                .replace("NOW OPEN!", "")
                .strip(";! ")
            )

            if (
                hours_of_operation
                == "Mon: -; Tue: -; Wed: -; Thu: -; Fri: -; Sat: -; Sun: -"
            ):
                hours_of_operation = "<MISSING>"
            latitude, longitude = (
                store_res.text.split("lat:")[1]
                .split("}")[0]
                .strip()
                .replace("\n", "")
                .strip(),
                store_res.text.split("lng:")[1].split(",")[0].strip(),
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

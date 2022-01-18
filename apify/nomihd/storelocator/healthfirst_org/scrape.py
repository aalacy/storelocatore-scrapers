# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgpostal import sgpostal as parser
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "healthfirst.org"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
}


def fetch_data():
    # Your scraper here
    search_url = "https://hfrepdirectory.healthfirst.org/CommunityOffices"

    with SgRequests() as session:
        search_res = session.get(search_url, headers=headers)

        search_sel = lxml.html.fromstring(search_res.text)

        stores = search_sel.xpath(
            '//div[@class="communityOfficeLocationsContainer"]//div[h1]'
        )

        for no, store in enumerate(stores, 1):

            locator_domain = website
            store_number = "<MISSING>"

            page_url = search_url

            location_name = "".join(store.xpath("./h1//text()")).strip()

            location_type = "<MISSING>"

            store_info = list(
                filter(
                    str,
                    [x.strip() for x in store.xpath(".//p//text()")],
                )
            )

            phone = "<MISSING>"
            raw_address = " ".join(store_info)

            formatted_addr = parser.parse_address_usa(raw_address)
            street_address = formatted_addr.street_address_1
            if formatted_addr.street_address_2:
                street_address = street_address + ", " + formatted_addr.street_address_2

            if street_address is not None:
                street_address = street_address.replace("Ste", "Suite")

            city = formatted_addr.city

            state = formatted_addr.state
            zip = formatted_addr.postcode

            country_code = "US"

            hours = list(
                filter(str, [x.strip() for x in store.xpath(".//table//text()")])
            )

            hours_of_operation = (
                "; ".join(hours)
                .replace("day; ", "day: ")
                .replace("day:;", "day:")
                .replace("OPEN FOR BUSINESS!", "")
                .replace("NOW OPEN!", "")
                .replace("&nbsp&nbsp&nbsp&nbsp&nbsp;", ":")
                .replace("\n", "")
                .strip()
                .strip(";! ")
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
        deduper=SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()

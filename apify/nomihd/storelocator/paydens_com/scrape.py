# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgpostal import sgpostal as parser
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "paydens.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
}


def fetch_data():
    # Your scraper here
    base = "http://www.paydens.com"
    search_url = "https://www.paydens.com/findpharmacy/fulllist"

    with SgRequests() as session:
        search_res = session.get(search_url, headers=headers)

        search_sel = lxml.html.fromstring(search_res.text)

        stores = search_sel.xpath("//tbody/tr")
        log.info(f"Expected Total Location: {len(stores)}")
        for no, store in enumerate(stores, 1):

            locator_domain = website
            store_number = "<MISSING>"

            page_url = base + "".join(
                store.xpath(".//a[contains(text(),'More')]/@href")
            )
            log.info(f"Crawling {page_url}")

            store_res = session.get(page_url, headers=headers)
            log.info(f"Page Response: {store_res.status_code}")
            store_sel = lxml.html.fromstring(store_res.text)

            location_name = "".join(store.xpath(".//a[not(@class)]/text()")).strip()

            location_type = "<MISSING>"

            store_info = list(
                filter(
                    str,
                    [
                        x.strip()
                        for x in store.xpath(".//td[not(a) and not(@class)]//text()")
                    ],
                )
            )

            phone = "".join(store.xpath('.//td[@class="nowrap"]//text()')).strip()

            raw_address = " ".join(store_info).strip()

            formatted_addr = parser.parse_address_intl(raw_address)
            street_address = formatted_addr.street_address_1
            if formatted_addr.street_address_2:
                street_address = street_address + ", " + formatted_addr.street_address_2

            if street_address is not None:
                street_address = street_address.replace("Ste", "Suite")

            if street_address and street_address.replace("-", "").isdigit():
                street_address = raw_address.split(",")[0].strip()

            city = formatted_addr.city

            state = formatted_addr.state
            zip = formatted_addr.postcode
            if not zip:
                zip = store_info[-1].strip()

            country_code = "GB"

            hours = store_sel.xpath("//table//tr")
            hours_list = []
            for hour in hours:
                day = "".join(hour.xpath("td[1]//text()")).strip()
                time = "".join(hour.xpath("td[2]//text()")).strip()
                if len(day) > 0 and len(time) > 0:
                    hours_list.append(day + time)

            hours_of_operation = "; ".join(hours_list).strip()

            latitude, longitude = (
                "<MISSING>",
                "<MISSING>",
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

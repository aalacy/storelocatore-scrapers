# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgpostal import sgpostal as parser
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "pizzaexpress.ae"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Accept-Language": "en-US,en;q=0.9,ar;q=0.8",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36",
}


def fetch_data():
    # Your scraper here
    base = "https://pizzaexpress.ae"
    search_url = "https://pizzaexpress.ae/all-restaurants"

    with SgRequests() as session:
        search_res = session.get(search_url, headers=headers)

        search_sel = lxml.html.fromstring(search_res.text)

        stores = search_sel.xpath('//*[@class="summary-title"]/..')

        for store in stores:

            locator_domain = website

            page_url = base + "".join(
                store.xpath("./*[@class='summary-title']/a/@href")
            )
            log.info(page_url)

            store_res = session.get(page_url, headers=headers)

            store_sel = lxml.html.fromstring(store_res.text)
            location_name = "".join(
                store_sel.xpath('//meta[@property="og:title"]//@content')
            ).strip()

            store_info = list(
                filter(
                    str,
                    [
                        x.strip()
                        for x in store_sel.xpath(
                            '//meta[@property="og:description"]//@content'
                        )
                    ],
                )
            )
            location_type = "<MISSING>"

            raw_address = store_info[0].split("   ")[0].strip()
            phone = store_info[0].split("   ")[1].strip()
            hours_of_operation = (
                "; ".join(store_info[0].split("   ")[-1].split("  "))
                .strip()
                .replace("Daily;", "Daily")
                .strip()
            )

            formatted_addr = parser.parse_address_intl(raw_address)
            street_address = formatted_addr.street_address_1
            if formatted_addr.street_address_2:
                street_address = street_address + ", " + formatted_addr.street_address_2

            if street_address is not None:
                street_address = street_address.replace("Ste", "Suite")

            city = formatted_addr.city
            if not city:
                city = "".join(store.xpath(".//preceding::h2[1]//text()")).strip()

            state = formatted_addr.state
            zip = formatted_addr.postcode

            country_code = "AE"

            store_number = "<MISSING>"

            latitude = "".join(
                store_sel.xpath('//meta[@property="og:latitude"]//@content')
            ).strip()
            longitude = "".join(
                store_sel.xpath('//meta[@property="og:longitude"]//@content')
            ).strip()

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

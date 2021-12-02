# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import lxml.html
from sgpostal import sgpostal as parser

website = "jeep.com.do"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36",
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.jeep.com.do/concesionario/"
    with SgRequests(dont_retry_status_codes=([404]), proxy_country="us") as session:
        search_res = session.get(search_url, headers=headers)
        stores_sel = lxml.html.fromstring(search_res.text)
        stores = stores_sel.xpath(
            '//div[@class="wp-block-group__inner-container"][./h1[contains(text(),"Concesionario")]]'
        )
        for store in stores:
            location_type = "<MISSING>"
            page_url = search_url
            locator_domain = website
            location_name = "".join(store.xpath("h2/text()")).strip()
            store_info = store.xpath("p/text()")
            raw_address = store_info[0]

            formatted_addr = parser.parse_address_intl(raw_address)
            street_address = formatted_addr.street_address_1
            if street_address:
                if formatted_addr.street_address_2:
                    street_address = (
                        street_address + ", " + formatted_addr.street_address_2
                    )
            else:
                if formatted_addr.street_address_2:
                    street_address = formatted_addr.street_address_2

            city = formatted_addr.city
            if not city:
                city = "Santo Domingo"
            state = formatted_addr.state
            zip = formatted_addr.postcode

            country_code = "DO"

            phone = "".join(store_info[1]).strip().replace("Tel.", "").strip()
            store_number = "<MISSING>"

            hours_of_operation = "<MISSING>"
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
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PhoneNumberId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()

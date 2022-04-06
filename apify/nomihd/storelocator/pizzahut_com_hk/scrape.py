# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgpostal import sgpostal as parser
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "pizzahut.com.hk"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests(verify_ssl=False)
headers = {
    "authority": "www.pizzahut.com.hk",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="90", "Google Chrome";v="90"',
    "sec-ch-ua-mobile": "?0",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "none",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "accept-language": "en-US,en;q=0.9,ar;q=0.8",
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.pizzahut.com.hk/corp/en/store"
    search_res = session.get(search_url, headers=headers)

    search_sel = lxml.html.fromstring(search_res.text)

    store_list = search_sel.xpath('//a[contains(@href,"javascript:findstore")]')

    for store in store_list:

        page_url = search_url

        ID = (
            "".join(store.xpath("./@href"))
            .split("javascript:findstore('")[1]
            .split("',")[0]
            .strip()
        )

        page_url = f"https://www.pizzahut.com.hk/corp/en/store/detail.html?id={ID}&l=en"
        log.info(page_url)
        store_res = session.get(page_url, headers=headers)
        store_sel = lxml.html.fromstring(
            store_res.text.replace('<?xml version="1.0" encoding="utf-8"?>', "").strip()
        )

        for location in store_sel.xpath('//div[@class="store"]'):
            locator_domain = website
            location_name = " ".join(
                store_sel.xpath('//div[@class="store_district"]//text()')
            ).strip()

            full_address = list(
                filter(
                    str,
                    [
                        x.strip()
                        for x in location.xpath('./div[@class="store_address"]//text()')
                    ],
                )
            )

            raw_address = ", ".join(full_address).strip()

            formatted_addr = parser.parse_address_intl(raw_address)
            street_address = formatted_addr.street_address_1
            if formatted_addr.street_address_2:
                street_address = street_address + ", " + formatted_addr.street_address_2

            city = formatted_addr.city
            state = formatted_addr.state
            zip = formatted_addr.postcode

            country_code = "HK"

            phone = (
                "".join(location.xpath('./div[@class="store_to"]//text()'))
                .strip()
                .replace("Store phone no:", "")
                .strip()
            )

            location_type = ", ".join(
                location.xpath('.//div[@class="store_item"]//td/text()')
            ).strip()
            store_number = "<MISSING>"
            hours_of_operation = (
                "Monday to Thursday: 11:00 - 22:30, Friday to Sunday: 11:00 - 23:00"
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
        deduper=SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.RAW_ADDRESS,
                }
            )
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()

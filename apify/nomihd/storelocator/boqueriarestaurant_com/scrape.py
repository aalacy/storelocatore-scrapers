# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal import sgpostal as parser


website = "boqueriarestaurant.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "authority": "boqueriarestaurant.com",
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
    base = "https://boqueriarestaurant.com"

    search_res = session.get(base, headers=headers)
    search_sel = lxml.html.fromstring(search_res.text)

    stores_list = search_sel.xpath(
        '//div[@class="vc_tta-panels" and .//p[contains(./text(),"Hours")]]/div[.//text()="Hours"]'
    ) + search_sel.xpath(
        '//div[@class="vc_tta-panels" and .//p[contains(./text(),"Hours")]]/div[.//p[contains(text(),"HOURS")]]'
    )
    for store in stores_list:
        location_name = "".join(store.xpath(".//h3/text()")).strip()
        store_number = "".join(store.xpath("@id")).strip()
        page_url = "https://boqueriarestaurant.com/#" + store_number
        locator_domain = website

        raw_address = (
            "".join(store.xpath('.//p[./strong[contains(text(),"Address:")]]//text()'))
            .strip()
            .replace("Address:", "")
            .strip()
        )
        formatted_addr = parser.parse_address_usa(raw_address)
        street_address = formatted_addr.street_address_1
        if formatted_addr.street_address_2:
            street_address = street_address + ", " + formatted_addr.street_address_2

        city = formatted_addr.city
        state = formatted_addr.state
        if city and city == "Nyc":
            state = "NY"

        zip = formatted_addr.postcode
        country_code = "US"

        phone = (
            "".join(store.xpath('.//p[./strong[contains(text(),"Phone:")]]//text()'))
            .strip()
            .replace("Phone:", "")
            .strip()
            .split("Note")[0]
            .strip()
            .encode("ascii", "ignore")
            .decode("utf-8")
        )

        location_type = "<MISSING>"

        hours = list(
            filter(
                str,
                [
                    x.strip()
                    for x in store.xpath(
                        ".//div[./p[contains(text(),'Hours')]]/p[2]//text()"
                    )
                ],
            )
        )
        if len(hours) <= 0:
            hours = list(
                filter(
                    str,
                    [
                        x.strip()
                        for x in store.xpath(
                            ".//div[./p[contains(text(),'HOURS')]]/p[1]/text()"
                        )
                    ],
                )
            )
        hours_of_operation = (
            "; ".join(hours)
            .strip()
            .split("; Please")[0]
            .strip()
            .replace("HOURS;", "")
            .strip()
        )

        latitude = "<MISSING>"
        longitude = "<MISSING>"

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
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.StoreNumberId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()

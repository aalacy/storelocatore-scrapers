# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal import sgpostal as parser


website = "capitalhairandbeauty.ie"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "authority": "www.capitalhairandbeauty.ie",
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
    base = "https://www.capitalhairandbeauty.ie"
    search_url = "https://www.capitalhairandbeauty.ie/stores"
    search_res = session.get(search_url, headers=headers)

    search_sel = lxml.html.fromstring(search_res.text)

    store_list = search_sel.xpath('//div[contains(@class,"all-list")]/div')

    for store in store_list:

        page_url = base + "".join(store.xpath(".//a[@title and not(./img)]/@href"))

        locator_domain = website

        log.info(page_url)
        store_res = session.get(page_url, headers=headers)
        store_sel = lxml.html.fromstring(store_res.text)

        store_info = list(
            filter(
                str,
                [
                    x.strip()
                    for x in store.xpath('.//div[contains(@class,"address")]//text()')
                ],
            )
        )

        raw_address = ", ".join(store_info[1:]).strip()
        formatted_addr = parser.parse_address_intl(raw_address)
        street_address = formatted_addr.street_address_1
        if formatted_addr.street_address_2:
            street_address = street_address + ", " + formatted_addr.street_address_2

        city = formatted_addr.city

        state = "<MISSING>"
        zip = store_info[-1].strip()
        country_code = "IE"

        location_name = "".join(
            store.xpath(".//a[@title and not(./img)]//text()")
        ).strip()
        if not city:
            city = location_name.split(" ")[0].strip()

        phone = list(
            filter(
                str,
                [
                    x.strip()
                    for x in store.xpath('.//div[contains(@class,"phone")]/a/text()')
                ],
            )
        )
        phone = phone[0].replace("(ex1)", "").strip()

        store_number = "<MISSING>"

        location_type = "<MISSING>"
        hours = list(
            filter(
                str,
                [
                    x.strip()
                    for x in store_sel.xpath('//div[@class="opening-times"]//text()')
                ],
            )
        )

        hours_of_operation = (
            "; ".join(hours[1:-1]).replace("day;", "day:").replace(":;", ":").strip()
        )

        try:
            latitude = store_res.text.split("lat:")[1].split(",")[0].strip()
        except:
            latitude = "<MISSING>"

        try:
            longitude = store_res.text.split("lng:")[1].split("};")[0].strip()
        except:
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

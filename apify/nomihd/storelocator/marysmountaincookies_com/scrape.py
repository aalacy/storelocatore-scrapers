# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgpostal import sgpostal as parser
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "marysmountaincookies.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    # Your scraper here
    search_url = "https://marysmountaincookies.com/locations/"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    stores = stores_sel.xpath('//section[@id="section_1"]//article/a/@href')

    for store_url in stores:
        if "http" in store_url:
            continue
        page_url = "https://marysmountaincookies.com" + store_url
        log.info(page_url)
        store_req = session.get(page_url, headers=headers)
        if "Opening Soon" in store_req.text or "COMING SOON" in store_req.text:
            continue
        store_sel = lxml.html.fromstring(store_req.text)

        locator_domain = website
        location_name = (
            " ".join(
                store_sel.xpath('//section[@id="section_1"]/article//header/h1/text()')
            )
            .strip()
            .replace("Welcome to", "")
            .strip()
        )

        temp_address = store_sel.xpath(
            '//section[@id="section_2"]//li[@class="icon-map"]'
        )
        raw_address = ""
        if len(temp_address) > 0:
            raw_address = ", ".join(temp_address[0].xpath("text()")).strip()

            if len(raw_address) <= 0:
                raw_address = ", ".join(temp_address[0].xpath("a/text()")).strip()

            if len(raw_address) <= 0:
                raw_address = ", ".join(temp_address[0].xpath("span/a/text()")).strip()
        raw_address = raw_address.replace("local store6055", "local store, 6055")
        formatted_addr = parser.parse_address_usa(raw_address)
        street_address = formatted_addr.street_address_1
        if formatted_addr.street_address_2:
            street_address = street_address + ", " + formatted_addr.street_address_2

        street_address = (
            street_address.replace("Rockbrook Village", "")
            .strip()
            .replace("Fashion Square Mall", "")
            .replace(", 912.05 Mi", "")
            .strip()
        )
        if " Local Store," in street_address:
            street_address = street_address.split(" Local Store,")[1].strip()
        if " Local Store" in street_address:
            street_address = street_address.split(" Local Store")[1].strip()

        city = formatted_addr.city
        state = formatted_addr.state
        zip = formatted_addr.postcode
        country_code = "US"

        phone = store_sel.xpath(
            '//section[@id="section_2"]//li[@class="icon-phone"][1]//text()'
        )
        if len(phone) > 0:
            phone = phone[0].strip()

        store_number = "<MISSING>"
        location_type = "<MISSING>"

        hours = store_sel.xpath('//section[@id="section_2"]//li')
        hours_list = []
        is_found = False
        for index in range(0, len(hours)):
            if is_found is False:
                if "icon-hours" == "".join(hours[index].xpath("@class")).strip():
                    is_found = True
                    hours_list.append(
                        "".join(hours[index].xpath(".//text()"))
                        .strip()
                        .replace("\n", "; ")
                        .strip()
                    )
            else:
                if len("".join(hours[index].xpath("@class")).strip()) <= 0:
                    hours_list.append(
                        "".join(hours[index].xpath(".//text()"))
                        .strip()
                        .replace("\n", "; ")
                        .strip()
                    )

        hour2 = "".join(
            store_sel.xpath(
                '//section[@id="section_2"]//ul[./li[@class="icon-hours"]]/text()'
            )
        ).strip()
        if hour2:
            hours_list.append(hour2)

        hours_of_operation = "; ".join(hours_list).strip()
        if "; We are open for delivery" in hours_of_operation:
            hours_of_operation = hours_of_operation.split("; We are open for delivery")[
                0
            ].strip()

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

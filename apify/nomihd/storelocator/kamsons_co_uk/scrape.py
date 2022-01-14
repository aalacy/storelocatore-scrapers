# -*- coding: utf-8 -*-
from sgrequests import SgRequests, SgRequestError
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal import sgpostal as parser

website = "kamsons.co.uk"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "authority": "www.kamsons.co.uk",
    "sec-ch-ua": '" Not;A Brand";v="99", "Google Chrome";v="97", "Chromium";v="97"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "referer": "https://www.kamsons.co.uk/branches/",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}

params = (("cn-reloaded", "1"),)


def fetch_data():
    # Your scraper here
    search_url = "https://www.kamsons.co.uk/branches/"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    stores = stores_sel.xpath('//div[@class="marker"]')
    for store in stores:

        page_url = "".join(store.xpath("a/@href")).strip()
        log.info(page_url)
        store_req = session.get(page_url, headers=headers)
        if isinstance(store_req, SgRequestError):
            log.error(page_url)
            continue
        store_sel = lxml.html.fromstring(store_req.text)
        store_number = "<MISSING>"
        locator_domain = website

        location_name = "".join(
            store_sel.xpath("//div[@class='o_content c_page-header']/h1/text()")
        ).strip()

        raw_info = store_sel.xpath('//div[contains(@class,"c_pharmacy-details")]//p')
        add_list = []
        if len(raw_info) > 0:
            raw_info = "".join(raw_info[0].xpath(".//text()")).strip().split(",")
            for raw in raw_info:
                if (
                    len("".join(raw).strip()) > 0
                    and "Pharmacy" not in "".join(raw).strip()
                ):
                    add_list.append("".join(raw).strip())

        raw_address = ", ".join(add_list).strip()

        formatted_addr = parser.parse_address_intl(raw_address)
        street_address = formatted_addr.street_address_1
        if formatted_addr.street_address_2:
            street_address = street_address + ", " + formatted_addr.street_address_2

        city = formatted_addr.city
        state = formatted_addr.state
        zip = formatted_addr.postcode
        if not zip:
            street_address = raw_address.split(",")[0].strip()
            city = raw_address.split(",")[-3].strip()
            zip = raw_address.split(",")[-1].strip()

        if street_address and street_address.isdigit():
            street_address = raw_address.split(",")[0].strip()

        country_code = "GB"
        location_type = "<MISSING>"
        phone = "".join(
            store_sel.xpath(
                '//div[contains(@class,"c_pharmacy-details")]//p//a[contains(@href,"tel:")]/text()'
            )
        ).strip()
        hours_of_operation = (
            "; ".join(
                store_sel.xpath(
                    '//div[contains(@class,"c_pharmacy-details")]//div[@class="c_opening-hours"]/p/text()'
                )
            )
            .strip()
            .split("Opening hours may vary")[0]
            .strip()
            .replace("\r\n", "")
            .replace("\n", "")
            .strip()
        )
        if len(hours_of_operation) > 0 and hours_of_operation[-1] == ";":
            hours_of_operation = "".join(hours_of_operation[:-1]).strip()

        latitude, longitude = (
            "".join(store.xpath("@data-lat")).strip(),
            "".join(store.xpath("@data-lng")).strip(),
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

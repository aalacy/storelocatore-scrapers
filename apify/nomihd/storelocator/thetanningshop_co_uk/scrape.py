# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgpostal import sgpostal as parser
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "thetanningshop.co.uk"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "authority": "thetanningshop.co.uk",
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
    search_url = "https://thetanningshop.co.uk/stores/"
    search_res = session.get(search_url, headers=headers)

    search_sel = lxml.html.fromstring(search_res.text)
    store_list = search_sel.xpath(
        '//p[strong/a and not(./preceding-sibling::h1="Franchise")]//a'
    )
    for store in store_list[:10]:
        page_url = store.xpath("./@href")[0].strip()

        locator_domain = website

        log.info(page_url)
        store_res = session.get(page_url, headers=headers)
        store_sel = lxml.html.fromstring(store_res.text)

        store_info = list(
            filter(
                str,
                [
                    x.strip()
                    for x in store_sel.xpath(
                        '//div[./preceding-sibling::h2[contains(.//text(),"Address")]]/p//text()'
                    )
                ],
            )
        )

        raw_address = " ".join(store_info)
        formatted_addr = parser.parse_address_intl(raw_address)
        street_address = formatted_addr.street_address_1
        if formatted_addr.street_address_2:
            street_address = street_address + ", " + formatted_addr.street_address_2

        city = formatted_addr.city
        if not city:
            city = raw_address.split(",")[-2]
        state = formatted_addr.state
        zip = formatted_addr.postcode
        if not zip:
            zip = raw_address.split(" ")[-2] + " " + raw_address.split(" ")[-1]

        country_code = "GB"

        location_name = "".join(
            store_sel.xpath("//div[@data-title]/@data-title")
        ).strip()

        raw_phone = list(
            filter(
                str,
                [
                    x.strip()
                    for x in store_sel.xpath(
                        '//a[contains(@href,"tel:")]//text() | //tr[td="Phone"]/td[2]/text()'
                    )
                ],
            )
        )
        phone = " ".join(raw_phone[1:]).strip()
        store_number = "<MISSING>"
        location_type = "<MISSING>"
        hours = list(
            filter(
                str,
                [
                    x.strip()
                    for x in store_sel.xpath(
                        '//div[./preceding-sibling::h4[contains(.//text(),"Opening")]]/table//text()'
                    )
                ],
            )
        )

        hours_of_operation = "; ".join(hours).replace("day;", "day:")
        latitude, longitude = (
            "".join(store_sel.xpath("//div[@data-lat]/@data-lat")),
            "".join(store_sel.xpath("//div[@data-lng]/@data-lng")),
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

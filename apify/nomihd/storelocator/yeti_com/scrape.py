# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
import re
from sgpostal import sgpostal as parser
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


website = "yeti.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "authority": "www.yeti.com",
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


def get_latlng(map_link):
    if "z/data" in map_link:
        lat_lng = map_link.split("@")[1].split("z/data")[0]
        latitude = lat_lng.split(",")[0].strip()
        longitude = lat_lng.split(",")[1].strip()
    elif "ll=" in map_link:
        lat_lng = map_link.split("ll=")[1].split("&")[0]
        latitude = lat_lng.split(",")[0]
        longitude = lat_lng.split(",")[1]
    elif "!2d" in map_link and "!3d" in map_link:
        latitude = map_link.split("!3d")[1].strip().split("!")[0].strip()
        longitude = map_link.split("!2d")[1].strip().split("!")[0].strip()
    else:
        latitude = "<MISSING>"
        longitude = "<MISSING>"
    return latitude, longitude


def fetch_data():
    # Your scraper here
    search_url = "https://www.yeti.com/en_US/yeti-store-locations.html"
    search_res = session.get(search_url, headers=headers)

    search_sel = lxml.html.fromstring(search_res.text)

    store_list = list(search_sel.xpath('//a[@class="content-card"]/@href'))

    for store in store_list:

        page_url = store
        locator_domain = website
        log.info(page_url)
        store_res = session.get(page_url, headers=headers)
        store_sel = lxml.html.fromstring(store_res.text)

        if "Coming Soon" in store_res.text or "We're Moving" in store_res.text:
            continue
        location_name = "".join(store_sel.xpath("//div/h1/text()"))

        store_info = list(
            filter(
                str,
                [
                    x.strip()
                    for x in store_sel.xpath('//p[./a[contains(@href,"tel")]]//text()')
                ],
            )
        )
        full_address = ""
        phone = ""
        if len(store_info) > 0:
            for phn_idx, x in enumerate(store_info):
                if bool(re.search("^[0-9-() ]{1,15}$", x)):
                    break

            full_address = store_info[:phn_idx] + store_info[phn_idx + 1 :]
            phone = store_info[phn_idx].strip()

        else:
            store_info = list(
                filter(
                    str,
                    [
                        x.strip()
                        for x in store_sel.xpath(
                            '//div[@class="page-content page-with-banner"]/p[position()<=2]/text()'
                        )
                    ],
                )
            )
            full_address = store_info

        if len(full_address) == 1:
            store_info = list(
                filter(
                    str,
                    [
                        x.strip()
                        for x in store_sel.xpath(
                            '//div[@class="page-content page-with-banner"]/p[position()<=2]/text()'
                        )
                    ],
                )
            )
            full_address = store_info

        if len(phone) <= 0:
            phone = "".join(store_sel.xpath('//a[contains(@href,"tel:")]/text()'))
        raw_address = " ".join(full_address).replace("\n", " ").split("(")[0]

        formatted_addr = parser.parse_address_usa(raw_address)
        street_address = formatted_addr.street_address_1
        if formatted_addr.street_address_2:
            street_address = street_address + ", " + formatted_addr.street_address_2

        city = formatted_addr.city
        state = formatted_addr.state
        zip = formatted_addr.postcode

        country_code = "US"

        store_number = "<MISSING>"

        location_type = "<MISSING>"

        hours = list(
            filter(
                str,
                [
                    x.strip()
                    for x in store_sel.xpath(
                        '//p[contains(.//text(),"Hours")]/following-sibling::p[count(following-sibling::p/u)=1]//text()'
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
                        for x in store_sel.xpath(
                            '//p[contains(.//text(),"Hours")]/following-sibling::p/text()'
                        )
                    ],
                )
            )
        hours_of_operation = "; ".join(hours).strip()
        if "regular business hours:;" in hours_of_operation:
            hours_of_operation = hours_of_operation.split("regular business hours:;")[
                1
            ].strip()

        hours_of_operation = (
            hours_of_operation.split("; Bar Open Effective")[0]
            .strip()
            .split("; Hey Scottsdale")[0]
            .strip()
        )

        map_link = "".join(store_sel.xpath('//iframe[contains(@src,"maps")]/@src'))

        latitude, longitude = get_latlng(map_link)

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

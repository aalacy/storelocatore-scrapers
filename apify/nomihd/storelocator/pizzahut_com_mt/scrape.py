# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import lxml.html

website = "pizzahut.com.mt"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-User": "?1",
    "Sec-Fetch-Dest": "document",
    "sec-ch-ua": '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
    "sec-ch-ua-mobile": "?0",
    "Accept-Language": "en-US,en-GB;q=0.9,en;q=0.8",
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
    elif "/@" in map_link:
        latitude = map_link.split("/@")[1].split(",")[0].strip()
        longitude = map_link.split("/@")[1].split(",")[1].strip()
    else:
        latitude = "<MISSING>"
        longitude = "<MISSING>"
    return latitude, longitude


def fetch_data():
    # Your scraper here
    search_url = "https://www.pizzahut.com.mt/"
    search_res = session.get(search_url, headers=headers)
    search_sel = lxml.html.fromstring(search_res.text)
    stores = search_sel.xpath('//div[./h5[text()="Customer service"]]/ul/li/a/@href')

    for store_url in stores:

        page_url = store_url
        log.info(page_url)
        store_req = session.get(page_url, headers=headers)
        store_sel = lxml.html.fromstring(store_req.text)

        locator_domain = website
        location_name = "".join(
            store_sel.xpath('//h2[@class="static-page__title"]/text()')
        ).strip()

        raw_info = store_sel.xpath(
            '//div[@class="restaurant_page_right"]/p[./strong[text()="Address and details"]]/text()'
        )

        add_list = []
        for index in range(1, len(raw_info)):
            if "\xa0" in "".join(raw_info[index]).strip():
                add_list.append(
                    "".join(raw_info[index]).strip().split("\xa0")[0].strip()
                )
                add_list.append(
                    "".join(raw_info[index]).strip().split("\xa0")[-1].strip()
                )
            else:
                add_list.append("".join(raw_info[index]).strip())

        street_address = ", ".join(add_list[:-2]).strip()
        city = add_list[-1].strip()
        state = "<MISSING>"
        zip = add_list[-2].strip()
        country_code = "MT"

        phone = "".join(
            store_sel.xpath(
                '//div[@class="restaurant_page_right"]/p[./strong[text()="Address and details"]]/a[contains(@href,"tel:")]/text()'
            )
        ).strip()
        store_number = "<MISSING>"

        location_type = "<MISSING>"

        hours_of_operation = "; ".join(
            store_sel.xpath(
                '//div[@class="restaurant_page_right"]/p[./strong[contains(text(),"Opening Hours") or contains(text(),"Opening hours")]]/text()'
            )
        ).strip()

        if len(hours_of_operation) <= 0:
            hours_of_operation = "; ".join(
                store_sel.xpath(
                    '//div[@class="restaurant_page_right"]/p[./strong[contains(text(),"Opening Hours") or contains(text(),"Opening hours")]]/following-sibling::p//text()'
                )
            ).strip()

        hours_of_operation = hours_of_operation.split("; Access")[0].strip()
        if len(hours_of_operation) <= 0:
            hours_of_operation = (
                "Sunday to Thursday: 11h – 21h; Friday & Saturday: 11h – 22h"
            )
        map_link = store_sel.xpath('//div[@class="shop-info__google-maps"]/iframe/@src')
        latitude, longitude = "<MISSING>", "<MISSING>"

        if len(map_link) > 0:
            map_link = map_link[0]

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

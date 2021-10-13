# -*- coding: utf-8 -*-
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import time

from sgrequests import SgRequests


website = "canadagoose.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()

cookies = {
    "dwac_cdSAUiaaio11EaaadnOiJrNbA7": "5PXJtINY4DgUY5D_iUF-ZsHIRxad5m4mvv0%3D|dw-only|||USD|false|Canada%2FEastern|true",
    "cqcid": "abHD59LYsfOy6WboYD9gghKG4L",
    "cquid": "||",
    "sid": "5PXJtINY4DgUY5D_iUF-ZsHIRxad5m4mvv0",
    "language": "en_US",
    "dwanonymous_b3aa5771d8435c67a1a8775183c875b2": "abHD59LYsfOy6WboYD9gghKG4L",
    "dwsid": "n_kCnAw_0Ax8iXxr57o8zrrEjD4SgV4S1hdk-JdwdSOzBNNLdVJYCN1QlCC9I0nwRnkdZNnvsAqZ4P6E26AZJQ==",
    "akm_bmfp_b2-ssn": "0OWGeTyYYR4KixKt2pAmM2DXcIcQzq2M9Eom6bJw5PqxZpX8uw2nbtzJcPXaOVW6JyRDl6GTD6EKPOi0Ey75dEfwV0LoamhNN1bYF8vvEErxnDXyobZHmqKyXT3ImnGdhNFJaRNe2myQn50OJPriMzpqQ",
    "akm_bmfp_b2": "0OWGeTyYYR4KixKt2pAmM2DXcIcQzq2M9Eom6bJw5PqxZpX8uw2nbtzJcPXaOVW6JyRDl6GTD6EKPOi0Ey75dEfwV0LoamhNN1bYF8vvEErxnDXyobZHmqKyXT3ImnGdhNFJaRNe2myQn50OJPriMzpqQ",
}


headers = {
    "Connection": "keep-alive",
    "sec-ch-ua": '"Chromium";v="94", "Google Chrome";v="94", ";Not A Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-User": "?1",
    "Sec-Fetch-Dest": "document",
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
    search_url = (
        "https://www.canadagoose.com/us/en/find-a-retailer/find-a-retailer.html"
    )

    response = session.get(search_url, headers=headers, cookies=cookies)
    search_sel = lxml.html.fromstring(response.text, "lxml")
    store_list = search_sel.xpath('//div[@class="store"]')
    log.info(f"Total Locations to crawl: {len(store_list)}")
    for store in store_list:

        page_url = store.xpath("./a/@href")[0].strip()
        log.info(f"Now crawling: {page_url}")
        response2 = session.get(page_url, headers=headers)
        time.sleep(3)
        store_sel = lxml.html.fromstring(response2.text, "lxml")

        locator_domain = website

        street_address = (
            " ".join(
                store_sel.xpath(
                    '//div[@class="store-info desktop"]//*[@itemprop="streetAddress"]//text()'
                )
            )
            .strip()
            .replace("\n", "")
            .strip()
        )
        city = (
            " ".join(
                store_sel.xpath(
                    '//div[@class="store-info desktop"]//*[@itemprop="addressLocality"]//text()'
                )
            )
            .strip()
            .replace("\n", "")
            .strip()
        )
        try:
            if city[-1] == ",":
                city = "".join(city[:-1]).strip()
        except:
            city = "<MISSING>"

        state = " ".join(
            store_sel.xpath(
                '//div[@class="store-info desktop"]//*[@itemprop="addressRegion"]//text()'
            )
        ).strip()
        zip = " ".join(
            store_sel.xpath(
                '//div[@class="store-info desktop"]//*[@itemprop="postalCode"]//text()'
            )
        ).strip()

        if len(street_address) <= 0:
            street_address = ", ".join(
                "".join(
                    store_sel.xpath(
                        '//div[@class="store-info desktop"]//*[@itemprop="address"]//text()'
                    )
                )
                .strip()
                .split(",")[:-1]
            ).strip()

        country_code = "<INACCESSIBLE>"
        if "Italy" == state:
            country_code = "IT"
            state = "<MISSING>"
        if "France" == state:
            country_code = "FR"
            state = "<MISSING>"
        if "Taiwan" == state:
            country_code = "TW"
            state = "<MISSING>"

        try:
            if state.split(" ")[0].strip().isdigit():
                zip = state.split(" ", 1)[0].strip()
                state = state.split(" ", 1)[-1].strip()
        except:
            pass
        location_name = "".join(
            store_sel.xpath(
                '//div[@class="store-info desktop"]//span[@itemprop="name"]/text()'
            )
        ).strip()

        phone = store_sel.xpath(
            '//div[@class="store-info desktop"]//*[@itemprop="telephone"]//text()'
        )
        if len(phone) > 0:
            phone = "".join(phone[0]).strip()

        store_number = "<MISSING>"

        location_type = "<MISSING>"

        hours = store_sel.xpath('//div[@class="store-info desktop"]/text()')
        hours_list = []
        for hour in hours:
            if len("".join(hour).strip()) > 0:
                hours_list.append("".join(hour).strip())

        if len(hours_list) <= 0:
            hours = store_sel.xpath(
                '//div[@class="store-info desktop"]/p[./meta[@itemprop="openingHours"]]/text()'
            )
            for hour in hours:
                if len("".join(hour).strip()) > 0:
                    hours_list.append("".join(hour).strip())

        if len(hours_list) <= 0:
            hours = store_sel.xpath('//div[@class="store-info desktop"]/p/text()')
            for hour in hours:
                if len("".join(hour).strip()) > 0:
                    hours_list.append("".join(hour).strip())

        hours_of_operation = "; ".join(hours_list).strip()
        if "," == hours_of_operation:
            hours_of_operation = "<MISSING>"

        map_link = "".join(
            store_sel.xpath(
                '//div[@class="store-info desktop"]//a[contains(@href,"maps")]/@href'
            )
        )

        latitude, longitude = get_latlng(map_link)

        raw_address = "<MISSING>"

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

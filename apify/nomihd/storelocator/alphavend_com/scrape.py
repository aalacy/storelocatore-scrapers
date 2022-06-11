# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal import sgpostal as parser
import lxml.html

website = "alphavend.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()

headers = {
    "sec-ch-ua": '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
    "sec-ch-ua-mobile": "?0",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
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

    search_url = "https://www.alphavend.com/"
    states_req = session.get(search_url, headers=headers)
    states_sel = lxml.html.fromstring(states_req.text)
    states = states_sel.xpath('//a[contains(text(),"More information...")]/@href')

    for store_url in states:
        page_url = "https://www.alphavend.com" + store_url
        log.info(page_url)
        store_req = session.get(page_url, headers=headers)
        stores_sel = lxml.html.fromstring(store_req.text)
        stores = stores_sel.xpath(
            '//section[contains(@class,"elementor-section elementor-inner-section elementor-element elementor-element-")]'
        )
        for store in stores:
            location_name = "".join(
                store.xpath(
                    ".//p[@class='elementor-heading-title elementor-size-default']/text()"
                )
            ).strip()
            location_type = "<MISSING>"
            locator_domain = website

            raw_address = (
                ", ".join(
                    store.xpath(
                        './/div[@class="elementor-widget-container"]/p[1]/text()'
                    )
                )
                .strip()
                .replace(",,", ",")
                .strip()
                .replace(", ,", ",")
                .strip()
            )
            formatted_addr = parser.parse_address_intl(raw_address)
            street_address = formatted_addr.street_address_1
            if formatted_addr.street_address_2:
                street_address = street_address + ", " + formatted_addr.street_address_2

            city = formatted_addr.city
            state = formatted_addr.state
            zip = formatted_addr.postcode

            country_code = "GB"
            store_number = "<MISSING>"
            phone = "<MISSING>"
            hours_list = store.xpath(
                './/div[@class="elementor-widget-container"]/p[2]//text()'
            )
            hours_of_operation = (
                (" ".join(hours_list).strip().split("Live updates")[0].strip())
                .encode("ascii", "replace")
                .decode("utf-8")
                .replace("?", "-")
                .strip()
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
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.CITY,
                    SgRecord.Headers.ZIP,
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

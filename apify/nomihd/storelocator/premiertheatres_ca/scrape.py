# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
import lxml.html
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape import sgpostal as parser

website = "premiertheatres.ca"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    # Your scraper here

    search_url = "https://www.premiertheatres.ca/theaters"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    stores = stores_sel.xpath('//a[contains(text(),"Website")]')
    loc_names = stores_sel.xpath(
        '//div[@id="theatresInfo"]/span[1]/text()'
    ) + stores_sel.xpath('//div[@id="theatresInfo"]/text()')
    loc_list = []
    for loc in loc_names:
        if len("".join(loc).strip()) > 0:
            loc_list.append("".join(loc).strip())

    for index in range(0, len(stores)):
        page_url = "".join(stores[index].xpath("@href")).strip()
        if "http" in page_url:
            continue
        page_url = "https://www.premiertheatres.ca/" + page_url + "/theaterinfo"
        log.info(page_url)
        store_req = session.get(page_url, headers=headers)
        store_sel = lxml.html.fromstring(store_req.text)
        location_name = loc_list[index]
        location_type = "<MISSING>"
        locator_domain = website

        raw_address = (
            "".join(
                store_sel.xpath(
                    "//div[@class='locationLeft']//span[@class='mdl-typography--font-light mdl-typography--subhead']/text()"
                )
            )
            .strip()
            .replace("\n", "")
            .strip()
        )
        formatted_addr = parser.parse_address_intl(raw_address)
        street_address = formatted_addr.street_address_1
        if formatted_addr.street_address_2:
            street_address = street_address + ", " + formatted_addr.street_address_2
        city = formatted_addr.city
        state = formatted_addr.state
        zipp = formatted_addr.postcode
        phone = store_sel.xpath(
            "//div[@class='locationRight']//span[@class='mdl-typography--font-light mdl-typography--subhead']/text()"
        )
        if len(phone) > 0:
            phone = phone[0].strip().replace("Phone:", "").strip()

        hours_of_operation = "<MISSING>"

        country_code = "CA"
        store_number = "<MISSING>"

        latitude = "<MISSING>"
        longitude = "<MISSING>"
        map_link = "".join(
            store_sel.xpath('//iframe[contains(@src,"maps/embed?")]/@src')
        ).strip()

        if len(map_link) > 0:
            latitude = map_link.split("!3d")[1].strip().split("!")[0].strip()
            longitude = map_link.split("!2d")[1].strip().split("!")[0].strip()

        yield SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zipp,
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
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()

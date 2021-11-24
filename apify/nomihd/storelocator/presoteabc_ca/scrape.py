# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape import sgpostal as parser

website = "presoteabc.ca"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "authority": "presoteabc.ca",
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
    search_url = "https://presoteabc.ca/store-locations/"
    search_res = session.get(search_url, headers=headers)

    search_sel = lxml.html.fromstring(search_res.text)

    store_list = list(
        set(
            search_sel.xpath(
                '//section[not(@id)]//div[@data-element_type="column"  and .//h3]'
            )
        )
    )

    for store in store_list:

        page_url = search_url
        locator_domain = website

        location_name = "".join(store.xpath(".//h3/text()"))

        full_address = list(
            filter(
                str,
                [
                    x.strip()
                    for x in store.xpath('.//h6[not(contains(text(),"Phone"))]//text()')
                ],
            )
        )

        if not full_address:
            raw_address = ""
        else:
            raw_address = " ".join(full_address)

        formatted_addr = parser.parse_address_intl(raw_address)
        street_address = formatted_addr.street_address_1
        if formatted_addr.street_address_2:
            street_address = street_address + ", " + formatted_addr.street_address_2

        city = formatted_addr.city
        state = formatted_addr.state
        state = "BC"
        zip = formatted_addr.postcode

        if street_address is not None and "Delta" in street_address:
            street_address = street_address.replace("Delta", "").strip()
            city = "Delta"

        country_code = "CA"

        store_number = "<MISSING>"
        phone = (
            "".join(
                list(
                    filter(
                        str,
                        [
                            x.strip()
                            for x in store.xpath(
                                './/h6[contains(text(),"Phone")]//text()'
                            )
                        ],
                    )
                )
            )
            .replace("Phone", "")
            .replace(":", "")
            .strip()
        )

        location_type = "<MISSING>"

        if not phone and not full_address:
            location_type = "TEMPORARILY CLOSED"

        hours = list(
            filter(
                str,
                [
                    x.strip()
                    for x in store.xpath(
                        './/*[contains(text(),"Hours")]/following-sibling::p//text()'
                    )
                ],
            )
        )

        hours_of_operation = "; ".join(hours).replace("day;", "day:").strip()

        latitude = (
            "".join(store.xpath(".//div/@data-locations")).split(",")[0].strip('[" ')
        )
        longitude = (
            "".join(store.xpath(".//div/@data-locations")).split(",")[1].strip('[" ')
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
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()

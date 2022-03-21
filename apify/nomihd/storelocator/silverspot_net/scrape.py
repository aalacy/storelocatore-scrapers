# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape import sgpostal as parser
import urllib.parse

website = "silverspot.net"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "authority": "silverspot.net",
    "cache-control": "max-age=0",
    "sec-ch-ua": '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
    "sec-ch-ua-mobile": "?0",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "referer": "https://silverspot.net/locations",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here
    search_url = "https://silverspot.net/locations"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    stores = stores_sel.xpath('//div[@class="location-container"]/a/@href')
    for store_url in stores:
        page_url = "https://silverspot.net" + store_url
        log.info(page_url)
        store_req = session.get(page_url, headers=headers)
        store_sel = lxml.html.fromstring(store_req.text)
        locator_domain = website

        location_name = "".join(
            store_sel.xpath(
                "//div[@class='location-detail__container']//div[@class='location-detail__name']/text()"
            )
        ).strip()
        raw_address = (
            "".join(
                store_sel.xpath(
                    '//div[@class="location-detail__location"]/a[contains(@href,"map")]/@href'
                )
            )
            .strip()
            .split("&destination=")[1]
            .strip()
        )

        raw_address = urllib.parse.unquote(raw_address.replace("+", " "))
        formatted_addr = parser.parse_address_intl(raw_address)
        street_address = formatted_addr.street_address_1
        if formatted_addr.street_address_2:
            street_address = street_address + ", " + formatted_addr.street_address_2

        city = formatted_addr.city
        state = formatted_addr.state
        zip = formatted_addr.postcode

        country_code = "US"

        store_number = "<MISSING>"

        phone = "".join(
            store_sel.xpath(
                "//div[@class='location-detail__location']//a[@class='location-detail__phone']/span/text()"
            )
        ).strip()
        location_type = "<MISSING>"
        hours = store_sel.xpath("//table//tr[position()>2]/td")
        hours_list = []
        for hour in hours:
            if len("".join(hour.xpath("text()")).strip()) > 0:
                hours_list.append("".join(hour.xpath("text()")).strip())

        hours_of_operation = "; ".join(hours_list).strip()
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
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()

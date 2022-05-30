# -*- coding: utf-8 -*-
from sgrequests import SgRequests, SgRequestError
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal import sgpostal as parser

website = "sunrisetreatmentcenter.net"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()

headers = {
    "authority": "www.sunrisetreatmentcenter.net",
    "cache-control": "max-age=0",
    "sec-ch-ua": '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
    "sec-ch-ua-mobile": "?0",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "cross-site",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.sunrisetreatmentcenter.net/"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    stores = stores_sel.xpath(
        '//div[@class="nav-link w-dropdown"][.//div[contains(text(),"Locations")]]//a/@href'
    )
    for store_url in stores:
        if "/staff/corporate" == store_url:
            continue
        page_url = "https://www.sunrisetreatmentcenter.net" + store_url
        log.info(page_url)
        store_req = session.get(page_url, headers=headers)
        if isinstance(store_req, SgRequestError):
            continue
        store_sel = lxml.html.fromstring(store_req.text)

        locator_domain = website
        location_name = "".join(
            store_sel.xpath('//div[@class="div-text"]/h1/text()')
        ).strip()

        raw_info = list(
            filter(
                str,
                [
                    x.strip()
                    for x in store_sel.xpath(
                        '//div[@class="centered-container w-container"]/p/text()'
                    )
                ],
            )
        )
        raw_address = (
            raw_info[0]
            .strip()
            .replace("Address:", "")
            .strip()
            .replace("\xa0", " ")
            .strip()
        )

        formatted_addr = parser.parse_address_usa(raw_address)
        street_address = formatted_addr.street_address_1
        if street_address:
            if formatted_addr.street_address_2:
                street_address = street_address + ", " + formatted_addr.street_address_2
        else:
            if formatted_addr.street_address_2:
                street_address = formatted_addr.street_address_2

        city = formatted_addr.city
        state = formatted_addr.state
        zip = formatted_addr.postcode

        country_code = "US"

        store_number = "<MISSING>"
        phone = raw_info[1].strip().replace("Phone:", "").strip()
        location_type = "<MISSING>"

        hours_of_operation = "<MISSING>"

        latitude = (
            "".join(store_sel.xpath("//div[@data-widget-latlng]/@data-widget-latlng"))
            .strip()
            .split(",")[0]
            .strip()
        )
        longitude = (
            "".join(store_sel.xpath("//div[@data-widget-latlng]/@data-widget-latlng"))
            .strip()
            .split(",")[-1]
            .strip()
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

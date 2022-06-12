# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgpostal import sgpostal as parser
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "fayettepartsservice.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.fayettepartsservice.com/locations"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    stores = stores_sel.xpath('//li[./a[contains(@href,"/locations")]]/ul/li/a/@href')

    for store_url in stores:
        page_url = "https://www.fayettepartsservice.com" + store_url
        log.info(page_url)
        store_req = session.get(page_url, headers=headers)
        store_sel = lxml.html.fromstring(store_req.text)

        locator_domain = website
        location_name = "".join(store_sel.xpath("//h1/span/text()")).strip()

        latitude = "".join(
            store_sel.xpath('//div[@data-type="inlineMap"]/@data-lat')
        ).strip()
        longitude = "".join(
            store_sel.xpath('//div[@data-type="inlineMap"]/@data-lng')
        ).strip()

        raw_address = ""
        if "/newpage7fe6dbf7" in page_url:
            raw_address = "531 Rodi Rd, Pittsburgh, PA"
            latitude = "<MISSING>"
            longitude = "<MISSING>"
        else:
            raw_address = "".join(
                store_sel.xpath('//div[@data-type="inlineMap"]/@data-address')
            ).strip()
        formatted_addr = parser.parse_address_usa(raw_address)
        street_address = formatted_addr.street_address_1
        if formatted_addr.street_address_2:
            street_address = street_address + ", " + formatted_addr.street_address_2

        city = formatted_addr.city
        raw_city = formatted_addr.city
        if "," in city:
            city = city.split(",")[0].strip()

        state = formatted_addr.state
        if state is None:
            if "," in raw_city:
                state = raw_city.split(",")[1].strip()
        else:
            if "," in state:
                state = state.split(",")[0].strip()

        zip = formatted_addr.postcode
        country_code = formatted_addr.country
        if country_code == "United States":
            country_code = "US"
        store_number = "<MISSING>"
        location_type = "<MISSING>"

        phone = (
            "".join(store_sel.xpath('//a[@type="call"]/@href'))
            .strip()
            .replace("tel:", "")
            .strip()
        )
        if len(phone) <= 0:
            phone = "".join(
                store_sel.xpath(
                    '//span[contains(@ data-inline-binding,".phone.")]/text()'
                )
            ).strip()
        hours_of_operation = ""
        sections = store_sel.xpath("//span")
        for sec in sections:
            if "am " in "".join(sec.xpath("text()")).strip():
                hours_of_operation = "; ".join(sec.xpath("text()")).strip()

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

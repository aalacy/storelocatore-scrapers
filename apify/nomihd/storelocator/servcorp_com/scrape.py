# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal import sgpostal as parser

website = "servcorp.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "Connection": "keep-alive",
    "Cache-Control": "max-age=0",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="98", "Google Chrome";v="98"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.82 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Sec-Fetch-Site": "cross-site",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-User": "?1",
    "Sec-Fetch-Dest": "document",
    "Accept-Language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here
    countries_req = session.get(
        "https://www.servcorp.com/en/locations/worldwide-locations/", headers=headers
    )
    countries_sel = lxml.html.fromstring(countries_req.text)
    countries = countries_sel.xpath('//article[@class="col-sm-6 col-md-4"]')
    for country in countries:
        country_code = "".join(
            country.xpath('div[@class="property-tile"]/header/text()')
        ).strip()
        search_url = "".join(
            country.xpath('div[@class="property-tile"]/a/@href')
        ).strip()
        if "Australia" in country_code:
            search_url = "https://www.servcorp.com.au/en/locations/"

        if "Japan" in country_code:
            search_url = "https://www.servcorp.co.jp/en/office-finder/"

        log.info(search_url)
        stores_req = session.get(search_url, headers=headers)
        stores_sel = lxml.html.fromstring(stores_req.text)
        stores = stores_sel.xpath(
            '//div[@class="location-listing-desktop"]/article[./div[@class="property-tile"]/header]'
        )
        if len(stores) <= 0:
            stores = stores_sel.xpath('//article[@class="col-sm-6 col-md-4"]')
        for store in stores:
            page_url = (
                search_url.split("/en")[0].strip()
                + "".join(
                    store.xpath('div[@class="property-tile"]/header/a/@href')
                ).strip()
            )
            locator_domain = website
            location_name = "".join(
                store.xpath('div[@class="property-tile"]/header/a/text()')
            ).strip()

            raw_address = ", ".join(
                list(
                    filter(
                        str,
                        [
                            x.strip()
                            for x in store.xpath(
                                './/div[@class="property-address"]//text()'
                            )
                        ],
                    )
                )
            ).strip()
            formatted_addr = parser.parse_address_intl(raw_address)
            street_address = formatted_addr.street_address_1
            if formatted_addr.street_address_2:
                street_address = street_address + ", " + formatted_addr.street_address_2

            city = formatted_addr.city
            state = formatted_addr.state
            zip = formatted_addr.postcode

            store_number = "<MISSING>"
            phone = "".join(store.xpath('.//*[@class="phone-btn"]//text()')).strip()

            location_type = "<MISSING>"
            hours_of_operation = "<MISSING>"

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

# -*- coding: utf-8 -*-
from sgrequests import SgRequests, SgRequestError
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal import sgpostal as parser

website = "fredperry.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "authority": "www.fredperry.com",
    "sec-ch-ua": '" Not;A Brand";v="99", "Google Chrome";v="97", "Chromium";v="97"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "navigate",
    "sec-fetch-dest": "document",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.fredperry.com/us/shop-finder"
    with SgRequests(dont_retry_status_codes=([404])) as session:
        countries_req = session.get(search_url, headers=headers)
        countries_sel = lxml.html.fromstring(countries_req.text)
        countries = countries_sel.xpath(
            '//select[@id="location-selector"]/option[position()>1]'
        )
        for country in countries:
            country_code = "".join(country.xpath("text()")).strip()
            country_url = (
                "https://www.fredperry.com/us/shop-finder/location/"
                + "".join(country.xpath("@value")).strip()
            )
            stores_req = session.get(country_url, headers=headers)
            stores_sel = lxml.html.fromstring(stores_req.text)
            types = stores_sel.xpath(
                '//div[@class="store-list"]/div[@class="shop-container"]'
            )
            for typ in types:
                location_type = "".join(typ.xpath("h2/text()")).strip()
                if "Stockists" in location_type:
                    continue

                stores = typ.xpath('div[@class="store"]')
                for store in stores:
                    if (
                        "permanently closed"
                        in "".join(
                            store.xpath('span[@class="shop-notice"]/text()')
                        ).strip()
                    ):
                        continue
                    page_url = "".join(
                        store.xpath(
                            "div[@class='actions']/a[@class='visit-store']/@href"
                        )
                    ).strip()
                    log.info(page_url)
                    store_req = session.get(page_url, headers=headers)
                    if isinstance(store_req, SgRequestError):
                        continue
                    store_sel = lxml.html.fromstring(store_req.text)
                    store_number = "<MISSING>"
                    locator_domain = website

                    location_name = (
                        " ".join(store_sel.xpath("//h2[@id='shop-name']/text()"))
                        .strip()
                        .replace("  ", " ")
                        .strip()
                    )

                    raw_info = store_sel.xpath(
                        '//div[@data-title="Address"]/address/span/text()'
                    )

                    raw_address = ", ".join(raw_info).strip()
                    formatted_addr = parser.parse_address_intl(raw_address)
                    street_address = formatted_addr.street_address_1
                    if formatted_addr.street_address_2:
                        street_address = (
                            street_address + ", " + formatted_addr.street_address_2
                        )

                    city = formatted_addr.city
                    state = formatted_addr.state
                    zip = formatted_addr.postcode

                    phone = "".join(
                        store_sel.xpath('//div[@data-title="Telephone"]/a/text()')
                    ).strip()

                    hours = store_sel.xpath(
                        '//div[@data-title="Opening Times"]/div[@class="table"]/div'
                    )
                    hours_list = []
                    for hour in hours:
                        day = "".join(hour.xpath("div[1]//text()")).strip()
                        time = "".join(hour.xpath("div[2]//text()")).strip()
                        hours_list.append(day + ":" + time)

                    hours_of_operation = ";".join(hours_list).strip()
                    latitude, longitude = (
                        "".join(store.xpath("@data-lat")).strip(),
                        "".join(store.xpath("@data-long")).strip(),
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

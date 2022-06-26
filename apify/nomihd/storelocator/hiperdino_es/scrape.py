# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "hiperdino.es"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "authority": "www.hiperdino.es",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="102", "Google Chrome";v="102"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "cross-site",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36",
}


def fetch_data():
    # Your scraper here

    search_url = "https://www.hiperdino.es/tiendas"
    with SgRequests() as session:
        search_res = session.get(search_url, headers=headers)
        search_sel = lxml.html.fromstring(search_res.text)
        islands = search_sel.xpath('//select[@name="island"]/option/@value')
        for isl in islands:
            isl_url = f"https://www.hiperdino.es/c9504/tiendas/index/result/?island={isl}&city=&address="
            while True:
                log.info(isl_url)
                isl_req = session.get(isl_url, headers=headers)
                isl_sel = lxml.html.fromstring(isl_req.text)

                stores = isl_sel.xpath('//span[@class="flex-item text-postal"]/a/@href')
                for store_url in stores:

                    page_url = store_url
                    log.info(page_url)
                    store_req = session.get(page_url, headers=headers)
                    store_sel = lxml.html.fromstring(store_req.text)

                    locator_domain = website

                    location_name = "".join(
                        store_sel.xpath(
                            '//div[@class="page-corporate__tiendas"]//h3[@class="sub__title"]/text()'
                        )
                    ).strip()

                    raw_address = (
                        "".join(
                            store_sel.xpath(
                                '//div[contains(@class,"tienda__item tienda-")]/p[.//i[@class="icon icon-location-pin"]]/text()'
                            )
                        )
                        .strip()
                        .split(",")
                    )

                    log.info(raw_address)
                    street_address = "".join(raw_address[:-2]).strip()
                    city = raw_address[-1].strip()
                    state = "<MISSING>"
                    zip = raw_address[-2].strip()

                    country_code = "ES"

                    store_number = "".join(
                        store_sel.xpath(
                            '//div[contains(@class,"tienda__item tienda-")]/@data-store'
                        )
                    ).strip()

                    phone = "".join(
                        store_sel.xpath(
                            '//div[contains(@class,"tienda__item tienda-")]/p[.//i[@class="icon icon-contact"]]/text()'
                        )
                    ).strip()

                    location_type = "<MISSING>"

                    hours_of_operation = "".join(
                        store_sel.xpath(
                            '//div[contains(@class,"tienda__item tienda-")]/p[.//i[@class="icon icon-clock"]]/text()'
                        )
                    ).strip()

                    latitude, longitude = (
                        "".join(
                            store_sel.xpath(
                                '//div[contains(@class,"tienda__item tienda-")]/@data-lat'
                            )
                        ).strip(),
                        "".join(
                            store_sel.xpath(
                                '//div[contains(@class,"tienda__item tienda-")]/@data-lon'
                            )
                        ).strip(),
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
                    )

                next_page = "".join(
                    isl_sel.xpath(
                        '//div[@class="table-container--pagination__icon-right flex-item"]//a/@href'
                    )
                ).strip()
                if len(next_page) <= 0 or next_page == "#":
                    break
                else:
                    isl_url = next_page


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

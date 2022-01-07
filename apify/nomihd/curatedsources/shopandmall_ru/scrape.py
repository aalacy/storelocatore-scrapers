# -*- coding: utf-8 -*-
from sgrequests import SgRequests, SgRequestError
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "shopandmall.ru"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "Connection": "keep-alive",
    "Cache-Control": "max-age=0",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Sec-Fetch-Site": "cross-site",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-User": "?1",
    "Sec-Fetch-Dest": "document",
    "Accept-Language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here

    search_url = "https://shopandmall.ru/torgovye-centry"

    with SgRequests() as session:
        while True:
            search_res = session.get(search_url, headers=headers)
            stores_sel = lxml.html.fromstring(search_res.text)
            stores = stores_sel.xpath('//div[@class="center_in_result"]')

            for store in stores:
                locator_domain = website
                page_url = (
                    "https://shopandmall.ru"
                    + "".join(
                        store.xpath('div[@class="header-in-list"]/a/@href')
                    ).strip()
                )
                log.info(page_url)
                store_req = session.get(page_url, headers=headers)

                if isinstance(store_req, SgRequestError):
                    continue

                store_sel = lxml.html.fromstring(store_req.text)

                location_name = "".join(
                    store.xpath('div[@class="header-in-list"]/a/text()')
                ).strip()
                location_type = "".join(
                    store.xpath('div[@class="header-in-list"]/text()')
                ).strip()

                street_address = "".join(
                    store.xpath('p[@class="adress_center"]/text()')
                ).strip()
                city = (
                    "".join(store.xpath('p[@class="adress_center"]/b/text()'))
                    .strip()
                    .split("(")[0]
                    .strip()
                )

                state = "<MISSING>"
                if (
                    "("
                    in "".join(
                        store.xpath('p[@class="adress_center"]/b/text()')
                    ).strip()
                ):
                    state = (
                        "".join(store.xpath('p[@class="adress_center"]/b/text()'))
                        .strip()
                        .split("(")[1]
                        .strip()
                        .split(")")[0]
                        .strip()
                    )

                zip = "<MISSING>"
                country_code = "RU"

                phone = "<MISSING>"

                hours_of_operation = (
                    "".join(
                        store_sel.xpath(
                            '//li[./div[contains(text(),"Время работы ТЦ:")]]/div[@class="i-view"]//text()'
                        )
                    )
                    .strip()
                    .split("\n")[0]
                    .strip()
                )
                log.info(hours_of_operation)

                store_number = "<MISSING>"
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
                )

            next_page = stores_sel.xpath(
                '//a[./li[contains(text(),"следующая")]]/@href'
            )
            if len(next_page) > 0:
                search_url = "https://shopandmall.ru" + next_page[0]
                log.info(search_url)
            else:
                break


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

# -*- coding: utf-8 -*-
from sgrequests import SgRequests, SgRequestError
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "smashburger.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36",
}


def fetch_data():
    # Your scraper here

    urls = [
        "https://smashburger.com/locations/us/",
        "https://smashburger.com/locations/ca/",
    ]

    with SgRequests(dont_retry_status_codes=([404])) as session:
        for search_url in urls:
            search_res = session.get(search_url, headers=headers)
            search_sel = lxml.html.fromstring(search_res.text)

            stores = search_sel.xpath('//article[.//h3[@class="store-title"]]')

            for store in stores:

                page_url = "".join(
                    store.xpath('.//h3[@class="store-title"]/a/@href')
                ).strip()
                log.info(page_url)

                store_res = session.get(page_url, headers=headers)
                if isinstance(store_res, SgRequestError):
                    continue

                if page_url != store_res.url:
                    locator_domain = website

                    location_name = page_url.split("/")[-2]

                    raw_address = "<MISSING>"

                    add_list = list(
                        filter(str, [x.strip() for x in store.xpath(".//text()")])
                    )
                    street_address = ", ".join(add_list[:-2]).strip()

                    city = add_list[-2].strip().split(" ", 1)[0].strip()
                    state = (
                        add_list[-2]
                        .strip()
                        .split(" ", 1)[1]
                        .strip()
                        .split(",")[0]
                        .strip()
                    )
                    zip = (
                        add_list[-2]
                        .strip()
                        .split(" ", 1)[1]
                        .strip()
                        .split(",")[-1]
                        .strip()
                    )

                    country_code = page_url.split("locations/")[1].split("/")[0].upper()

                    store_number = "<MISSING>"

                    phone = add_list[-1]
                    location_type = "<MISSING>"
                    hours_of_operation = "<MISSING>"

                    latitude, longitude = "<MISSING>", "<MISSING>"

                else:
                    store_sel = lxml.html.fromstring(store_res.text)

                    locator_domain = website

                    location_name = page_url.split("/")[-2]

                    raw_address = "<MISSING>"

                    add_list = store_sel.xpath("//div[@data-lat]/div/span/text()")
                    street_address = ", ".join(add_list[:-3]).strip()

                    city = add_list[-3].strip()
                    state = add_list[-2].strip()
                    zip = add_list[-1].strip()

                    country_code = page_url.split("locations/")[1].split("/")[0].upper()

                    store_number = "<MISSING>"

                    phone = "".join(
                        store_sel.xpath('//a[@itemprop="telephone"]//text()')
                    ).strip()
                    if not phone:
                        phone = "".join(
                            store_sel.xpath(
                                '//div[./h4[contains(text(),"Phone")]]/p/a[contains(@href,"tel:")]//text()'
                            )
                        ).strip()
                    location_type = "<MISSING>"
                    hours = list(
                        filter(
                            str,
                            [
                                x.strip()
                                for x in store_sel.xpath(
                                    '//div[h4/text()="Hours"]/p//text()'
                                )
                            ],
                        )
                    )
                    hours_of_operation = (
                        "; ".join(hours).strip().replace("day;", "day:")
                    )

                    latitude, longitude = (
                        "".join(store_sel.xpath("//div[@data-lat]/@data-lat")),
                        "".join(store_sel.xpath("//div[@data-lat]/@data-lng")),
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

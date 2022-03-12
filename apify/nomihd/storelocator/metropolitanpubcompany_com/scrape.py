# -*- coding: utf-8 -*-
from sgrequests import SgRequests, SgRequestError
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "metropolitanpubcompany.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
}


def get_latlng(map_link):
    if "z/data" in map_link:
        lat_lng = map_link.split("@")[1].split("z/data")[0]
        latitude = lat_lng.split(",")[0].strip()
        longitude = lat_lng.split(",")[1].strip()
    elif "ll=" in map_link:
        lat_lng = map_link.split("ll=")[1].split("&")[0]
        latitude = lat_lng.split(",")[0]
        longitude = lat_lng.split(",")[1]
    elif "!2d" in map_link and "!3d" in map_link:
        latitude = map_link.split("!3d")[1].strip().split("!")[0].strip()
        longitude = map_link.split("!2d")[1].strip().split("!")[0].strip()
    elif "/@" in map_link:
        latitude = map_link.split("/@")[1].split(",")[0].strip()
        longitude = map_link.split("/@")[1].split(",")[1].strip()
    else:
        latitude = "<MISSING>"
        longitude = "<MISSING>"
    return latitude, longitude


def fetch_data():
    # Your scraper here

    search_url = "https://www.metropolitanpubcompany.com/our-pubs/"

    with SgRequests(dont_retry_status_codes=([404])) as session:
        search_res = session.get(search_url, headers=headers)

        search_sel = lxml.html.fromstring(search_res.text)

        categories = search_sel.xpath('//section[@class="cat-section"]/a[h3]')

        for _, category in enumerate(categories, 1):

            category_name = "".join(category.xpath("./h3/text()"))
            log.info(category_name)

            category_url = "".join(category.xpath("./@href"))
            log.info(category_url)

            category_res = session.get(category_url, headers=headers)
            category_sel = lxml.html.fromstring(category_res.text)
            stores = category_sel.xpath('//section[@class="wppl-single-result"]')

            for no, store in enumerate(stores, 1):

                locator_domain = website
                page_url = "".join(store.xpath("./a[h2]/@href"))
                log.info(page_url)

                store_res = session.get(page_url, headers=headers)
                if isinstance(store_res, SgRequestError):
                    continue
                store_sel = lxml.html.fromstring(store_res.text)

                store_number = "<MISSING>"

                location_name = "".join(store.xpath(".//h2/text()")).strip()
                location_type = category_name

                raw_address = "<MISSING>"

                street_address = (
                    ", ".join(
                        store_sel.xpath(
                            '//div[@class="Box"]//div[@class="street-block"]/div//text()'
                        )
                    )
                    .strip(" ,")
                    .strip()
                )
                if len(street_address) <= 0:
                    street_address = ", ".join(
                        store_sel.xpath('//div[@class="street-block"]//text()')
                    ).strip()

                city = "".join(
                    store_sel.xpath(
                        '//div[@class="Box"]//div[@class="locality"]/text()'
                    )
                )
                if len(city) <= 0:
                    city = "".join(
                        store_sel.xpath('//div[@class="locality"]/text()')
                    ).strip()

                state = "<MISSING>"
                zip = "".join(
                    store_sel.xpath(
                        '//div[@class="Box"]//div[@class="postal-code"]/text()'
                    )
                )
                if len(zip) <= 0:
                    zip = "".join(
                        store_sel.xpath('//div[@class="postal-code"]/text()')
                    ).strip()

                country_code = "GB"

                phone = store_sel.xpath(
                    '//div[@class="LocationInfo-telephone"]/div[@class="LocationInfo-value"]/text()'
                )
                if len(phone) > 0:
                    phone = phone[0]
                else:
                    phone = "<MISSING>"

                hours = list(
                    filter(
                        str,
                        [
                            x.strip()
                            for x in store_sel.xpath(
                                '//div[@class="LocationInfo LocationInfo--openingHours"]//span//text()'
                            )
                        ],
                    )
                )
                if len(hours) <= 0:
                    hours = list(
                        filter(
                            str,
                            [
                                x.strip()
                                for x in store_sel.xpath(
                                    '//div[@class="LocationInfo LocationInfo--foodHours"]//span//text()'
                                )
                            ],
                        )
                    )
                hours_of_operation = (
                    "; ".join(hours).replace("day; ", "day: ").replace(":;", ":")
                )

                map_link = "".join(store_sel.xpath('//a[contains(@href,"maps")]/@href'))

                latitude, longitude = get_latlng(map_link)

                if (
                    "https://www.metropolitanpubcompany.com/best-pubs-for-rugby"
                    in page_url
                ):
                    continue

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

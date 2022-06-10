# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgpostal import sgpostal as parser
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "pizza-la.co.jp"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "authority": "www.pizza-la.co.jp",
    "sec-ch-ua": '" Not;A Brand";v="99", "Google Chrome";v="97", "Chromium";v="97"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "none",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "accept-language": "en-US,en;q=0.9,ar;q=0.8",
}


def fetch_data():
    # Your scraper here
    base = "https://www.pizza-la.co.jp/"
    search_url = "https://www.pizza-la.co.jp/TenpoTop.aspx"

    with SgRequests() as session:
        search_res = session.get(search_url, headers=headers)
        log.info(search_res)

        search_sel = lxml.html.fromstring(search_res.text)

        areas = search_sel.xpath("//article//ul//a")

        for no, area in enumerate(areas, 1):  # @TODO update remove slice
            log.info("area")
            locator_domain = website

            area_url = base + "".join(area.xpath("./@href")).strip()
            log.info(area_url)
            area_res = session.get(area_url, headers=headers)
            area_sel = lxml.html.fromstring(area_res.text)

            perfectures = area_sel.xpath("//article//ul//a[@href]")

            for perfecture in perfectures:  # @TODO update remove slice
                log.info("perfecture")
                perfecture_url = base + "".join(perfecture.xpath("./@href")).strip()
                log.info(perfecture_url)

                perfecture_res = session.get(perfecture_url, headers=headers)
                perfecture_sel = lxml.html.fromstring(perfecture_res.text)

                city_initials = perfecture_sel.xpath("//article//ul//a[@href]")

                for city_initial in city_initials:  # @TODO update remove slice
                    log.info("city_initial")
                    city_initial_url = (
                        base + "".join(city_initial.xpath("./@href")).strip()
                    )
                    log.info(city_initial_url)

                    city_initial_res = session.get(city_initial_url, headers=headers)
                    city_initial_sel = lxml.html.fromstring(city_initial_res.text)
                    cities = city_initial_sel.xpath(
                        '//article[@id="searchArea"]//li/a[@href]'
                    )
                    log.info(
                        len(cities)
                    )  # @TODO HERE WE GET 0 list because jp symbol didn't form correct url as we get from web.

                    for _city in cities:
                        log.info("city")
                        city_url = base + "".join(_city.xpath("./@href")).strip()
                        log.info(city_url)

                        city_res = session.get(city_url, headers=headers)
                        city_sel = lxml.html.fromstring(city_res.text)

                        first_letter_next_addresses = city_sel.xpath(
                            "//article//ul//a[@href]"
                        )

                        for flna in first_letter_next_addresses:
                            log.info("first_letter_next_address_name")
                            flna_url = base + "".join(flna.xpath("./@href")).strip()
                            log.info(flna_url)

                            flna_res = session.get(flna_url, headers=headers)
                            flna_sel = lxml.html.fromstring(flna_res.text)

                            next_address_names = flna_sel.xpath(
                                "//article//ul//a[@href]"
                            )

                            for next_address_name in next_address_names:
                                log.info("next_address_name")
                                next_address_name_url = (
                                    base
                                    + "".join(
                                        next_address_name.xpath("./@href")
                                    ).strip()
                                )
                                log.info(next_address_name_url)

                                next_address_name_res = session.get(
                                    next_address_name_url, headers=headers
                                )
                                next_address_name_sel = lxml.html.fromstring(
                                    next_address_name_res.text
                                )

                                stores = next_address_name_sel.xpath(
                                    "//article//ul//a[@href]"
                                )

                                for store in stores:
                                    log.info("address/store")
                                    page_url = (
                                        base + "".join(store.xpath("./@href")).strip()
                                    )
                                    log.info(page_url)

                                    store_res = session.get(page_url, headers=headers)
                                    store_sel = lxml.html.fromstring(store_res.text)

                                    location_name = " ".join(
                                        store_sel.xpath('//h1[@class="title"]//text()')
                                    ).strip()

                                    location_type = "<MISSING>"

                                    store_info = list(
                                        filter(
                                            str,
                                            [
                                                x.strip()
                                                for x in store_sel.xpath(
                                                    "//table//tr[last()]/td//text()"
                                                )
                                            ],
                                        )
                                    )
                                    raw_address = ", ".join(store_info)
                                    log.info(raw_address)
                                    formatted_addr = parser.parse_address_intl(
                                        raw_address
                                    )
                                    street_address = formatted_addr.street_address_1
                                    if formatted_addr.street_address_2:
                                        street_address = (
                                            street_address
                                            + ", "
                                            + formatted_addr.street_address_2
                                        )

                                    if street_address is not None:
                                        street_address = street_address.replace(
                                            "Ste", "Suite"
                                        )

                                    city = formatted_addr.city

                                    state = formatted_addr.state

                                    zip = formatted_addr.postcode

                                    country_code = "JP"

                                    phone = "".join(
                                        store_sel.xpath(
                                            "//table//tr[last()-1]/td//text()"
                                        )
                                    )

                                    hours = list(
                                        filter(
                                            str,
                                            [
                                                x.strip()
                                                for x in store_sel.xpath(
                                                    "//table//tr[last()-2]/td//text()"
                                                )
                                            ],
                                        )
                                    )
                                    if hours:

                                        hours_of_operation = (
                                            "; ".join(hours[:1])
                                            .strip()
                                            .replace("day; ", "day: ")
                                            .replace("Show More", "")
                                            .strip("; ")
                                        )
                                    else:
                                        hours_of_operation = "<MISSING>"

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

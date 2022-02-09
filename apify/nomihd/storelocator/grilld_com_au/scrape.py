# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "grilld.com.au"
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

    search_url = "https://www.grilld.com.au/locations"

    with SgRequests() as session:
        search_res = session.get(search_url, headers=headers)

        search_sel = lxml.html.fromstring(search_res.text)
        states = search_sel.xpath('//a[contains(@class,"js-tracking-click")]')

        for no, state in enumerate(states, 1):

            locator_domain = website

            state_url = "".join(state.xpath("./@href"))
            if "restaurants/" not in state_url:
                continue

            log.info(state_url)

            state_res = session.get(state_url, headers=headers)

            state_sel = lxml.html.fromstring(state_res.text)

            stores = state_sel.xpath('//li[@class="restaurant-list__item"]')

            store_len = len(stores)
            if not stores:
                stores = ["state url is of store url"]

            for store in stores:
                is_url_broken = False
                if store_len > 0:

                    store_url = "".join(store.xpath(".//a/@href"))
                    log.info(store_url)

                    store_res = session.get(store_url, headers=headers)
                    if store_res.status_code not in [200, 302]:
                        log.info("SOME PAGE ERROR")
                        is_url_broken = True

                        location_name = "".join(
                            store.xpath(
                                ".//span[@class='restaurant-list__item__heading']/text()"
                            )
                        ).strip()
                        location_type = "<MISSING>"

                        raw_info = store.xpath(
                            './/div[@class="restaurant-list__item__address"]/text()'
                        )
                        street_address = raw_info[0].replace(",", "").strip()
                        city = " ".join(raw_info[1].strip().split(" ")[:-1]).strip()
                        state = (
                            state_url.split("restaurants/")[-1]
                            .strip()
                            .split("/")[0]
                            .strip()
                        )
                        zip = raw_info[1].strip().split(" ")[-1]
                        country_code = "AU"

                        phone = raw_info[-1].strip()
                        raw_address = "<MISSING>"

                        hours_of_operation = "<MISSING>"

                        store_number = "<MISSING>"
                        latitude, longitude = "<MISSING>", "<MISSING>"

                        yield SgRecord(
                            locator_domain=locator_domain,
                            page_url=state_url,
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
                    else:
                        store_sel = lxml.html.fromstring(store_res.text)

                        page_url = store_res.url

                else:  # state url is of store url

                    store_sel = state_sel
                    log.info("no parsing need".upper())
                    page_url = state_res.url

                if is_url_broken is False:
                    location_name = "".join(
                        store_sel.xpath("//h1[@class='hero-restaurant__title']/text()")
                    ).strip()
                    location_type = "<MISSING>"

                    street_address = " ".join(
                        store_sel.xpath(
                            '//div[contains(@class,"restaurant-details")]//span[@itemprop="streetAddress"]//text()'
                        )
                    ).strip()
                    city = " ".join(
                        store_sel.xpath(
                            '//div[contains(@class,"restaurant-details")]//span[@itemprop="addressLocality"]//text()'
                        )
                    ).strip()
                    state = " ".join(
                        store_sel.xpath(
                            '//div[contains(@class,"restaurant-details")]//span[@itemprop="addressRegion"]//text()'
                        )
                    ).strip()
                    zip = " ".join(
                        store_sel.xpath(
                            '//div[contains(@class,"restaurant-details")]//span[@itemprop="postalCode"]//text()'
                        )
                    ).strip()
                    country_code = "AU"

                    phone = " ".join(
                        store_sel.xpath(
                            '//div[contains(@class,"restaurant-details")]//span[@itemprop="telephone"]//text()'
                        )
                    ).strip()

                    raw_address = "<MISSING>"

                    hours = list(
                        filter(
                            str,
                            [
                                x.strip()
                                for x in store_sel.xpath(
                                    '//div[contains(@class,"restaurant-details")]//tr[@itemprop="openingHours"]/@content'
                                )
                            ],
                        )
                    )
                    hours_of_operation = "; ".join(hours)

                    store_number = "<MISSING>"
                    map_link = "".join(
                        store_sel.xpath(
                            '//div[contains(@class,"restaurant-details")]//a[contains(@href,"maps")]/@href'
                        )
                    )

                    latitude, longitude = get_latlng(map_link)

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

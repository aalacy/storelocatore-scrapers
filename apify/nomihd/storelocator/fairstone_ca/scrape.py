# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "fairstone.ca"
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
    elif "daddr=" in map_link:
        latitude = map_link.split("daddr=")[1].split(",")[0].strip()
        longitude = map_link.split("daddr=")[1].split(",")[1].strip()
    else:
        latitude = "<MISSING>"
        longitude = "<MISSING>"
    return latitude, longitude


def fetch_data():
    # Your scraper here

    search_url = "https://branches.fairstone.ca/browse/"

    with SgRequests() as session:
        search_res = session.get(search_url, headers=headers)

        search_sel = lxml.html.fromstring(search_res.text)

        states = search_sel.xpath('//ul[@class="browse"]//a')

        for _state in states:

            state_url = "".join(_state.xpath("./@href"))
            log.info(state_url)

            state_res = session.get(state_url, headers=headers)
            state_sel = lxml.html.fromstring(state_res.text)

            cities = state_sel.xpath('//ul[@class="map-list"]//a')

            for _city in cities:

                city_url = "".join(_city.xpath("./@href"))
                log.info(city_url)
                city_res = session.get(city_url, headers=headers)
                city_sel = lxml.html.fromstring(city_res.text)

                stores = city_sel.xpath(
                    '//ul[@class="map-list"]//div[@class="map-list-item"]'
                )

                for no, store in enumerate(stores, 1):

                    locator_domain = website

                    page_url = "".join(store.xpath("div[1]/a/@href"))

                    log.info(page_url)
                    store_res = session.get(page_url, headers=headers)

                    store_sel = lxml.html.fromstring(store_res.text)
                    store_number = "<MISSING>"

                    location_name = " ".join(
                        store_sel.xpath('//div[@class="locator"]//h1/text()')
                    )
                    location_type = "<MISSING>"

                    store_info = store_sel.xpath(
                        '//div[@class="locator"]//div[@class="map-list"]//p[@class="address"]/span[not(@data-hide-empty)]/text()'
                    )
                    log.info(store_info)
                    street_address = store_info[0]
                    city = store_info[-1].strip().split(",")[0].strip()

                    state = (
                        store_info[-1]
                        .strip()
                        .split(",")[-1]
                        .strip()
                        .split(" ", 1)[0]
                        .strip()
                    )
                    zip = (
                        store_info[-1]
                        .strip()
                        .split(",")[-1]
                        .strip()
                        .split(" ", 1)[-1]
                        .strip()
                    )

                    country_code = "CA"

                    phone = "".join(
                        store_sel.xpath(
                            '//div[@class="locator"]//div[@class="map-list"]//a[contains(@href,"tel")]//text()'
                        )
                    ).strip()

                    hours = list(
                        filter(
                            str,
                            [
                                x.strip()
                                for x in store_sel.xpath(
                                    '//div[@class="locator"]//div[@class="hours"]//span//text()'
                                )
                            ],
                        )
                    )
                    hours_of_operation = (
                        "; ".join(hours)
                        .replace("day;", "day:")
                        .replace("; -;", " - ")
                        .strip()
                    )

                    map_link = "".join(
                        store_sel.xpath(
                            '//div[@class="locator"]//div[@class="map-list"]//a[contains(@href,"maps")]/@href'
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

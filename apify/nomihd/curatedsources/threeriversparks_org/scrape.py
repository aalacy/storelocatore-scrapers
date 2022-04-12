# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal import sgpostal as parser

website = "threeriversparks.org"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36",
    "accept-language": "en-US,en;q=0.9,ar;q=0.8",
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
    elif "&q=" in map_link:
        latitude = map_link.split("&q=")[1].split(",")[0].strip()
        longitude = map_link.split("&q=")[1].split(",")[1].strip()
    elif "?q=" in map_link:
        latitude = map_link.split("?q=")[1].split(",")[0].strip()
        longitude = map_link.split("?q=")[1].split(",")[1].strip()
    else:
        latitude = "<MISSING>"
        longitude = "<MISSING>"
    return latitude, longitude


def fetch_data():
    # Your scraper here

    search_url = "https://www.threeriversparks.org/locations"
    with SgRequests() as session:
        stores_req = session.get(search_url, headers=headers)
        stores_sel = lxml.html.fromstring(stores_req.text)
        location_type = stores_sel.xpath(
            '//div[./noscript]/div[@class="isVisuallyHidden"]/h1[1]/text()'
        )
        stores = stores_sel.xpath(
            '//div[./noscript]/div[@class="isVisuallyHidden"]/ul[1]/li/a/@href'
        )
        for store_url in stores:

            locator_domain = website

            if "threeriversparks.org" not in store_url:
                page_url = "https://www.threeriversparks.org" + store_url
            else:
                page_url = store_url

            log.info(page_url)

            store_res = session.get(page_url, headers=headers)
            store_sel = lxml.html.fromstring(store_res.text)

            location_name = "".join(
                store_sel.xpath('//div[@class="billboard__content__hd"]/h1/text()')
            ).strip()

            location_type = "<MISSING>"

            raw_address = ", ".join(
                list(
                    filter(
                        str,
                        [
                            x.strip()
                            for x in store_sel.xpath(
                                '//div[@class="billboard__cta__item"][.//title[contains(text(),"Location")]]//span[@class="slab__text__line3"]/text()'
                            )
                        ],
                    )
                )
            )

            formatted_addr = parser.parse_address_usa(raw_address)
            street_address = formatted_addr.street_address_1
            if street_address:
                if formatted_addr.street_address_2:
                    street_address = (
                        street_address + ", " + formatted_addr.street_address_2
                    )
            else:
                if formatted_addr.street_address_2:
                    street_address = formatted_addr.street_address_2

            if street_address is not None:
                street_address = street_address.replace("Ste", "Suite")

            city = formatted_addr.city

            state = formatted_addr.state
            if state:
                state = state.replace("Center", "").strip()

            zip = formatted_addr.postcode

            country_code = "US"

            phone = "".join(
                store_sel.xpath(
                    '//div[@class="billboard__cta__item"][.//title[contains(text(),"Phone Number")]]//span[@class="slab__text__line3"][last()]/text()'
                )
            ).strip()

            hours_of_operation = "".join(
                store_sel.xpath(
                    '//div[@class="billboard__cta__item"][.//title[contains(text(),"Hours")]]//span[@class="slab__text__line3"][last()]/text()'
                )
            ).strip()

            store_number = "<MISSING>"
            map_link = "".join(
                store_sel.xpath(
                    '//div[@class="billboard__cta__item"][.//title[contains(text(),"Location")]]/a/@href'
                )
            ).strip()

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

            more_locations = store_sel.xpath(
                '//div[@class="clicker clicker--isGreen"][.//a[@class="blockLink map-location"]]'
            )
            for loc in more_locations:
                page_url = "".join(loc.xpath("div[1]/a/@href")).strip()
                if "threeriversparks.org" not in page_url:
                    page_url = "https://www.threeriversparks.org" + page_url

                store_res = session.get(page_url, headers=headers)
                store_sel = lxml.html.fromstring(store_res.text)

                location_name = "".join(
                    store_sel.xpath('//div[@class="billboard__content__hd"]/h1/text()')
                ).strip()

                location_type = "<MISSING>"

                raw_address = ", ".join(
                    list(
                        filter(
                            str,
                            [
                                x.strip()
                                for x in store_sel.xpath(
                                    '//div[@class="billboard__cta__item"][.//title[contains(text(),"Location")]]//span[@class="slab__text__line3"]/text()'
                                )
                            ],
                        )
                    )
                )

                formatted_addr = parser.parse_address_intl(raw_address)
                street_address = formatted_addr.street_address_1
                if street_address:
                    if formatted_addr.street_address_2:
                        street_address = (
                            street_address + ", " + formatted_addr.street_address_2
                        )
                else:
                    if formatted_addr.street_address_2:
                        street_address = formatted_addr.street_address_2

                if street_address is not None:
                    street_address = street_address.replace("Ste", "Suite")

                city = formatted_addr.city

                state = formatted_addr.state
                if state:
                    state = state.replace("Center", "").strip()

                zip = formatted_addr.postcode

                country_code = "US"

                phone = "".join(
                    store_sel.xpath(
                        '//div[@class="billboard__cta__item"][.//title[contains(text(),"Phone Number")]]//span[@class="slab__text__line3"][last()]/text()'
                    )
                ).strip()

                hours_of_operation = "".join(
                    store_sel.xpath(
                        '//div[@class="billboard__cta__item"][.//title[contains(text(),"Hours")]]//span[@class="slab__text__line3"][last()]/text()'
                    )
                ).strip()

                store_number = "<MISSING>"

                latitude = "".join(
                    loc.xpath(".//a[@class='blockLink map-location']/@data-latitude")
                ).strip()
                longitude = "".join(
                    loc.xpath(".//a[@class='blockLink map-location']/@data-longitude")
                ).strip()

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

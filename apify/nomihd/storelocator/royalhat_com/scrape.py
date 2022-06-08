# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgpostal import sgpostal as parser
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "royalhat.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "authority": "www.royalhat.com",
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
    else:
        latitude = "<MISSING>"
        longitude = "<MISSING>"
    return latitude, longitude


def fetch_data():
    # Your scraper here
    base = "http://www.royalhat.com"
    search_url = "http://www.royalhat.com/shop/"

    with SgRequests() as session:
        search_res = session.get(search_url, headers=headers)
        log.info(search_res)

        search_sel = lxml.html.fromstring(search_res.text)

        states = search_sel.xpath('//div[@id="shop-side2-div"]/div//a')

        for no, _state in enumerate(states, 1):

            locator_domain = website

            state_url = base + "".join(_state.xpath("./@href")).strip()
            log.info(state_url)
            state_res = session.get(state_url, headers=headers)
            state_sel = lxml.html.fromstring(state_res.text)

            stores = state_sel.xpath('//div[@id="shop-ken-info-div"]')

            for n, store in enumerate(stores, 1):

                page_url = "".join(store.xpath("./div//a/@href"))
                page_url = state_url + page_url
                log.info(page_url)

                store_res = session.get(page_url, headers=headers)
                store_sel = lxml.html.fromstring(store_res.text)

                location_name = " ".join(
                    store_sel.xpath('//div[@id="shop-tenpo-div"]/h1//text()')
                ).strip()

                location_type = "<MISSING>"

                store_info = list(
                    filter(
                        str,
                        [
                            x.strip()
                            for x in store_sel.xpath(
                                '//div[@id="shop-ken-info-address-div"]//text()'
                            )
                        ],
                    )
                )

                raw_address = ", ".join(store_info)

                formatted_addr = parser.parse_address_intl(raw_address)
                street_address = formatted_addr.street_address_1
                if formatted_addr.street_address_2:
                    street_address = (
                        street_address + ", " + formatted_addr.street_address_2
                    )

                if street_address is not None:
                    street_address = street_address.replace("Ste", "Suite")

                city = formatted_addr.city

                state = formatted_addr.state

                zip = formatted_addr.postcode

                country_code = "JP"

                phone = "".join(
                    store_sel.xpath('//div[@id="shop-ken-info-tel-div"]//text()')
                )

                hours = list(
                    filter(
                        str,
                        [
                            x.strip()
                            for x in store_sel.xpath(
                                '//div[@id="shop-ken-info-businesshours-div"]//text()'
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

                map_link = "".join(
                    store_sel.xpath('//iframe[contains(@src,"maps")]/@src')
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

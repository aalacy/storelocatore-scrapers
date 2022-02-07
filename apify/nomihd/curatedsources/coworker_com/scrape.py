# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgpostal import sgpostal as parser
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "coworker.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "authority": "www.coworker.com",
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

    search_url = "https://www.coworker.com/office-space/cities"

    with SgRequests() as session:
        search_res = session.get(search_url, headers=headers)

        search_sel = lxml.html.fromstring(search_res.text)

        cities = search_sel.xpath(
            '//div[@class="col-xs-12 pade_none around_city_con"]//ul/li/a'
        )

        for no, _city in enumerate(cities, 1):

            locator_domain = website

            city_url = "".join(_city.xpath("./@href")).strip()
            log.info(city_url)
            city = "".join(_city.xpath(".//text()")).strip()

            city_res = session.get(city_url, headers=headers)
            city_sel = lxml.html.fromstring(city_res.text)

            stores = city_sel.xpath('//div[@class="item"]//a')

            for n, store in enumerate(stores, 1):

                page_url = "".join(store.xpath("./@href"))

                log.info(page_url)

                store_res = session.get(page_url, headers=headers)
                store_sel = lxml.html.fromstring(store_res.text)

                location_name = " ".join(store.xpath(".//h4//text()")).strip()

                location_type = "<MISSING>"

                store_info = list(
                    filter(
                        str,
                        [
                            x.strip()
                            for x in store_sel.xpath(
                                '//div[@id="location"]//h2/span//text()'
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

                city = page_url.split("/")[-2]
                state = formatted_addr.state

                zip = formatted_addr.postcode

                country_code = page_url.split("/")[-3]
                phone = "<MISSING>"

                hours = store_sel.xpath('//h4[text()="Opening Hours"]/../div')
                hours_list = []
                for hour in hours:
                    day = "".join(hour.xpath("span/text()")).strip()
                    time = "".join(hour.xpath("text()")).strip()
                    hours_list.append(day + ":" + time)

                hours_of_operation = (
                    "; ".join(hours_list)
                    .strip()
                    .replace("day; ", "day: ")
                    .replace("Show More", "")
                    .strip("; ")
                )

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

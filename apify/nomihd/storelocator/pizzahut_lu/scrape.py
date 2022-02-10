# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgpostal import sgpostal as parser
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


website = "pizzahut.lu"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "authority": "restaurants.pizzahut.lu",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="90", "Google Chrome";v="90"',
    "sec-ch-ua-mobile": "?0",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "none",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "accept-language": "en-US,en;q=0.9,ar;q=0.8",
}


def fetch_data():
    # Your scraper here
    base = "https://restaurants.pizzahut.lu"
    search_url = "https://restaurants.pizzahut.lu/?lang=en"
    search_res = session.get(search_url, headers=headers)

    search_sel = lxml.html.fromstring(search_res.text)

    store_list = search_sel.xpath('//div[@id="restaurant_submenu"]//li')

    for store in store_list:

        page_url = base + "".join(store.xpath("./a/@href")).strip()

        locator_domain = website

        slug = page_url.split("/")[-1].strip()
        log.info(f"https://restaurants.pizzahut.lu/pages/restaurant.php?attr={slug}")
        store_res = session.get(
            f"https://restaurants.pizzahut.lu/pages/restaurant.php?attr={slug}",
            headers=headers,
        )
        store_sel = lxml.html.fromstring(store_res.text)

        location_name = " ".join(
            store_sel.xpath(
                "//table[not(@class)]//div[@id='left_bar_content']/div[1]//text()"
            )
        ).strip()

        store_info = list(
            filter(
                str,
                [
                    x.strip()
                    for x in store_sel.xpath(
                        '//table[not(@class)]//div[contains(@class,"description")]//text()'
                    )
                ],
            )
        )

        raw_address = " ".join(store_info[:-2]).strip()

        formatted_addr = parser.parse_address_intl(raw_address)
        street_address = formatted_addr.street_address_1
        if formatted_addr.street_address_2:
            street_address = street_address + ", " + formatted_addr.street_address_2

        city = formatted_addr.city
        if not city:
            city = raw_address.split(" ")[-1].strip()
        state = formatted_addr.state
        zip = formatted_addr.postcode
        country_code = "LU"

        phone = store_info[-1].strip()

        store_number = "<MISSING>"

        location_type = "<MISSING>"

        hours = list(
            filter(
                str,
                [
                    x.strip()
                    for x in store_sel.xpath(
                        '//table[@class="mob"]//div[contains(@class,"description")]//text()'
                    )
                ],
            )
        )
        hours_of_operation = (
            "; ".join(hours)
            .replace("Open:;", "Open")
            .replace("to; ", "to ")
            .replace("SPACIOUS CAR PARK & SOLARIUM; ", "")
            .strip()
            .replace(":;", ":")
            .strip()
            .split("; Holiday hours")[0]
            .strip()
            .replace("7/7;", "7/7")
            .strip()
        )
        if "Temporarily closed" in hours_of_operation:
            hours_of_operation = "<MISSING>"
            location_type = "Temporarily closed"

        map_link = store_res.text.split("maps.LatLng(")[1].split(");")[0]

        latitude, longitude = map_link.split(",")[0], map_link.split(",")[1]

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

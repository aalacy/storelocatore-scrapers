# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgpostal import sgpostal as parser
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgselenium import SgChrome
import ssl

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification

website = "pizzahut.es"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "Connection": "keep-alive",
    "Cache-Control": "max-age=0",
    "sec-ch-ua": '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
    "sec-ch-ua-mobile": "?0",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-User": "?1",
    "Sec-Fetch-Dest": "document",
    "Accept-Language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.pizzahut.es/sitemap.xml"
    search_res = session.get(search_url, headers=headers)

    links = search_res.text.split("<loc>")

    with SgChrome() as driver:

        for index in range(1, len(links)):
            page_url = links[index].split("</loc>")[0].strip()
            if "pizzahut.es/pizzeria/" not in page_url:
                continue

            locator_domain = website

            log.info(page_url)
            driver.get(page_url)
            store_sel = lxml.html.fromstring(driver.page_source)

            location_name = "".join(
                store_sel.xpath(
                    '//div[@class="mod_generic_promotion shopTitle"]/h1/text()'
                )
            ).strip()

            temp_address = store_sel.xpath(
                '//div[@class="mod_generic_promotion shopTitle"]/address/span/text()'
            )
            add_list = []
            for add in temp_address:
                if len("".join(add).strip()) > 0:
                    add_list.append("".join(add).strip())

            raw_address = " ".join(add_list).strip()
            formatted_addr = parser.parse_address_intl(raw_address)
            street_address = formatted_addr.street_address_1
            if formatted_addr.street_address_2:
                street_address = street_address + ", " + formatted_addr.street_address_2

            city = formatted_addr.city
            state = formatted_addr.state
            zip = formatted_addr.postcode

            country_code = "ES"

            phone = "".join(
                store_sel.xpath('//span[@itemprop="telephone"]//text()')
            ).strip()

            store_number = "<MISSING>"

            location_type = "<MISSING>"
            hours = store_sel.xpath(
                '//*[@class="hours clearfix pls prs pbs mts"]/div[@class="columns"][./h4[contains(text(),"A domicilio")]]/table//tr'
            )
            hours_list = []
            for hour in hours:
                day = "".join(hour.xpath("td[1]/text()")).strip()
                time = "".join(hour.xpath("td[2]/text()")).strip()
                hours_list.append(day + ":" + time)

            hours_of_operation = "; ".join(hours_list).strip()

            latitude = (
                driver.page_source.split("var lat = ")[1].strip().split(";")[0].strip()
            )
            longitude = (
                driver.page_source.split("var lng = ")[1].strip().split(";")[0].strip()
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

# -*- coding: utf-8 -*-
from sgrequests import SgRequests, SgRequestError
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal import sgpostal as parser

website = "trekbikes.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "authority": "www.trekbikes.com",
    "sec-ch-ua": '" Not;A Brand";v="99", "Google Chrome";v="97", "Chromium";v="97"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "navigate",
    "sec-fetch-dest": "document",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.trekbikes.com/store-finder/allRetailers/"
    base = "https://www.trekbikes.com"
    countries_req = session.get(search_url, headers=headers)
    countries_sel = lxml.html.fromstring(countries_req.text)
    countries = countries_sel.xpath(
        '//li[@class="region__list-item"]/div[@class="country"]/a'
    )
    for country in countries:
        country_code = "".join(country.xpath("text()")).strip()
        country_url = base + "".join(country.xpath("@href")).strip()
        stores_req = session.get(country_url, headers=headers)
        stores_sel = lxml.html.fromstring(stores_req.text)
        stores = stores_sel.xpath(
            '//li[@class="region__list-item"]/div[@class="country"][./a/span[@class="text-weak"]]/a'
        )
        for store in stores:
            location_type = "".join(store.xpath("span/text()")).strip()
            page_url = base + "".join(store.xpath("@href")).strip()
            log.info(page_url)
            store_req = session.get(page_url, headers=headers)
            if isinstance(store_req, SgRequestError):
                continue
            store_sel = lxml.html.fromstring(store_req.text)
            store_number = "<MISSING>"
            locator_domain = website

            location_name = "".join(
                store_sel.xpath("//h2[@class='header-largish']/text()")
            ).strip()

            raw_info = store_sel.xpath(
                '//ul[contains(@class,"address")]/li[./span[contains(text(),"address")]]/following-sibling::li[not(.//a[contains(@href,"tel:")])]/span'
            )

            phone = "".join(
                store_sel.xpath(
                    '//ul[contains(@class,"address")]/li//a[contains(@href,"tel:")]/text()'
                )
            ).strip()
            if len(phone) <= 0:
                phone = "".join(
                    store_sel.xpath(
                        '//div[@class="elp-details__contactInfo"]//li//a[contains(@href,"tel:")]/text()'
                    )
                )
            add_list = []
            for raw in raw_info:
                if (
                    len(
                        "".join(raw.xpath(".//text()"))
                        .strip()
                        .replace("\n", "")
                        .replace("\t", "")
                        .strip()
                    )
                    > 0
                ):
                    add_list.append(
                        "".join(raw.xpath(".//text()"))
                        .strip()
                        .replace("\n", "")
                        .replace("\t", "")
                        .strip()
                        .replace(",\xa0", " ")
                    )

            street_address = (
                store_req.text.split("var storeaddressline1 = ")[1]
                .strip()
                .split(";")[0]
                .strip()
                .replace("'", "")
                .strip()
            )
            add_2 = (
                store_req.text.split("var storeaddressline2 = ")[1]
                .strip()
                .split(";")[0]
                .strip()
                .replace("'", "")
                .strip()
            )
            if len(add_2) > 0:
                street_address = street_address + ", " + add_2

            city = (
                store_req.text.split("var storeaddresstown = ")[1]
                .strip()
                .split(";")[0]
                .strip()
                .replace("'", "")
                .strip()
            )

            raw_address = ", ".join(add_list).strip()
            formatted_addr = parser.parse_address_intl(raw_address)
            state = formatted_addr.state
            zip = (
                store_req.text.split("var storeaddresspostalCode = ")[1]
                .strip()
                .split(";")[0]
                .strip()
                .replace("'", "")
                .strip()
            )

            hours = store_sel.xpath('//table[@qaid="store-hours"]//tr')
            hours_list = []
            for hour in hours:
                day = "".join(hour.xpath("td[1]//text()")).strip()
                temp_time = hour.xpath("td[2]//text()")
                time = []
                for t in temp_time:
                    if len("".join(t).strip()) > 0:
                        time.append(
                            "".join(t)
                            .strip()
                            .replace("\r\n", "")
                            .replace("\n", "")
                            .strip()
                        )
                hours_list.append(day + ":" + ", ".join(time))

            hours_of_operation = ";".join(hours_list).strip()
            latitude, longitude = (
                store_req.text.split("var storelatitude = ")[1]
                .strip()
                .split(";")[0]
                .strip()
                .replace("'", "")
                .strip(),
                store_req.text.split("var storelongitude = ")[1]
                .strip()
                .split(";")[0]
                .strip()
                .replace("'", "")
                .strip(),
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

# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgpostal import sgpostal as parser
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "pizzahut.com.co"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "authority": "www.pizzahut.com.co",
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
    base = "https://www.pizzahut.com.co"
    search_url = "https://www.pizzahut.com.co/pizzerias"
    search_res = session.get(search_url, headers=headers)

    search_sel = lxml.html.fromstring(search_res.text)

    regions = search_sel.xpath('//ul[@class="areas"]/li/a/@href')

    for region in regions:
        log.info(base + region)

        region_res = session.get(base + region)
        region_sel = lxml.html.fromstring(region_res.text)

        cities = region_sel.xpath('//ul[@class="cities"]/li/a/@href')

        for city in cities:
            log.info(base + city)
            city_res = session.get(base + city)
            city_sel = lxml.html.fromstring(city_res.text)

            store_list = city_sel.xpath('//ul[@class="list"]/li//a/@href')

            for store in store_list:
                page_url = base + store

                locator_domain = website
                log.info(page_url)
                store_res = session.get(page_url, headers=headers)
                store_sel = lxml.html.fromstring(store_res.text)

                full_address = list(
                    filter(
                        str,
                        [x.strip() for x in store_sel.xpath("//address//text()")],
                    )
                )

                raw_address = " ".join(full_address).strip()

                formatted_addr = parser.parse_address_intl(raw_address)
                street_address = formatted_addr.street_address_1
                if formatted_addr.street_address_2:
                    street_address = (
                        street_address + ", " + formatted_addr.street_address_2
                    )

                city = formatted_addr.city
                if city is None:
                    city = street_address.rsplit(" ", 1)[-1].strip()
                    street_address = street_address.rsplit(" ", 1)[0].strip()

                state = formatted_addr.state
                zip = formatted_addr.postcode

                country_code = "Colombia"

                location_name = " ".join(store_sel.xpath("//title//text()")).strip()

                phone = " ".join(store_sel.xpath('//*[@class="phone"]//text()')).strip()
                store_number = store.split("-")[-1].strip()

                location_type = "<MISSING>"

                hours = store_sel.xpath(
                    '//div[@class="shopInfo col"]//div[contains(./h4/text(),"A domicilio")]//tr'
                )

                if len(hours) <= 0:
                    hours = store_sel.xpath(
                        '//div[@class="shopInfo col"]//div[contains(./h4/text(),"A recoger")]//tr'
                    )
                hours_list = []
                for hour in hours:
                    day = "".join(hour.xpath("td[1]/text()")).strip()
                    time = "".join(hour.xpath("td[2]/text()")).strip()
                    hours_list.append(day + ": " + time)

                hours_of_operation = "; ".join(hours_list).strip()
                latitude, longitude = (
                    store_res.text.split("lat =")[1].split(";")[0].strip(),
                    store_res.text.split("lng =")[1].split(";")[0].strip(),
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

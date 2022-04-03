# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "bankofmarin.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "authority": "www.bankofmarin.com",
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


def split_fulladdress(address_info):
    street_address = " ".join(address_info[0:-1]).strip(" ,.")

    city_state_zip = (
        address_info[-1].replace(",", " ").replace(".", " ").replace("  ", " ").strip()
    )

    city = " ".join(city_state_zip.split(" ")[:-2]).strip()
    state = city_state_zip.split(" ")[-2].strip()
    zip = city_state_zip.split(" ")[-1].strip()
    country_code = "US"
    return street_address, city, state, zip, country_code


def fetch_data():
    # Your scraper here
    search_url = "https://www.bankofmarin.com/about-us/contact-us/"
    search_res = session.get(search_url, headers=headers)

    search_sel = lxml.html.fromstring(search_res.text)

    store_list = search_sel.xpath('//a[contains(@href,"branches")]/@href')

    for store in store_list:

        page_url = store
        locator_domain = website
        log.info(page_url)
        store_res = session.get(page_url, headers=headers)
        store_sel = lxml.html.fromstring(store_res.text)

        location_name = "".join(store_sel.xpath("//h1/text()"))

        store_data = list(
            filter(
                str,
                [
                    x.strip()
                    for x in store_sel.xpath('//*[contains(@class,"left-")]/p//text()')
                ],
            )
        )

        full_address = store_data[:2]

        street_address, city, state, zip, country_code = split_fulladdress(full_address)

        store_number = "<MISSING>"
        phone = store_data[-1]
        if "call" in phone:
            phone = phone.split("call")[1].strip()

        location_type = "Branch"

        hours = list(
            filter(
                str,
                [
                    x.strip()
                    for x in store_sel.xpath('//*[contains(@class,"right-")]/p//text()')
                ],
            )
        )
        hours = hours[1:-1]
        hours_of_operation = "; ".join(hours)

        if "Branch services unavailable" in hours_of_operation:
            hours_of_operation = "<MISSING>"
            location_type = "ATM"
        if "ppointment" in hours_of_operation:
            hours_of_operation = "<MISSING>"

        if "no branch service" in location_name:
            location_type = "ATM"

        latitude = "".join(
            store_sel.xpath('//div[contains(@class,"marker")]/@data-lat')
        )
        longitude = "".join(
            store_sel.xpath('//div[contains(@class,"marker")]/@data-lng')
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

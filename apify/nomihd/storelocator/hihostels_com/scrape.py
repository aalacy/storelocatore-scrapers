# -*- coding: utf-8 -*-
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal import sgpostal as parser

local = threading.local()
website = "hihostels.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "authority": "www.hihostels.com",
    "sec-ch-ua": '" Not;A Brand";v="99", "Google Chrome";v="97", "Chromium";v="97"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "none",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def get_session(retry):
    if retry or not hasattr(local, "session"):
        local.session = SgRequests(timeout_config=600)

    return local.session


def fetch_locations(retry=0):
    try:
        urls = []
        session = get_session(retry)
        response = session.get(
            "https://www.hihostels.com/sitemap.xml",
        )

        time.sleep(15)

        stores = response.text.split("<loc>")
        for index in range(1, len(stores)):
            page_url = "".join(stores[index].split("</loc>")[0].strip()).strip()
            if "/hostels/" not in page_url or "/es/" in page_url:
                continue

            urls.append(page_url)

        return urls
    except Exception as e:
        if retry < 10:
            return fetch_locations(retry + 1)

        raise e


def fetch_location(page_url, retry=0):
    try:
        session = get_session(retry)
        response = session.get(page_url)

        store_sel = lxml.html.fromstring(response.text)
        locator_domain = website

        store_number = "<MISSING>"

        location_type = "<MISSING>"
        location_name = "".join(
            store_sel.xpath('//h1[contains(@class,"hostel-header")]//text()')
        ).strip()

        temp_address = store_sel.xpath('//p[@class="full-address"]/text()')

        add_list = []
        for temp in temp_address:
            if (
                len(
                    "".join(temp)
                    .strip()
                    .replace("\r\n", "")
                    .strip()
                    .replace("\n", "")
                    .strip()
                )
                > 0
            ):
                add_list.append(
                    "".join(temp)
                    .strip()
                    .replace("\r\n", "")
                    .strip()
                    .replace("\n", "")
                    .strip()
                )

        full_address = ", ".join(add_list).strip().split(",")
        full_add_list = []
        for add in full_address:
            if len("".join(add).strip()) > 0:
                full_add_list.append("".join(add).strip())

        raw_address = ", ".join(full_add_list).strip()
        formatted_addr = parser.parse_address_intl(raw_address)
        street_address = formatted_addr.street_address_1
        if formatted_addr.street_address_2:
            street_address = street_address + ", " + formatted_addr.street_address_2

        city = formatted_addr.city
        state = formatted_addr.state
        zip = formatted_addr.postcode
        country_code = formatted_addr.country

        temp_phone = store_sel.xpath('//div[@class="acc-inner"]/p/text()')
        phone_list = []
        for ph in temp_phone:
            if len("".join(ph).strip()) > 0:
                phone_list.append("".join(ph).strip())

        log.info(phone_list)
        if len(phone_list) > 0:
            phone = phone_list[0].split("/")[0].strip()
        else:
            phone = "<MISSING>"

        hours = store_sel.xpath(
            '//div[@id="opening-times-section"]//div[@class="acc-inner"]/p/span/text()'
        )
        if len(hours) > 0:
            hours_of_operation = hours[-1].strip().replace("Check-in:", "").strip()
        else:
            hours_of_operation = "<MISSING>"

        latitude, longitude = (
            "".join(store_sel.xpath('//input[@id="lat"]/@value')).strip(),
            "".join(store_sel.xpath('//input[@id="lon"]/@value')).strip(),
        )

        return SgRecord(
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
    except:
        if retry < 10:
            return fetch_location(page_url, retry + 1)


def fetch_data():
    urls = fetch_locations()
    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = [executor.submit(fetch_location, url) for url in urls]
        for future in as_completed(futures):
            poi = future.result()
            if poi:
                yield poi


def scrape():
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PageUrlId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)


if __name__ == "__main__":
    scrape()

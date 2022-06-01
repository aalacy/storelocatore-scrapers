# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json

website = "exclusivefurniture.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "Connection": "keep-alive",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="99", "Google Chrome";v="99"',
    "sec-ch-ua-mobile": "?0",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36",
    "sec-ch-ua-platform": '"Windows"',
    "Accept": "*/*",
    "Sec-Fetch-Site": "cross-site",
    "Sec-Fetch-Mode": "no-cors",
    "Sec-Fetch-Dest": "script",
    "Accept-Language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def split_fulladdress(address_info):
    street_address = ", ".join(address_info[:-2]).strip(" ,.")

    state_zip = (
        address_info[-1].replace(",", " ").replace(".", " ").replace("  ", " ").strip()
    )

    city = "".join(address_info[-2]).strip()
    state = state_zip.split(" ")[-2].strip()
    zip = state_zip.split(" ")[-1].strip()
    country_code = "US"
    return street_address, city, state, zip, country_code


def fetch_data():
    # Your scraper here
    search_url = "https://storemapper-herokuapp-com.global.ssl.fastly.net/api/users/13949/stores.js"
    search_res = session.get(search_url, headers=headers)

    stores = json.loads(search_res.text)["stores"]

    for store in stores:

        page_url = store["url"]
        locator_domain = website

        location_name = store["name"]

        store_number = store["id"]
        phone = store["phone"]
        location_type = "<MISSING>"
        log.info(page_url)
        store_req = session.get(page_url, headers=headers)
        store_sel = lxml.html.fromstring(store_req.text)
        full_address = (
            "".join(store_sel.xpath('//a[contains(text(),"Get Direction:")]/text()'))
            .strip()
            .replace("Get Direction:", "")
            .strip()
            .split(",")
        )
        street_address, city, state, zip, country_code = split_fulladdress(full_address)

        hours_of_operation = "; ".join(
            store_sel.xpath(
                '//div[@class="card"][./h4[contains(text(),"Store Hours")]]//li/text()'
            )
        ).strip()
        latitude, longitude = store["latitude"], store["longitude"]

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
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.StoreNumberId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()

# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
import json


website = "pizzerialocale.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "authority": "www.pizzerialocale.com",
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
    search_url = "https://www.pizzerialocale.com/locations/"
    search_res = session.get(search_url, headers=headers)

    search_sel = lxml.html.fromstring(search_res.text)

    store_list = list(
        set(
            search_sel.xpath(
                f'//a[@href="{search_url}"]/following-sibling::ul//a/@href'
            )
        )
    )

    for store in store_list:
        log.info(store)
        page_res = session.get(store, headers=headers)
        page_sel = lxml.html.fromstring(page_res.text)

        json_res = json.loads(
            "".join(page_sel.xpath('//script[@type="application/ld+json"]/text()'))
        )

        json_obj = json_res["@graph"][2]

        page_url = store
        locator_domain = website

        location_name = json_obj["name"].strip()

        street_address = json_obj["address"]["streetAddress"].strip()

        city = json_obj["address"]["addressLocality"].strip()
        state = json_obj["address"]["addressRegion"].strip()
        zip = json_obj["address"]["postalCode"].strip()

        country_code = json_obj["address"]["addressCountry"].strip()
        store_number = "<MISSING>"
        phone = json_obj["telephone"].strip()

        location_type = "<MISSING>"

        hours_of_operation = (
            json_obj["description"].upper().split("WE'RE OPEN ")[1].strip()
        )

        latitude = json_obj["geo"]["latitude"].strip()
        longitude = json_obj["geo"]["longitude"].strip()

        raw_address = "<MISSING>"

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
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()

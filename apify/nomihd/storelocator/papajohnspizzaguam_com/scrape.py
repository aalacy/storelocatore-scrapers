# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json

website = "papajohnspizzaguam.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "authority": "papajohnspizzaguam.com",
    "cache-control": "max-age=0",
    "sec-ch-ua": '"Google Chrome";v="93", " Not;A Brand";v="99", "Chromium";v="93"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "referer": "https://papajohnspizzaguam.com/",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.papajohnsguam.com/store-locator"
    search_res = session.get(search_url, headers=headers)
    search_sel = lxml.html.fromstring(search_res.text)

    stores = json.loads(
        "".join(search_sel.xpath('//script[@id="__NEXT_DATA__"]/text()')).strip()
    )["props"]["pageProps"]["locations"]

    for store in stores:
        page_url = search_url

        locator_domain = website
        location_name = store["name"]
        street_address = (
            store["address"]["street_number"] + " " + store["address"]["street_name"]
        )
        city = store["address"]["city"]
        state = store["address"]["region"]
        if state and state == "-":
            state = "<MISSING>"

        zip = store["address"]["postcode"]
        country_code = store["address"]["country"]

        store_number = store["id"]
        phone = store["address"]["phone_number"]
        location_type = "<MISSING>"

        hours_list = []
        hours = store["opening_hours"]["pickup"]
        for day in hours.keys():
            if not isinstance(hours[day], bool):
                time = hours[day][0]
                hours_list.append(day + ":" + time)

        hours_of_operation = "; ".join(hours_list).strip()

        latitude = store["address"]["latitude"]
        longitude = store["address"]["longitude"]

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

# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


website = "kyfb.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "authority": "www.kyfb.com",
    "sec-ch-ua": '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
    "accept": "application/json, text/javascript, */*; q=0.01",
    "x-requested-with": "XMLHttpRequest",
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36",
    "content-type": "application/json",
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "accept-language": "en-US,en;q=0.9,ar;q=0.8",
}


def fetch_data():
    # Your scraper here
    base = "https://www.kyfb.com"
    search_url = "https://www.kyfb.com/find/agencies/"
    search_res = session.get(search_url, headers=headers)

    json_str = (
        search_res.text.split("var pushpinAgenciesObject = ")[1]
        .split("var pushpinClaimsObject = ")[0]
        .strip()
        .strip(";")
        .strip()
    )

    json_res = json.loads(json_str)

    store_list = json_res["DATA"]

    for store in store_list:

        page_url = base + store[10]
        log.info(page_url)
        store_res = session.get(page_url, headers=headers)
        store_sel = lxml.html.fromstring(store_res.text)

        locator_domain = website

        street_address = store[14]  # 14,15,16

        city = store[18].strip()
        state = store[19].strip()
        zip = store[20].strip()

        country_code = "US"

        location_name = store[1].strip()

        if "COMING SOON" in location_name:
            continue
        phone = store[24] + store[25] + store[26]
        store_number = store[0]

        location_type = "<MISSING>"

        hours = list(
            filter(
                str,
                [
                    x.strip()
                    for x in store_sel.xpath('//p[./strong[text()="Hours"]]//text()')
                ],
            )
        )

        hours_of_operation = (
            "; ".join(hours[2:])
            .replace("day;", "day:")
            .replace(":;", ":")
            .replace("\n", " ")
            .replace("  ", " ")
            .strip()
        )
        latitude, longitude = (
            store[8],
            store[9],
        )
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

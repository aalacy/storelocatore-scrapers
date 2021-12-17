# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "wendys.com.ph"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "authority": "wendys.com.ph",
    "content-length": "0",
    "sec-ch-ua": '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
    "accept": "application/json, text/javascript, */*; q=0.01",
    "x-requested-with": "XMLHttpRequest",
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36",
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "accept-language": "en-US,en;q=0.9,ar;q=0.8",
}

headers_post = {
    "Connection": "keep-alive",
    "sec-ch-ua": '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
    "Accept": "*/*",
    "X-Requested-With": "XMLHttpRequest",
    "sec-ch-ua-mobile": "?0",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "Origin": "https://wendys.com.ph",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Dest": "empty",
    "Referer": "https://wendys.com.ph/ourStores",
    "Accept-Language": "en-US,en;q=0.9,ar;q=0.8",
}

data = {"_token": "", "mode": "", "search": "", "city": ""}


def fetch_data():
    # Your scraper here
    search_url = "https://wendys.com.ph/ourStores"
    search_res = session.get(search_url, headers=headers)

    search_sel = lxml.html.fromstring(search_res.text)

    token = "".join(search_sel.xpath('//meta[@name="csrf-token"]/@content'))
    data["_token"] = token
    cities = search_sel.xpath('//select[@id="select-city"]//option')

    for city in cities[1:]:
        data["city"] = city.xpath("./@value")
        api_res = session.post(
            "https://wendys.com.ph/search/list/stores/all",
            headers=headers_post,
            data=data,
        )

        json_res = json.loads(api_res.text)

        store_list = json_res

        for store in store_list:

            page_url = "https://wendys.com.ph/ourStores"
            locator_domain = website

            raw_address = "<MISSING>"

            street_address = store["address"]
            city = store["city"]
            state = store["province"]
            zip = store["wii_code"]

            country_code = "PH"

            location_name = store["branch"] + ", " + city

            phone = store["contact"]
            store_number = str(store["id"])

            location_type = "<MISSING>"

            hours_of_operation = f"{store['start']} - {store['end']}"

            latitude, longitude = (
                "<MISSING>",
                "<MISSING>",
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

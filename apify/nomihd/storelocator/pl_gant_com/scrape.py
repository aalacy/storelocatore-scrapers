# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json
import lxml.html

website = "pl.gant.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "authority": "pl.gant.com",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
    "accept": "*/*",
    "x-requested-with": "XMLHttpRequest",
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "referer": "https://pl.gant.com/en/stores/",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here
    with SgRequests(dont_retry_status_codes=([404])) as session:
        search_url = "https://pl.gant.com/en/stores/?format=json&country=67"
        stores_req = session.get(
            search_url,
            headers=headers,
        )
        stores = json.loads(stores_req.text)["results"]
        for store in stores:
            store_number = "<MISSING>"
            locator_domain = website
            page_url = "https://pl.gant.com" + store["absolute_url"]
            log.info(page_url)
            store_req = session.get(page_url, headers=headers)
            store_sel = lxml.html.fromstring(store_req.text)
            location_name = store["name"]
            street_address = store["address"]

            city = store["township"]["city"]["name"]

            state = "<MISSING>"
            zip = "<MISSING>"
            country_code = "PL"

            phone = store["phone_number"]
            location_type = "<MISSING>"

            latitude = store["latitude"]
            longitude = store["longitude"]

            hours_list = []
            hours = store_sel.xpath(
                '//p[@class="store-detail-address-text"][./span[@class="store-day"]]'
            )
            for hour in hours:
                day = "".join(hour.xpath('span[@class="store-day"]/text()')).strip()
                time = "".join(hour.xpath("text()")).strip()
                hours_list.append(day + ":" + time)

            hours_of_operation = "; ".join(hours_list).strip()

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

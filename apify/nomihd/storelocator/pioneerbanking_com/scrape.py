# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
import json
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "pioneerny.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "authority": "www.pioneerny.com",
    "accept": "application/json, text/javascript, */*; q=0.01",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
    "referer": "https://www.pioneerny.com/locations",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="100", "Google Chrome";v="100"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.88 Safari/537.36",
    "x-requested-with": "XMLHttpRequest",
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.pioneerny.com/_/api/branches/42.7258356/-73.7937026/50000"
    with SgRequests() as session:
        stores_req = session.get(search_url, headers=headers)
        stores = json.loads(stores_req.text)["branches"]

        for store in stores:
            page_url = "https://www.pioneerny.com/locations"
            locator_domain = website
            location_name = store["name"]
            if location_name == "Test":
                continue
            street_address = store["address"]
            city = store["city"]
            state = store["state"]
            zip = store["zip"]

            country_code = "US"

            store_number = store["id"]
            phone = store["phone"]

            location_type = "<MISSING>"
            hours_list = []
            if store["description"] is not None and len(store["description"]) > 0:
                hours = lxml.html.fromstring(store["description"]).xpath("//div/ul")
                if len(hours) > 0:
                    hours = hours[0].xpath("li")
                    hours_list = []
                    hours_of_operation = ""
                    for hour in hours:
                        hours_list.append("".join(hour.xpath("text()")).strip())

            hours_of_operation = "; ".join(hours_list).strip()

            latitude = store["lat"]
            longitude = store["long"]

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

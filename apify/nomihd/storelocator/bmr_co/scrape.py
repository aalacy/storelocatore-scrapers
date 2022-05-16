# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
import json
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import us
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import lxml.html

website = "bmr.co"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "authority": "www.bmr.ca",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="101", "Google Chrome";v="101"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "none",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.67 Safari/537.36",
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.bmr.ca/fr/storelocator/index/loadstore/"
    with SgRequests(dont_retry_status_codes=([404])) as session:
        stores_req = session.get(search_url, headers=headers)
        stores = stores_req.json()["storesjson"]
        openingTimes = json.loads(stores_req.text)["openingTimes"]
        for store in stores:
            page_url = "https://www.bmr.co/en/" + store["rewrite_request_path"]
            locator_domain = website
            location_name = store["store_name"]
            street_address = store["address"]
            city = store["city"]
            state = store["state"]
            zip = store["zipcode"]

            country_code = "CA"
            if state is not None and us.states.lookup(state):
                country_code = "US"

            store_number = store["storelocator_id"]
            phone = store["phone"]
            if "," in phone:
                phone = phone.split(",")[0].strip()

            location_type = "<MISSING>"

            hours_list = []
            hours_found = True
            for time in openingTimes:
                if store_number == time["storelocator_id"]:
                    hours = time["store_hours"]
                    for day in hours.keys():
                        time = ""
                        if isinstance(hours[day], dict):
                            if "open" in hours[day]:
                                time = hours[day]["open"] + " - " + hours[day]["close"]
                            else:
                                hours_found = False
                                break
                        else:
                            time = hours[day]
                        if len(time) > 0:
                            hours_list.append(day + ":" + time)

                    break

            if hours_found is False:
                log.info(page_url)
                store_req = session.get(page_url, headers=headers)
                store_sel = lxml.html.fromstring(store_req.text)

                hours_list = []
                hours = store_sel.xpath('//div[@class="opening-hours"]/li')
                for hour in hours:
                    day = "".join(hour.xpath('div[@class="content1"]/text()')).strip()
                    time = "".join(hour.xpath('div[@class="content2"]//text()')).strip()
                    hours_list.append(day + ":" + time)

            hours_of_operation = "; ".join(hours_list).strip()

            latitude = store["latitude"]
            longitude = store["longitude"]

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

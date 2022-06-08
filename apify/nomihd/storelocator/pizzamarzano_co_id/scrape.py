# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "pizzamarzano.co.id"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "authority": "pizzamarzano.co.id",
    "accept": "application/json, text/javascript, */*; q=0.01",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
    "referer": "https://pizzamarzano.co.id/find-a-restaurant/",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="101", "Google Chrome";v="101"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.67 Safari/537.36",
    "x-requested-with": "XMLHttpRequest",
}


def fetch_data():
    # Your scraper here

    search_url = "https://pizzamarzano.co.id/wp-admin/admin-ajax.php?action=asl_load_stores&nonce=26943e2885&load_all=2&layout=1&lat=-6.192000908057697&lng=106.8351452&nw%5B%5D=-0.08740650406030263&nw%5B%5D=79.501160825&se%5B%5D=-12.296595312055091&se%5B%5D=134.169129575"

    with SgRequests() as session:
        stores_req = session.get(search_url, headers=headers)
        stores = json.loads(stores_req.text)

        for store in stores:
            page_url = "https://pizzamarzano.co.id/find-a-restaurant/"
            locator_domain = website
            location_name = store["title"]
            street_address = store["street"]
            city = store["city"].replace(",", "").strip()
            state = store["state"]
            zip = store["postal_code"]

            country_code = "ID"

            store_number = store["id"]
            phone = store["phone"]

            location_type = "<MISSING>"
            hours = store["open_hours"]
            hours_list = []
            if hours:
                hours = json.loads(hours)
                for day in hours.keys():
                    time = ""
                    if isinstance(hours[day], list):
                        time = hours[day][0]
                    else:
                        if hours[day] == "0":
                            time = "Closed"

                    hours_list.append(day + ":" + time)

            hours_of_operation = "; ".join(hours_list).strip()

            latitude = store["lat"]
            longitude = store["lng"]

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

# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json

website = "pizzahut.fr"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "authority": "www.pizzahut.fr",
    "cache-control": "max-age=0",
    "sec-ch-ua": '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
    "sec-ch-ua-mobile": "?0",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "cross-site",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.pizzahut.fr/huts/"
    search_res = session.get(search_url, headers=headers)

    search_sel = lxml.html.fromstring(search_res.text)

    store_list = search_sel.xpath(
        '//a[@class="mb-10 w-full md:w-1/2 text-left pl-15 py-10 typo-l5"]/@href'
    )

    for store_url in store_list:

        page_url = "https://www.pizzahut.fr" + store_url
        log.info(page_url)
        store_number = page_url.split("/fr-1/")[1].split("-")[0].strip()

        API_URL = f"https://api.pizzahut.io/v1/hut?sector=fr-1&hutId={store_number}&openDays=7"

        store_res = session.get(API_URL, headers=headers)

        store_json = json.loads(store_res.text)

        locator_domain = website
        location_name = store_json["name"]

        street_address = store_json["address"]["lines"][0]
        city = "<MISSING>"
        state = store_json["address"]["lines"][1]
        zip = store_json["address"]["postcode"]

        country_code = "FR"

        phone = store_json["phone"]
        location_type = "<MISSING>"

        hours_of_operation = "<MISSING>"
        hours_list = []
        try:
            hours = store_json["hours"]["web"]["scheduled"]
            for hour in hours:
                if hour["disposition"] != "collection":
                    continue

                temp_date = hour["open"].split("T")[0].strip()
                day = datetime.datetime.strptime(temp_date, "%Y-%m-%d").strftime("%A")
                ftime = hour["open"].split("T")[0].strip().split(":00.000Z")[0].strip()
                to_time = (
                    hour["close"].split("T")[0].strip().split(":00.000Z")[0].strip()
                )
                hours_list.append(day + ":" + ftime + " - " + to_time)

        except:
            pass

        hours_of_operation = "; ".join(hours_list).strip()
        latitude = store_json["latitude"]
        longitude = store_json["longitude"]

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

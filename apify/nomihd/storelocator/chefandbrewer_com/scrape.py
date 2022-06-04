# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "chefandbrewer.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "Connection": "keep-alive",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-User": "?1",
    "Sec-Fetch-Dest": "document",
    "Accept-Language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here

    search_url = "https://www.chefandbrewer.com/find-us/"
    with SgRequests() as session:
        stores_req = session.get(search_url)
        stores_sel = lxml.html.fromstring(stores_req.text)
        stores = stores_sel.xpath('//li/a[@class="pub-list__pub-name"]/@href')
        for store_url in stores:
            page_url = "https://www.chefandbrewer.com" + store_url
            log.info(page_url)
            store_req = session.get(page_url)
            venueId = (
                store_req.text.split("venueId: '")[1].strip().split("',")[0].strip()
            )
            data = {
                "operationName": "Venue",
                "variables": {"id": venueId},
                "query": "query Venue($id: ID!) {\n  venue(id: $id) {\n    name\n    address {\n      line1\n      line2\n      line3\n      county\n      postcode\n    }\n    closed\n    phone\n    email\n    attributes {\n      name\n      value\n    }\n    location {\n      latitude\n      longitude\n    }\n    operatingHours {\n      close\n      comment\n      name\n      open\n    }\n    specialOperatingHours {\n      name\n      open\n      close\n      comment\n      date\n    }\n    servingHours {\n      name\n      start\n      end\n      comment\n    }\n    specialServingHours {\n      name\n      start\n      end\n      comment\n      date\n    }\n    urls {\n      directions\n      book\n    }\n  }\n}\n",
            }

            store_req = session.post(
                "https://venuefinder.greeneking-pubs.co.uk/graphql",
                json=data,
                headers=headers,
            )
            store_json = store_req.json()["data"]["venue"]
            if store_json is not None:
                locator_domain = website
                latitude = store_json["location"]["latitude"]
                longitude = store_json["location"]["longitude"]
                store_number = venueId
                location_name = store_json["name"]
                location_type = "<MISSING>"
                if store_json["closed"] is True:
                    location_type = "Temporary Closed"

                street_address = store_json["address"]["line1"]
                city = store_json["address"]["line2"]
                state = store_json["address"]["county"]
                zip = store_json["address"]["postcode"]
                phone = store_json["phone"]

                hours = store_json["operatingHours"]
                hours_list = []
                for hour in hours:
                    if hour["open"] is not None and len(hour["open"]) > 0:
                        day = hour["name"]
                        time = hour["open"] + "-" + hour["close"]
                        hours_list.append(day + ":" + time)

                hours_of_operation = "; ".join(hours_list).strip()

                country_code = "GB"

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

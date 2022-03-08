# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "gas-station.info"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "authority": "api.nearest.place",
    "sec-ch-ua": '"Google Chrome";v="95", "Chromium";v="95", ";Not A Brand";v="99"',
    "accept": "*/*",
    "content-type": "application/json",
    "x-apikey": "AUY6koebnyee9NPJ",
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
    "sec-ch-ua-platform": '"Windows"',
    "origin": "https://gas-station.info",
    "sec-fetch-site": "cross-site",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "referer": "https://gas-station.info/",
    "accept-language": "en-US,en;q=0.9,ar;q=0.8",
}

data = '{"query":"query getLocationList($app: String!, $lat: Float!, $lng: Float!, $limit: Int!, $radius: Int!, $filter: [[String]]) {\\n  getNearestNodesByPoint(app: $app, lat: $lat, lng: $lng, limit: $limit, radius: $radius, filter: $filter) {\\n    id\\n    address {\\n      address\\n      city\\n      postal\\n      w3w\\n      formatted_name\\n      country\\n      timezone\\n      __typename\\n    }\\n    elements\\n    geojson {\\n      geometry {\\n        coordinates\\n        __typename\\n      }\\n      __typename\\n    }\\n    __typename\\n  }\\n}\\n","variables":{"app":"9T6wpGPFQs9Sar3nv","lat":31.587894,"lng":36.35376,"limit":1000,"radius":723363,"filter":[]},"operationName":"getLocationList"}'


def fetch_data():
    # Your scraper here
    search_url = "https://gas-station.info/en"
    api_url = "https://api.nearest.place/graphql"

    with SgRequests() as session:
        api_res = session.post(api_url, headers=headers, data=data)
        json_res = json.loads(api_res.text)

        stores = json_res["data"]["getNearestNodesByPoint"]

        for idx, store in enumerate(stores, 1):

            locator_domain = website

            location_name = "Gas Station"

            elements = store["elements"]
            for elem in elements:
                if elem["key"] == "locationName":
                    location_name = elem["value"][0]["value"].strip()

            page_url = (
                search_url
                + "/p/"
                + location_name.lower().replace(" ", "-")
                + "/"
                + store["id"]
            )

            raw_address = "<MISSING>"

            street_address = store["address"]["address"]

            city = store["address"]["city"]
            state = "<MISSING>"
            zip = store["address"]["postal"]

            country_code = store["address"]["country"]
            if country_code != "JOR":
                continue
            phone = "<MISSING>"
            location_type = "<MISSING>"

            store_number = store["id"]

            hours_of_operation = "<MISSING>"

            latitude, longitude = (
                store["geojson"]["geometry"]["coordinates"][0],
                store["geojson"]["geometry"]["coordinates"][1],
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

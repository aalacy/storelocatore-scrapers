# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json

website = "dierbergs.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "authority": "api.dierbergs.com",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="98", "Google Chrome";v="98"',
    "accept": "*/*",
    "authorization": "",
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36",
    "sec-ch-ua-platform": '"Windows"',
    "origin": "https://www.dierbergs.com",
    "sec-fetch-site": "same-site",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "referer": "https://www.dierbergs.com/",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}

json_data = {
    "operationName": "SearchStoresByCoord",
    "variables": {},
    "query": "query SearchStoresByCoord($lat: String, $long: String) {\n  locations(lat: $lat, long: $long) {\n    distance\n    ...LocationFields\n    __typename\n  }\n}\n\nfragment LocationFields on Location {\n  id\n  name\n  image\n  location\n  locationId\n  googleMapsUrl\n  streetAddress\n  zipCode\n  city\n  state\n  name\n  director\n  number\n  phone\n  departments {\n    hours {\n      id\n      end\n      start\n      __typename\n    }\n    name\n    phone\n    __typename\n  }\n  scheduledHours {\n    date\n    operatingHours {\n      end\n      start\n      __typename\n    }\n    __typename\n  }\n  hours {\n    day\n    operatingHours {\n      id\n      start\n      end\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n",
}


def fetch_data():
    # Your scraper here
    with SgRequests() as session:
        stores_req = session.post(
            "https://api.dierbergs.com/graphql/", headers=headers, data=json_data
        )
        stores = json.loads(stores_req.text)["data"]["locations"]
        for store in stores:
            locator_domain = website
            location_name = store["name"]
            street_address = store["streetAddress"]
            city = store["city"]
            state = store["state"]
            zip = store["zipCode"]

            country_code = "US"

            store_number = store["locationId"]
            phone = store["phone"]
            location_type = store["__typename"]
            ID = store["id"]

            page_url = f"https://www.dierbergs.com/store-locations/{ID}"
            latitude = store["location"].split("/")[1].strip()
            longitude = store["location"].split("/")[0].strip()
            hours = store["hours"]
            hours_list = []
            for hour in hours:
                day = hour["day"]
                time = (
                    hour["operatingHours"]["start"]
                    + " - "
                    + hour["operatingHours"]["end"]
                )

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

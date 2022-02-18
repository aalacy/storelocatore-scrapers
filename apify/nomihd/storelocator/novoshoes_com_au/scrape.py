# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
import json
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "novoshoes.com.au"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "authority": "code.metalocator.com",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="98", "Google Chrome";v="98"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.82 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "none",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}

params = (
    ("option", "com_locator"),
    ("view", "directory"),
    ("layout", "combined"),
    ("Itemid", "9067"),
    ("tmpl", "component"),
    ("framed", "1"),
    ("source", "js"),
)


def fetch_data():
    # Your scraper here
    search_url = "https://code.metalocator.com/index.php"
    with SgRequests() as session:
        stores_req = session.get(search_url, headers=headers, params=params)
        stores = json.loads(
            stores_req.text.split("var location_data =")[1]
            .strip()
            .split("}];")[0]
            .strip()
            + "}]"
        )

        for store in stores:
            store_number = store["id"]
            page_url = f"https://novo.locationlandingpages.com/{store_number}/9067"
            locator_domain = website
            location_name = store["name"]

            street_address = store["address"]
            if "address2" in store and len(store["address2"]) > 0:
                street_address = street_address + ", " + store["address2"]

            city = store["city"]
            state = store["state"]
            zip = store["postalcode"]

            country_code = store["country"]
            phone = store.get("phone", "<MISSING>")

            location_type = "<MISSING>"

            latitude = store["lat"]
            longitude = store["lng"]

            hours_of_operation = "<MISSING>"
            if "hours" in store:
                hours = store["hours"].split("}")[:-1]
                hours_list = []
                for hour in hours:
                    day = hour.split("|")[0].strip().replace("{", "").strip()
                    time = hour.split("|")[1].strip()
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

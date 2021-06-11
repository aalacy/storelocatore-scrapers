# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json

website = "ipre.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36",
}


def fetch_data():
    # Your scraper here

    search_url = "https://maps.offices.keyes.com/api/getAsyncLocations?template=domainIpre&level=domain"
    search_res = session.get(search_url, headers=headers)

    json_text = (
        "[{"
        + json.loads(search_res.text)["maplist"]
        .split(">{")[1]
        .strip()
        .split(",</div>")[0]
        .strip()
        + "]"
    )
    json_text = (
        json_text.replace('"', '"')
        .strip()
        .replace("\r\n", "")
        .strip()
        .replace('\\"', "'")
        .strip()
    )
    stores = json.loads(json_text)

    for store in stores:

        page_url = store["url"]
        locator_domain = website

        location_name = store["location_name"]

        street_address = store["address_1"]

        if (
            "address_2" in store
            and store["address_2"] is not None
            and len(store["address_2"]) > 0
        ):
            street_address = street_address + ", " + store["address_2"]

        city = store["city"]
        state = store["region"]
        zip = store["post_code"]

        country_code = store["country"]

        store_number = store["fid"]

        phone = store["local_phone"]

        location_type = "<MISSING>"

        hours_list = []
        try:
            hours = json.loads(store["hours_sets:primary"].replace("'", '"').strip())[
                "days"
            ]
            for day in hours.keys():
                time = hours[day][0]["open"] + " - " + hours[day][0]["close"]
                hours_list.append(day + ":" + time)

        except:
            pass

        hours_of_operation = "; ".join(hours_list).strip()
        latitude = store["lat"]
        longitude = store["lng"]

        raw_address = "<MISSING>"

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
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()

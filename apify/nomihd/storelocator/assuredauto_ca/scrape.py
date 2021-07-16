# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json

website = "assuredauto.ca"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.assuredauto.ca/locations"
    stores_req = session.get(search_url, headers=headers)
    stores_array = (
        stores_req.text.split("values:[")[1].strip().rsplit("],", 1)[0].strip() + "]"
    ).split("options:")[:-1]
    for store in stores_array:
        store_text = "{" + store.split("data: {")[1].strip().rsplit(",", 1)[0].strip()
        store_json = json.loads(store_text)
        page_url = "https://www.assuredauto.ca" + store_json["aliasurl"]

        locator_domain = website
        location_name = store_json["fullname"]
        street_address = store_json["address"]
        if (
            "address2" in store
            and store_json["address2"] is not None
            and len(store_json["address2"]) > 0
        ):
            street_address = street_address + ", " + store_json["address2"]

        if "," in street_address[-1]:
            street_address = "".join(street_address[:-1]).strip()

        city = store_json["city"]
        state = store_json["state"]
        zip = store_json["zip"]
        country_code = store_json["country"]

        phone = store_json["phone"]
        store_number = store_json["id"]
        location_type = "<MISSING>"

        hours_list = []
        if store_json["hoursstruct"] is not None and len(store_json["hoursstruct"]) > 0:
            hours = json.loads(store_json["hoursstruct"])
            days = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
            for index in range(0, len(hours)):
                day = days[index]
                if "ISCLOSED" in hours[index]:
                    if hours[index]["ISCLOSED"] == 1:
                        time = "CLOSED"
                        hours_list.append(day + ":" + time)
                else:
                    time = hours[index]["START"][0] + "-" + hours[index]["END"][0]
                    hours_list.append(day + ":" + time)

        hours_of_operation = "; ".join(hours_list).strip()
        latitude = store.split("latLng:[")[1].strip().split(",")[0].strip()
        longitude = (
            store.split("latLng:[")[1]
            .strip()
            .split(",")[1]
            .strip()
            .split("]")[0]
            .strip()
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

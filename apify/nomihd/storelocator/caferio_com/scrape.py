# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json

website = "caferio.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "authority": "ncr.trinitip.caferio-core.com",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="90", "Google Chrome";v="90"',
    "accept": "application/json, text/plain, */*",
    "x-trinitip-app-installation-id": "5fb4492158dcd50009c97f45",
    "x-trinitip-api-key": "5fb44823a9d0ae5e4df93daf",
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36",
    "content-type": "application/json",
    "origin": "https://www.caferio.com",
    "sec-fetch-site": "cross-site",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "referer": "https://www.caferio.com/",
    "accept-language": "en-US,en;q=0.9",
}

data = '{"customAttributes":["punchhLocationId"],"fields":["address","contact","hours","referenceId","timeZone"]}'


def fetch_data():
    # Your scraper here
    api_url = "https://ncr.trinitip.caferio-core.com/v1/sites/find"

    api_res = session.post(api_url, headers=headers, data=data)

    json_res = json.loads(api_res.text)

    store_list = json_res["pageContent"]
    for store in store_list:

        if "*TEST" in store["siteName"]:
            continue
        page_url = "https://www.caferio.com/locations/" + store[
            "enterpriseUnitName"
        ].lower().replace(" ", "-")
        locator_domain = website

        location_name = (
            store["siteName"]
            .replace("(NOTE: We are behind security in Concourse A)", "")
            .strip()
        )

        street_address = store["address"]["street"].strip()
        city = store["address"]["city"].strip()
        state = store["address"]["state"].strip()
        zip = store["address"]["postalCode"].strip()

        country_code = "US"
        store_number = store["referenceId"].strip()

        phone = (
            "("
            + store["contact"]["phoneNumberCountryCode"]
            + ")"
            + store["contact"]["phoneNumber"]
        )

        location_type = "<MISSING>"
        try:
            location_type = "(" + location_name.split("(", 1)[1].strip()
            location_name = location_name.split("(", 1)[0].strip()
        except:
            pass
        if store["hours"]:
            hours = store["hours"]
            hours_list = []
            for hour in hours:

                day = hour["open"]["day"]
                open_time = hour["open"]["time"]
                close_time = hour["close"]["time"]
                timing = f"{open_time[0:2]+':'+open_time[2:]} - {close_time[0:2]+':'+close_time[2:]}"

                hours_list.append(f"{day}: {timing}")

            hours_of_operation = "; ".join(hours_list)
        else:
            hours_of_operation = "<MISSING>"

        latitude = store["coordinates"]["latitude"]
        longitude = store["coordinates"]["longitude"]

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

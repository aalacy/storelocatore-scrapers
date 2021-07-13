# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json

website = "alaskausa.org"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "authority": "www.alaskausa.org",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="90", "Google Chrome";v="90"',
    "sec-ch-ua-mobile": "?0",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "none",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "accept-language": "en-US,en;q=0.9,ar;q=0.8",
    "Referer": "https://www.alaskausa.org/service/branches.asp",
}


def getday(x):
    if x == "1":
        return "Mon"
    if x == "2":
        return "Tue"
    if x == "3":
        return "Wed"
    if x == "4":
        return "Thu"
    if x == "5":
        return "Fri"
    if x == "6":
        return "Sat"
    if x == "7":
        return "Sun"


def fetch_data():
    # Your scraper here

    search_url = "https://www.alaskausa.org/current/locations/locationsData.js.asp"
    search_res = session.get(search_url, headers=headers)

    store_list = search_res.text.split("var holidays =")[0].split(" = ")[2:]

    for store in store_list:
        json_text = (
            store.replace("\n", "")
            .replace("\r", "")
            .replace("\t", "")
            .replace("parseFloat(", "")
            .replace('"),', '",')
            .split("};")[0]
            .strip(",")
            + "}"
        )

        json_res = json.loads(json_text)
        if "branch" not in json_res:
            continue

        page_url = "https://www.alaskausa.org/service/branches.asp"
        locator_domain = website

        location_name = json_res["branch"]["name"]

        street_address = json_res["address1"]
        if (
            "address2" in json_res
            and json_res["address2"] is not None
            and json_res["address2"] != "null"
        ):
            street_address = (street_address + ", " + json_res["address2"]).strip(", ")

        city = json_res["city"]
        state = json_res["state"]
        zip = json_res["zip"]

        country_code = "US"

        store_number = json_res["branch"]["id"]
        phone = "<MISSING>"

        location_type = "<MISSING>"

        hours_info = json_res["branch"]["hours"]
        hour_list = []
        for hour in hours_info:
            if "Lobby" in hour["featureName"]:
                from_day = getday(hour["startDay"])
                to_day = getday(hour["endDay"])
                opens = hour["startTime"].split("T")[1].strip("0").strip(":")
                closes = hour["endTime"].split("T")[1].strip("0").strip(":")
                hour_list.append(f"{from_day} - {to_day}: {opens} - {closes}")
        hours_of_operation = "; ".join(hour_list)

        latitude, longitude = json_res["latitude"], json_res["longitude"]
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

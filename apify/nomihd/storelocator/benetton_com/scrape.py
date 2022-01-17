# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
import json
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "benetton.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "authority": "api.woosmap.com",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36",
    "sec-ch-ua-platform": '"Windows"',
    "accept": "*/*",
    "origin": "https://us.benetton.com",
    "sec-fetch-site": "cross-site",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here
    search_url = "https://us.benetton.com/store-locator"
    with SgRequests(dont_retry_status_codes=([404])) as session:
        stores_req = session.get(search_url)
        API_KEY = (
            stores_req.text.split('data-publicKey="')[1].strip().split('"')[0].strip()
        )
        params = (("key", API_KEY),)

        val_list = [
            "1-0-1",
            "1-0-0",
            "1-1-1",
            "1-1-0",
            "1-2-1",
            "1-2-0",
            "0-0-1",
            "0-0-0",
            "0-1-1",
            "0-1-0",
        ]
        id_list = []
        for val in val_list:
            stores_req = session.get(
                f"https://api.woosmap.com/tiles/{val}.grid.json",
                headers=headers,
                params=params,
            )
            if "data" in stores_req.text:
                stores = json.loads(stores_req.text)["data"]
                for store_ID in stores.keys():
                    store_number = stores[store_ID]["store_id"]
                    if store_number in id_list:
                        continue

                    id_list.append(store_number)

                    page_url = "<MISSING>"
                    log.info(f"fetching data for record having ID: {store_number}")
                    store_req = session.get(
                        "https://api.woosmap.com/stores/" + store_number,
                        headers=headers,
                        params=params,
                    )
                    store_json = json.loads(store_req.text)
                    locator_domain = website
                    prop = store_json["properties"]
                    location_name = prop["name"]
                    raw_address = ""
                    street_address = ", ".join(prop["address"]["lines"]).strip()
                    if street_address:
                        raw_address = street_address

                    city = prop["address"]["city"]
                    if city:
                        raw_address = raw_address + ", " + city

                    state = "<MISSING>"
                    zip = prop["address"]["zipcode"]
                    if zip:
                        if zip == "." or zip == "-":
                            zip = "<MISSING>"
                        else:
                            raw_address = raw_address + ", " + zip

                    country_code = prop["address"]["country_code"]

                    phone = prop["contact"]["phone"]
                    if not phone:
                        phone = "<MISSING>"

                    if phone and phone == "null":
                        phone = "<MISSING>"

                    location_type = "<MISSING>"

                    latitude = store_json["geometry"]["coordinates"][1]
                    longitude = store_json["geometry"]["coordinates"][0]

                    hours_of_operation = "<MISSING>"
                    hours_list = []
                    try:
                        hours = prop["opening_hours"]["usual"]  # mon-sun
                        for day_val in hours.keys():
                            day = ""
                            if day_val == "1":
                                day = "Monday:"
                            if day_val == "2":
                                day = "Tuesday:"
                            if day_val == "3":
                                day = "Wednesday:"
                            if day_val == "4":
                                day = "Thursday:"
                            if day_val == "5":
                                day = "Friday:"
                            if day_val == "6":
                                day = "Saturday:"
                            if day_val == "7":
                                day = "Sunday:"

                            start = hours[day_val][0]["start"]
                            end = hours[day_val][0]["end"]
                            time = start + " - " + end
                            hours_list.append(day + time)
                    except:
                        pass

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

# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json

website = "kingsfamily.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    # Your scraper here

    search_url = "https://www.kingsfamily.com/wp-json/wp/v2/location?filter[orderby]=date&per_page=100"
    stores_req = session.get(search_url, headers=headers)
    stores = json.loads(stores_req.text)

    store_header = {
        "authority": "www.kingsfamily.com",
        "cache-control": "max-age=0",
        "sec-ch-ua": '"Chromium";v="88", "Google Chrome";v="88", ";Not A Brand";v="99"',
        "sec-ch-ua-mobile": "?0",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "sec-fetch-site": "same-origin",
        "sec-fetch-mode": "navigate",
        "sec-fetch-user": "?1",
        "sec-fetch-dest": "document",
        "referer": "https://www.kingsfamily.com/locations/",
        "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
    }

    for store in stores:
        page_url = store["link"]
        location_type = "<MISSING>"
        location_name = store["title"]["rendered"]
        locator_domain = website

        log.info(page_url)
        store_req = session.get(page_url, headers=store_header)
        locID = (
            store_req.text.split('"locId":')[1]
            .strip()
            .split(",")[0]
            .strip()
            .replace('"', "")
            .strip()
        )

        store_json = json.loads(
            session.get(
                "https://api.momentfeed.com/v1/lf/location/store-info/{}".format(locID)
            ).text
        )

        street_address = store_json["address"]
        if (
            store_json["addressExtended"] is not None
            and len(store_json["addressExtended"]) > 0
        ):
            street_address = street_address + ", " + store_json["addressExtended"]

        city = store_json["locality"]
        state = store_json["region"]
        zip = store_json["postcode"]
        country_code = store_json["country"]

        phone = store_json["phone"]
        location_type = store_json["status"]

        hours_list = []
        if location_type == "open":
            hours = store_json["hours"].split(";")
            for index in range(0, len(hours) - 1):
                day_val = hours[index].split(",")[0].strip()
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

                hours_list.append(
                    day + hours[index].split(",", 1)[1].replace(",", " - ").strip()
                )

        hours_of_operation = (
            "; ".join(hours_list)
            .strip()
            .encode("ascii", "replace")
            .decode("utf-8")
            .replace("?", "-")
            .strip()
        )

        store_number = store["id"]

        latitude = store["metaval"]["location_lat"][0]
        longitude = store["metaval"]["location_lng"][0]

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

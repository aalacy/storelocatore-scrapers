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

params_2 = (
    ("option", "com_locator"),
    ("view", "directory"),
    ("force_link", "1"),
    ("tmpl", "component"),
    ("task", "search_zip"),
    ("framed", "1"),
    ("format", "raw"),
    ("no_html", "1"),
    ("templ/[/]", "address_format"),
    ("layout", "_jsonfast"),
    ("radius", "25"),
    ("interface_revision", "58"),
    ("user_lat", "0"),
    ("user_lng", "0"),
    ("state", ""),
    ("Itemid", "9450"),
    ("ml_skip_interstitial", "0"),
    ("preview", "0"),
    ("parent_table", ""),
    ("parent_id", "0"),
    ("search_type", "point"),
    ("_opt_out", ""),
    ("ml_location_override", ""),
    ("reset", "true"),
    ("nearest", "false"),
    ("national", "true"),
)


def fetch_data():
    # Your scraper here
    search_url = "https://code.metalocator.com/index.php"
    with SgRequests() as session:
        for index in range(0, 2):  # first australia, 2nd newzealand
            if index == 0:
                data = params
            else:
                data = params_2

            stores_req = session.get(search_url, headers=headers, params=data)
            if index == 0:
                stores = json.loads(
                    stores_req.text.split("var location_data =")[1]
                    .strip()
                    .split("}];")[0]
                    .strip()
                    + "}]"
                )
            else:
                stores = stores_req.json()

            for store in stores:
                store_number = store["id"]
                if index == 0:
                    page_url = (
                        f"https://novo.locationlandingpages.com/{store_number}/9067"
                    )
                else:
                    page_url = "https://www.novoshoes.co.nz/store-locator"

                locator_domain = website
                location_name = store["name"]

                street_address = store["address"]
                if "address2" in store and len(store["address2"]) > 0:
                    street_address = street_address + ", " + store["address2"]

                city = store.get("city", "<MISSING>")
                state = store.get("state", "<MISSING>")
                zip = store.get("postalcode", "<MISSING>")

                raw_address = ""
                if len(street_address) > 0 and street_address != "<MISSING>":
                    raw_address = street_address

                if len(city) > 0 and city != "<MISSING>":
                    raw_address = raw_address + ", " + city

                if len(state) > 0 and state != "<MISSING>":
                    raw_address = raw_address + ", " + state

                if len(zip) > 0 and zip != "<MISSING>":
                    raw_address = raw_address + ", " + zip

                if len(street_address.split(",")) >= 2:
                    if "shop" in street_address.split(",")[0].strip().lower():
                        street_address = ", ".join(
                            street_address.split(",")[1:]
                        ).strip()

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

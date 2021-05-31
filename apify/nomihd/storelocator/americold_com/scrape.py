# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape import sgpostal as parser
import json

website = "americold.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "Connection": "keep-alive",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="90", "Google Chrome";v="90"',
    "Accept": "*/*",
    "X-Requested-With": "XMLHttpRequest",
    "sec-ch-ua-mobile": "?0",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
    "X-WPGMZA-Action-Nonce": "0ba742e607",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "Origin": "https://www.americold.com",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Dest": "empty",
    "Accept-Language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here

    search_url = "https://www.americold.com/wp-admin/admin-ajax.php?fields%5B%5D=id&filter=%7B%22map_id%22%3A%2223%22%2C%22center%22%3A%7B%22lat%22%3A40.75368539999999%2C%22lng%22%3A-73.9991637%7D%2C%22radius%22%3A%223000000%22%2C%22mashupIDs%22%3A%5B%5D%2C%22customFields%22%3A%5B%5D%7D&route=%2Fmarkers&action=wpgmza_rest_api_request"
    search_req = session.get(search_url, headers=headers)
    store_ids = json.loads(search_req.text)
    ID_LIST = []
    for ids in store_ids:
        ID_LIST.append(ids["id"])
    data = {
        "phpClass": "WPGMZA\\MarkerListing\\Carousel",
        "map_id": "23",
        "overrideMarkerIDs": ",".join(ID_LIST),
        "filteringParams[map_id]": "23",
        "filteringParams[center][lat]": "40.75368539999999",
        "filteringParams[center][lng]": "-73.9991637",
        "filteringParams[radius]": "300000",
        "route": "/marker-listing/",
        "action": "wpgmza_rest_api_request",
    }

    stores_res = session.post(
        "https://www.americold.com/wp-admin/admin-ajax.php", headers=headers, data=data
    )
    stores = json.loads(stores_res.text.replace("&nbsp;", "").strip())["meta"]
    for store in stores:
        page_url = store["link"]
        location_name = store["title"]
        location_type = "<MISSING>"
        locator_domain = website

        raw_address = store["address"]
        formatted_addr = parser.parse_address_intl(raw_address)
        street_address = formatted_addr.street_address_1
        if formatted_addr.street_address_2:
            street_address = street_address + ", " + formatted_addr.street_address_2

        city = formatted_addr.city
        state = formatted_addr.state
        zipp = formatted_addr.postcode
        country_code = formatted_addr.country
        phone = "<MISSING>"
        try:
            phone = (
                store["description"]
                .split("Telephone:")[1]
                .strip()
                .split("strong>")[1]
                .strip()
                .split("<")[0]
                .strip()
            )
        except:
            pass

        if phone == "<MISSING>":
            try:
                phone = (
                    store["description"]
                    .split("Tel:")[1]
                    .strip()
                    .split("strong>")[1]
                    .strip()
                    .split("<")[0]
                    .strip()
                )
            except:
                pass

        if phone == "<MISSING>" and zipp is not None and ("." in zipp or "-" in zipp):
            phone = zipp
            zipp = "<MISSING>"
            raw_address = raw_address.replace(phone, "").strip()
        hours_of_operation = "<MISSING>"

        store_number = "<MISSING>"

        latitude = store["lat"]
        longitude = store["lng"]

        yield SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zipp,
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

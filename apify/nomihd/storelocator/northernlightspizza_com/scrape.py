# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape import sgpostal as parser
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json

website = "northernlightspizza.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "authority": "www.northernlightspizza.com",
    "sec-ch-ua": '"Chromium";v="88", "Google Chrome";v="88", ";Not A Brand";v="99"',
    "accept": "*/*",
    "x-requested-with": "XMLHttpRequest",
    "sec-ch-ua-mobile": "?0",
    "x-wp-nonce": "8bd42dc3e8",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36",
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "referer": "https://www.northernlightspizza.com/locations/",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here
    loc_list = []

    url_list = [
        "https://www.northernlightspizza.com/wp-json/wpgmza/v1/markers/base64eJyrVkrLzClJLVKyUqqOUcpNLIjPTIlRsopRMopR0gEJFGeUgsSKgYLRsbVKtQCWBhBO",
        "https://www.northernlightspizza.com/wp-json/wpgmza/v1/markers/base64eJyrVkrLzClJLVKyUqqOUcpNLIjPTIlRsopRMo5R0gEJFGeUgsSKgYLRsbVKtQCWHhBP",
    ]
    for search_url in url_list:
        stores_req = session.get(search_url, headers=headers)
        stores = json.loads(stores_req.text)

        for store in stores:
            page_url = "https://www.northernlightspizza.com/locations/"
            location_type = "<MISSING>"
            location_name = store["title"]
            locator_domain = website

            raw_address = store["address"].strip()
            formatted_addr = parser.parse_address_usa(raw_address)
            street_address = formatted_addr.street_address_1
            if formatted_addr.street_address_2:
                street_address = street_address + ", " + formatted_addr.street_address_2

            city = formatted_addr.city
            state = formatted_addr.state
            if "," in state:
                state = state.split(",")[0].strip()
            zip = formatted_addr.postcode
            country_code = formatted_addr.country

            phone = ""
            hours_of_operation = ""
            if "Hours" in store["description"]:
                phone = store["description"].split("Hours")[0].strip()
                hours_of_operation = "; ".join(
                    store["description"].split("Hours")[1].strip().split("\n")
                ).strip()
            elif "\n" in store["description"]:
                phone = (
                    store["description"]
                    .split("\n")[1]
                    .strip()
                    .replace("(", "")
                    .replace(")", "-")
                    .strip()
                    .replace("- ", "-")
                    .strip()
                )
                if not phone[0].isdigit():
                    phone = store["description"].split("\n")[0].strip()

            elif "<br />" in store["description"]:
                phone = store["description"].split("<br />", 1)[0].strip()
                hours_of_operation = "; ".join(
                    store["description"].split("<br />", 1)[1].strip().split("<br />")
                ).strip()

            hours_of_operation = (
                hours_of_operation.replace("</p>", "")
                .strip()
                .encode("ascii", "replace")
                .decode("utf-8")
                .replace("?", "-")
                .strip()
            )
            phone = phone.replace("<p>", "").replace("NOW OPEN!", "").strip()
            location_type = "<MISSING>"

            store_number = store["id"]

            latitude = store["lat"]
            longitude = store["lng"]

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

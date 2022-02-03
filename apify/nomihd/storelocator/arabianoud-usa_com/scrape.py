# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgpostal import sgpostal as parser
import json
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "arabianoud-usa.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "authority": "arabianoud-usa.com",
    "sec-ch-ua": '" Not;A Brand";v="99", "Google Chrome";v="97", "Chromium";v="97"',
    "accept": "*/*",
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    "x-requested-with": "XMLHttpRequest",
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36",
    "sec-ch-ua-platform": '"Windows"',
    "origin": "https://arabianoud-usa.com",
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "referer": "https://arabianoud-usa.com/find-stores/",
    "accept-language": "en-US,en;q=0.9,ar;q=0.8",
}

data = {
    "latitude": "",
    "longitude": "",
    "geolocation": "no",
    "number_results_to_show": "5",
    "results_info_to_show": "",
    "action": "yith_sl_get_results",
    "product": "",
    "context": "frontend",
}


def fetch_data():
    # Your scraper here

    api_url = "https://arabianoud-usa.com/wp-admin/admin-ajax.php"

    with SgRequests() as session:
        api_res = session.post(api_url, headers=headers, data=data)

        json_res = json.loads(api_res.text)
        stores = json_res["markers"]

        for no, store in enumerate(stores, 1):

            locator_domain = website

            page_url = "https://arabianoud-usa.com/store-locator/" + store["slug"] + "/"

            log.info(page_url)
            store_res = session.get(page_url, headers=headers)
            store_sel = lxml.html.fromstring(store_res.text)

            location_name = store["name"].strip()

            location_type = "<MISSING>"

            store_info = list(
                filter(
                    str,
                    [
                        x.strip()
                        for x in store_sel.xpath(
                            '//div[@class="wrap-single-info location "]//div[@class="info"]//text()'
                        )
                    ],
                )
            )

            raw_address = ", ".join(store_info)

            formatted_addr = parser.parse_address_intl(raw_address)
            street_address = formatted_addr.street_address_1
            if formatted_addr.street_address_2:
                street_address = street_address + ", " + formatted_addr.street_address_2

            if street_address is not None:
                street_address = street_address.replace("Ste", "Suite")

            if street_address and "UNDEFINED" in street_address.upper():
                street_address = "<MISSING>"

            city = formatted_addr.city

            state = formatted_addr.state

            zip = formatted_addr.postcode
            if zip and "UNDEFINED" in zip.upper():
                zip = "<MISSING>"

            country_code = formatted_addr.country
            if not country_code:
                country_code = raw_address.split(" ")[-1].strip()
                if country_code == "Emirates":
                    country_code = "UAE"

            phone = store_sel.xpath(
                '//div[@class="wrap-single-info contact"]//div[@class="info"]//text()'
            )
            phone = " ".join(phone)
            if "Phone:" in phone:
                phone = phone.split("Phone:")[1].split("Website")[0].strip()
            else:
                phone = "<MISSING>"

            hours = list(
                filter(
                    str,
                    [
                        x.strip()
                        for x in store_sel.xpath(
                            '//div[@class="wrap-single-info opening-hours"]//div[@class="info"]//text()'
                        )
                    ],
                )
            )

            hours_of_operation = (
                "; ".join(hours)
                .strip()
                .replace("Opening hours", "")
                .strip()
                .replace("Opening hours :", "")
                .strip()
                .replace("Opening hours :;", "")
                .strip()
                .replace("Welcome to our Arabian Oud Outlet;", "")
                .strip()
            )
            if len(hours_of_operation) > 0 and hours_of_operation[0] == ":":
                hours_of_operation = "".join(hours_of_operation[1:]).strip()

            if (
                len(hours_of_operation) > 0
                and hours_of_operation[0] == ":"
                and hours_of_operation[1] == ";"
            ):
                hours_of_operation = "".join(hours_of_operation[2:]).strip()

            if len(hours_of_operation) > 0 and hours_of_operation[0] == ";":
                hours_of_operation = "".join(hours_of_operation[1:]).strip()

            if "opening soon" in hours_of_operation.lower():
                hours_of_operation = "<MISSING>"
                location_type = "Coming Soon"

            store_number = store["id"]

            latitude, longitude = store["latitude"], store["longitude"]
            if latitude == longitude:
                latitude = longitude = "<MISSING>"

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
                phone=phone.split("Email:")[0].strip(),
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
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PageUrlId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()

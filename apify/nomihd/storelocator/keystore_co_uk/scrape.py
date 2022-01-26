# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgpostal import sgpostal as parser
import lxml.html
import json
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "keystore.co.uk"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "authority": "www.keystore.co.uk",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
    "accept": "application/json, text/javascript, */*; q=0.01",
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    "x-requested-with": "XMLHttpRequest",
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
    "sec-ch-ua-platform": '"Windows"',
    "origin": "https://www.keystore.co.uk",
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "referer": "https://www.keystore.co.uk/store-locator/",
    "accept-language": "en-US,en;q=0.9,ar;q=0.8",
}

data = {"action": "get_all_stores", "lat": "", "lng": ""}


def fetch_data():
    # Your scraper here
    api_url = "https://www.keystore.co.uk/wp-admin/admin-ajax.php"

    with SgRequests() as session:
        api_res = session.post(api_url, headers=headers, data=data)

        stores = json.loads(api_res.text)

        for _, store in stores.items():

            locator_domain = website

            location_name = store["ic"].split("/")[-1].split("-")[0]
            if len(location_name.split("KeyStore")) > 1:
                location_name = (
                    "KeyStore " + location_name.split("KeyStore")[-1].strip()
                )

            location_type = location_name

            page_url = store["gu"]
            log.info(page_url)
            store_res = session.get(page_url, headers=headers)
            store_sel = lxml.html.fromstring(store_res.text)

            store_info = list(
                filter(
                    str,
                    [x.strip() for x in store_sel.xpath('//div[h2="Address"]//text()')],
                )
            )
            raw_address = ", ".join(store_info[1:])
            raw_address = (
                raw_address.replace("Scotland, GB", "")
                .replace("England, GB", "")
                .strip()
            )
            formatted_addr = parser.parse_address_intl(raw_address)
            street_address = formatted_addr.street_address_1
            if formatted_addr.street_address_2:
                street_address = street_address + ", " + formatted_addr.street_address_2

            city = formatted_addr.city

            if street_address is not None:
                street_address = (
                    street_address.replace("Ste", "Suite")
                    .replace("G75 8Rq", "")
                    .strip()
                    .replace("Pa16", "")
                    .replace("Fk2 0Xf", "")
                    .replace("Pa21 2Ad", "")
                    .replace("Fk20 8Ry", "")
                    .replace("Td13 5Yp", "")
                    .replace("Ph36 4Hz", "")
                )
                if "Knottingly" in street_address:
                    street_address = street_address.replace("Knottingly", "").strip()
                    city = "Knottingly"

            state = "<MISSING>"

            zip = store["zp"]
            if not zip:
                zip = formatted_addr.postcode

            country_code = "GB"

            phone = store.get("te", "<MISSING>")

            hours = list(
                filter(
                    str,
                    [
                        x.strip()
                        for x in store_sel.xpath('//div[h2="Opening Hours"]//text()')
                    ],
                )
            )

            hours_of_operation = (
                "; ".join(hours[1:])
                .replace("day;", "day:")
                .replace("Fri;", "Fri:")
                .replace("Sat;", "Sat:")
                .replace("Sun;", "Sun:")
                .replace("Thurs;", "Thurs:")
                .replace(":;", ":")
            )

            store_number = store["ID"]

            latitude, longitude = store["lat"], store["lng"]
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

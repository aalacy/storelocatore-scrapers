# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
import json
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "pepsibottlingventures.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "authority": "www.pepsibottlingventures.com",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
    "accept": "application/json, text/javascript, */*; q=0.01",
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    "x-requested-with": "XMLHttpRequest",
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "accept-language": "en-US,en;q=0.9,ar;q=0.8",
}


def fetch_data():
    # Your scraper here

    search_url = "https://www.pepsibottlingventures.com/locations"

    with SgRequests() as session:
        search_res = session.get(search_url, headers=headers)
        search_sel = lxml.html.fromstring(search_res.text)

        json_str = (
            search_res.text.split("data-location=")[1]
            .split("data-property")[0]
            .replace("&quot;", '"')
            .strip()
            .strip('"')
        )

        json_res = json.loads(json_str)

        stores = json_res

        for no, store in enumerate(stores, 1):

            locator_domain = website
            location_name = store["title"].strip().replace("&amp;", "&").strip()

            store_info = list(
                filter(
                    str,
                    [
                        x.strip()
                        for x in search_sel.xpath(
                            f'//h5//span[contains(text(),"{location_name.split(" ")[-1].strip()}")]/following::div[1]//p//text()'
                        )
                    ],
                )
            )
            store_number = "<MISSING>"

            page_url = search_url

            location_type = "<MISSING>"

            raw_address = "<MISSING>"

            street_address = store["address1"]
            if store["address2"] is not None:
                street_address = (street_address + ", " + store["address2"]).strip()
            if street_address is not None:
                street_address = street_address.replace("Ste", "Suite")

            if street_address and street_address[-1] == ",":
                street_address = "".join(street_address[:-1]).strip()

            city = store["city"]

            state = store["state"]
            zip = store["zipcode"]

            country_code = "US"

            phone = store_info[-1]

            hours_of_operation = "<MISSING>"

            latitude, longitude = store["Latitude"], store["Longitude"]
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
        deduper=SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.CITY,
                    SgRecord.Headers.STATE,
                    SgRecord.Headers.ZIP,
                }
            )
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()

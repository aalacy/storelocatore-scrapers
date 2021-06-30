# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
import json

website = "laprep.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.laprep.com/locations"
    states_req = session.get(search_url, headers=headers)
    states_sel = lxml.html.fromstring(states_req.text)
    states = states_sel.xpath('//div[@id="addressHeading1"]/a/@href')
    for state_url in states:
        log.info(state_url)
        stores_req = session.get(state_url, headers=headers)
        stores = stores_req.text.split("] = [")
        for index in range(1, len(stores)):
            json_text = (
                (
                    "["
                    + stores[index]
                    .replace("restaurants[" + str(index - 1), "")
                    .split("];")[0]
                    .strip()
                    + "]"
                )
                .replace("'\"", '"')
                .replace("\"'", '"')
                .replace("'", '"')
            )
            store_json = json.loads(json_text)

            page_url = state_url
            locator_domain = website
            location_name = store_json[0]

            street_address = store_json[1].strip()
            city = location_name
            state = state_url.split("/")[-1].strip()
            zip = "<MISSING>"

            country_code = "CA"

            store_number = "<MISSING>"
            location_type = "<MISSING>"

            phone = store_json[3].strip()
            hours_of_operation = (
                store_json[7].replace("<li>", "").replace("</li>", "").strip()
            )

            latitude = store_json[5]
            longitude = store_json[6]

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

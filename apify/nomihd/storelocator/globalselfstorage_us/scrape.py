# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
import lxml.html
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json
import us

website = "globalselfstorage.us"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    # Your scraper here

    search_url = "https://inventory.g5marketingcloud.com/api/v1/locations?client_id=7&per_page=1000&sort_by=state_then_city"
    stores_req = session.get(search_url, headers=headers)
    stores = json.loads(stores_req.text)["locations"]
    for store in stores:
        page_url = store["home_page_url"]
        location_type = "<MISSING>"
        locator_domain = website
        log.info(page_url)
        location_name = store["name"]

        street_address = store["street_address_1"]
        city = store["city"]
        state = store["state"]
        zip = store["postal_code"]
        country_code = "<MISSING>"
        if us.states.lookup(state):
            country_code = "US"

        phone = store["phone_number"]

        store_req = session.get(page_url, headers=headers)
        store_sel = lxml.html.fromstring(store_req.text)

        hours_of_operation = "<MISSING>"
        hours = store_sel.xpath('//div[@class="office-hours-condensed"]/div')
        hours_list = []
        for hour in hours:
            day = "".join(hour.xpath("label/text()")).strip()
            time = "".join(hour.xpath("span/text()")).strip()
            if len(day) > 0:
                hours_list.append(day + time)

        hours_of_operation = (
            "; ".join(hours_list)
            .strip()
            .encode("ascii", "replace")
            .decode("utf-8")
            .replace("?", "-")
            .strip()
        )
        store_number = store["id"]

        latitude = store["latitude"]
        longitude = store["longitude"]

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

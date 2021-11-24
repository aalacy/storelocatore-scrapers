# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
import lxml.html
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json

website = "theubank.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    # Your scraper here

    search_url = (
        "https://www.theubank.com/_/api/branches/40.75368539999999/-73.9991637/50000000"
    )
    stores_req = session.get(search_url, headers=headers)
    stores = json.loads(stores_req.text)["branches"]
    for store in stores:
        page_url = "<MISSING>"
        location_name = store["name"]
        location_type = "<MISSING>"
        locator_domain = website
        phone = store["phone"]

        street_address = store["address"]
        city = store["city"]
        state = store["state"]
        zipp = store["zip"]

        hours_sel = lxml.html.fromstring(store["description"])
        sections = hours_sel.xpath("//div")
        hours_list = []
        hours = []
        for index in range(0, len(sections)):
            if "Lobby Hours" in "".join(sections[index].xpath("b/text()")).strip():
                hours = sections[index + 1 :]
                break

        for hour in hours:
            if "Drive-Thru" in "".join(hour.xpath("b/text()")).strip():
                break
            if len("".join(hour.xpath(".//text()")).strip()) > 0:
                temp_hours = "; ".join(hour.xpath(".//text()")).strip()
                hours_list.append(temp_hours)

        hours_of_operation = "; ".join(hours_list).strip()
        country_code = "US"
        store_number = "<MISSING>"

        latitude = store["lat"]
        longitude = store["long"]

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
        )
        # break


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

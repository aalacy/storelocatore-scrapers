# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json
import lxml.html

website = "thpharmacy.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    # Your scraper here
    search_url = "https://thpharmacy.com/wp-admin/admin-ajax.php?action=store_search&lat=43.65323&lng=-79.38318&max_results=2500&search_radius=50000&autoload=1"
    stores_req = session.get(search_url, headers=headers)
    stores = json.loads(stores_req.text, strict=False)
    for store in stores:
        page_url = store["permalink"]

        locator_domain = website
        location_name = (
            store["store"]
            .replace("&#8217;", "'")
            .replace("&#8211;", "-")
            .strip()
            .replace("&#038;", "&")
            .strip()
        )
        street_address = store["address"]
        if (
            "address2" in store
            and store["address2"] is not None
            and len(store["address2"]) > 0
        ):
            street_address = street_address + ", " + store["address2"]

        if "," in street_address[-1]:
            street_address = "".join(street_address[:-1]).strip()
        city = store["city"]
        state = store["state"]
        zip = store["zip"]
        country_code = store["country"]

        phone = store["phone"]
        if "or" in phone:
            phone = phone.split("or")[0].strip()

        store_number = ""
        if "#" in location_name:
            store_number = location_name.split("#")[1].strip()

        location_type = "<MISSING>"

        hours_list = []
        if store["hours"] is not None and len(store["hours"]) > 0:
            hours = lxml.html.fromstring(store["hours"]).xpath("//tr")
            hours_list = []
            hours_of_operation = ""
            for hour in hours:
                day = "".join(hour.xpath("td[1]/text()")).strip()
                time = "".join(hour.xpath("td[2]//text()")).strip()
                hours_list.append(day + ":" + time)

        hours_of_operation = "; ".join(hours_list).strip()
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

# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
import lxml.html
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "salvatores.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    # Your scraper here

    search_url = "https://www.salvatores.com/locations"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    stores = stores_sel.xpath('//div[@class="location-list-item"]')
    for store in stores:
        if "COMING SOON" in "".join(store.xpath("h3/a/text()")).strip():
            continue

        page_url = (
            "https://www.salvatores.com" + "".join(store.xpath("h3/a/@href")).strip()
        )
        location_type = "<MISSING>"
        locator_domain = website
        log.info(page_url)
        store_req = session.get(page_url, headers=headers)
        store_sel = lxml.html.fromstring(store_req.text)
        json_list = store_sel.xpath('//script[@type="application/ld+json"]/text()')

        for js in json_list:
            if "streetAddress" in js:
                json_data = json.loads(js)

                location_name = json_data["name"]

                street_address = json_data["address"]["streetAddress"]
                city = json_data["address"]["addressLocality"]
                state = json_data["address"]["addressRegion"]
                zip = json_data["address"]["postalCode"]
                phone = json_data["telephone"]
                country_code = json_data["address"]["addressCountry"]
                if "geo" in json_data:
                    latitude = json_data["geo"]["lattitude"]
                    longitude = json_data["geo"]["longitude"]
                else:
                    latitude, longitude = "<MISSING>", "<MISSING>"

                hours_of_operation = "<MISSING>"
                hours = json_data["openingHoursSpecification"]
                hours_list = []
                for hour in hours:
                    days = hour["dayOfWeek"]
                    time = hour["opens"] + "-" + hour["closes"]
                    for day in days:
                        hours_list.append(day + ":" + time)

                hours_of_operation = (
                    "; ".join(hours_list)
                    .strip()
                    .encode("ascii", "replace")
                    .decode("utf-8")
                    .replace("?", "-")
                    .strip()
                )
                store_number = "<MISSING>"

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

# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
import lxml.html
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json

website = "whywaitintheer.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    # Your scraper here

    search_url = "https://whywaitintheer.com/locations/"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    stores = stores_sel.xpath('//div[@class="locations-grid-location"]')

    for store in stores:
        page_url = "".join(store.xpath("h4/a/@href"))
        log.info(page_url)
        location_type = "<MISSING>"
        locator_domain = website
        store_req = session.get(page_url, headers=headers)
        store_sel = lxml.html.fromstring(store_req.text)
        json_data = json.loads(
            "".join(store_sel.xpath('//script[@type="application/ld+json"]/text()'))
            .strip()
            .replace('"image":', '"image":""')
        )

        location_name = json_data["name"]

        street_address = json_data["address"]["streetAddress"]
        city = json_data["address"]["addressLocality"]
        state = json_data["address"]["addressRegion"]
        zip = json_data["address"]["postalCode"]
        country_code = json_data["address"]["addressCountry"]
        phone = "".join(
            store_sel.xpath(
                '//div[@class="fl-callout-text"]//a[contains(@href,"tel:")]/text()'
            )
        ).strip()
        hours_of_operation = "<MISSING>"
        store_number = "<MISSING>"
        hours = json_data["openingHoursSpecification"]
        hours_list = []

        for index in range(0, len(hours), 2):
            day = hours[index]["dayOfWeek"]
            time = hours[index]["opens"] + "-" + hours[index + 1]["opens"]
            hours_list.append(day + ":" + time)

        hours_of_operation = "; ".join(hours_list).strip()
        latitude = json_data["geo"]["latitude"]
        longitude = json_data["geo"]["longitude"]

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

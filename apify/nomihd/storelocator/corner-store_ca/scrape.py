# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json
import lxml.html

website = "corner-store.ca"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.corner-store.ca/en/find-corner-store/ajax_location/?location=que+bec&visitor_lat=46.8138783&visitor_lng=-71.2079809&place=Quebec+City+Communaut%C3%A9-Urbaine-de-Qu%C3%A9bec%2C+Quebec&services_filters_codes=&banners_filters_codes="
    stores_req = session.get(search_url, headers=headers)
    stores = json.loads(stores_req.text)["stores"]
    for store in stores:
        page_url = "https://www.corner-store.ca" + store["url"]
        locator_domain = website
        location_name = store["name"]
        street_address = store["address"]
        city = store["city"]
        state = store["province"]
        zip = store["postal_code"]
        country_code = "CA"
        log.info(page_url)
        store_req = session.get(page_url, headers=headers)
        store_sel = lxml.html.fromstring(store_req.text)
        phone = "".join(store_sel.xpath('//div[@class="store_phone"]/text()')).strip()

        store_number = store["pk"]
        location_type = "<MISSING>"

        hours_of_operation = "; ".join(
            store_sel.xpath(
                '//div[@class="store_open_hours"]//span[@itemprop="openingHours"]/text()'
            )
        ).strip()
        latitude = store["location"]["lat"]
        longitude = store["location"]["lng"]

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

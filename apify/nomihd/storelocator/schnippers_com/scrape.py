# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
import lxml.html
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json

website = "schnippers.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    # Your scraper here

    search_url = "https://www.schnippers.com/"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    json_list = stores_sel.xpath('//script[@type="application/ld+json"]/text()')
    if len(json_list) > 0:
        stores = json.loads(json_list[0])["subOrganization"]
        for store in stores:
            page_url = store["url"]
            location_type = "<MISSING>"
            locator_domain = website
            log.info(page_url)
            store_req = session.get(page_url, headers=headers)
            store_sel = lxml.html.fromstring(store_req.text)
            location_name = store["name"]

            street_address = store["address"]["streetAddress"]
            city = store["address"]["addressLocality"]
            state = store["address"]["addressRegion"]
            zip = store["address"]["postalCode"]
            country_code = "US"

            phone = store["telephone"]

            hours_of_operation = " ".join(
                store_sel.xpath('//section[@id="intro"]/p[position()>1]//text()')
            ).strip()
            store_number = "<MISSING>"

            latitude = "".join(store_sel.xpath('//div[@class="gmaps"]/@data-gmaps-lat'))
            longitude = "".join(
                store_sel.xpath('//div[@class="gmaps"]/@data-gmaps-lng')
            )

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

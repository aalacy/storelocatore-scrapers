# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "mrgreek.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.mrgreek.com/locations/"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    stores_raw_text = "".join(
        stores_sel.xpath('//script[contains(text(),"estHref")]/text()')
    ).strip()
    stores = stores_raw_text.split("googleMapsLocations.push(")
    for index in range(1, len(stores)):
        store_json = json.loads(stores[index].split(");")[0].strip())
        if "estHref" not in store_json:
            continue
        page_url = store_json["estHref"]
        locator_domain = website
        location_name = store_json["estName"].replace("&amp;", "&").strip()
        log.info(page_url)
        store_req = session.get(page_url, headers=headers)
        store_sel = lxml.html.fromstring(store_req.text)

        street_address = "".join(
            store_sel.xpath('//div[@class="address"]/span[@class="street"]/text()')
        ).strip()
        city = "".join(
            store_sel.xpath('//div[@class="address"]/span[@class="city"]/text()')
        ).strip()
        state = "".join(
            store_sel.xpath('//div[@class="address"]/span[@class="province"]/text()')
        ).strip()
        zip = "".join(
            store_sel.xpath('//div[@class="address"]/span[@class="postal"]/text()')
        ).strip()
        country_code = "Canada"

        phone = store_json["estPhone"]

        store_number = store_json["estID"]
        location_type = "<MISSING>"

        hours_url = page_url + "hours/"
        log.info(hours_url)
        hours_req = session.get(hours_url, headers=headers)
        hours_sel = lxml.html.fromstring(hours_req.text)
        hours = hours_sel.xpath('//table[@class="text_list list_hours"]//tr')
        hours_list = []
        for hour in hours:
            day = "".join(hour.xpath('td[@class="item_label"]/text()')).strip()
            time = "".join(hour.xpath('td[@class="item_value"]/text()')).strip()
            hours_list.append(day + ":" + time)

        hours_of_operation = "; ".join(hours_list).strip()
        latitude = store_json["centerLat"]
        longitude = store_json["centerLon"]

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
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.StoreNumberId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()

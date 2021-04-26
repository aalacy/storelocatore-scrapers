# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html

website = "starpt.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.starpt.com/star-physical-therapy-clinics/"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    stores = stores_sel.xpath('//div[@class="programs-wrap"]/div[position()>1]')

    for store in stores:
        page_url = "".join(store.xpath("div[1]/a/@href")).strip()
        locator_domain = website

        location_name = "".join(store.xpath("div[1]/a/text()")).strip()

        street_address = "".join(store.xpath("div[2]/text()")).strip()
        city = "".join(store.xpath("div[3]/text()")).strip()
        state = "".join(store.xpath("div[4]/text()")).strip()
        zip = "".join(store.xpath("div[5]/text()")).strip()

        country_code = "US"
        phone = "".join(store.xpath("div[6]/a[1]/text()")).strip()

        store_number = "<MISSING>"
        location_type = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        map_link = "".join(
            store.xpath('div[7]/a[contains(text(),"Directions")]/@href')
        ).strip()
        if len(map_link) > 0 and "destination" in map_link:
            latitude = map_link.split("destination=")[1].strip().split(",")[0].strip()
            longitude = map_link.split("destination=")[1].strip().split(",")[1].strip()

        log.info(page_url)
        store_req = session.get(page_url, headers=headers)
        store_sel = lxml.html.fromstring(store_req.text)

        hours_of_operation = ""
        hours = store_sel.xpath('//div[@class="day-time"]')
        hours_list = []
        for hour in hours:
            day = "".join(hour.xpath('div[@class="day"]/text()')).strip()
            time = "".join(hour.xpath('div[@class="time"]/text()')).strip()
            hours_list.append(day + ":" + time)

        hours_of_operation = "; ".join(hours_list).strip()

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

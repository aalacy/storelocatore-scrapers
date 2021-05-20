# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
import lxml.html
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter

website = "oldspaghettifactory.ca"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    # Your scraper here

    search_url = "https://oldspaghettifactory.ca/locations/"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    stores = stores_sel.xpath('//div[@class="location-info-wrap"]/a/@href')
    for store_url in stores:
        page_url = store_url
        location_type = "<MISSING>"
        locator_domain = website
        log.info(page_url)
        store_req = session.get(page_url, headers=headers)
        store_sel = lxml.html.fromstring(store_req.text)
        location_name = "".join(
            store_sel.xpath('//div[@class="location-content-wrap"]/h2/text()')
        ).strip()

        address = store_sel.xpath('//ul[@class="address"]/li/text()')
        street_address = ", ".join(address[:-1]).strip()
        city_zip = address[-1].strip()
        city = city_zip.split(",")[0].strip()
        state = "".join(
            store_sel.xpath('//div[@class="location-content-wrap"]/h3/text()')
        ).strip()
        zip = city_zip.split(",")[1].strip()
        country_code = "CA"

        sections = store_sel.xpath('//div[@class="location-content-wrap"]/ul')
        phone = ""
        try:
            phone = "".join(sections[-2].xpath("li[1]/span[2]/text()")).strip()
        except:
            pass

        hours_list = []
        try:
            hours = sections[-1].xpath("li")
            for hour in hours:
                day = "".join(hour.xpath("span[1]/text()")).strip()
                time = "".join(hour.xpath("span[2]/text()")).strip()
                hours_list.append(day + time)
        except:
            pass

        hours_of_operation = "; ".join(hours_list).strip()
        store_number = "<MISSING>"

        latitude = "".join(store_sel.xpath('//div[@class="marker"]/@data-lat'))
        longitude = "".join(store_sel.xpath('//div[@class="marker"]/@data-lng'))

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

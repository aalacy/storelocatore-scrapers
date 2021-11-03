# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
import lxml.html
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter

website = "centerforvein.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    # Your scraper here

    search_url = "https://www.centerforvein.com/find-a-center"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    stores = stores_sel.xpath('//li/a[@class="fourColumnTextList__group-link"]/@href')
    for store_url in stores:
        page_url = store_url
        location_type = "<MISSING>"
        locator_domain = website
        log.info(page_url)
        store_req = session.get(page_url, headers=headers)
        store_sel = lxml.html.fromstring(store_req.text)
        location_name = "".join(
            store_sel.xpath('//div[@class="locationSummary__header-inner"]/h1/text()')
        ).strip()

        address = (
            "".join(
                store_sel.xpath(
                    '//h5[@class="locationSummary__summary-title type__h5"]/text()'
                )
            )
            .strip()
            .split("\n")
        )
        street_address = ", ".join([x.strip() for x in address[:-1]]).strip()
        city = address[-1].strip().split(",")[0].strip()
        state = address[-1].strip().split(",")[1].strip().split(" ")[0].strip()
        zipp = ""
        if len(address[-1].strip().split(",")) == 3:
            zipp = address[-1].strip().split(",")[-1].strip()
        else:
            zipp = address[-1].strip().split(",")[1].strip().split(" ")[-1].strip()
        country_code = "US"
        phone = "".join(
            store_sel.xpath('//a[@class="locationSummary__summary-phone"]/span/text()')
        ).strip()
        days = store_sel.xpath('//dl[@class="locationSummary__summary-list"]/dt/text()')
        time = store_sel.xpath('//dl[@class="locationSummary__summary-list"]/dd/text()')
        hours_of_operation = ""
        hours_list = []
        for hour in zip(days, time):
            hours_list.append(hour[0] + ":" + hour[1])

        hours_of_operation = "; ".join(hours_list).strip()
        store_number = "<MISSING>"

        latitude = "<MISSING>"
        longitude = "<MISSING>"
        try:
            latitude = (
                store_req.text.split('"latitude":')[1].strip().split(",")[0].strip()
            )
            longitude = (
                store_req.text.split('"longitude":')[1].strip().split("}")[0].strip()
            )
        except:
            pass

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

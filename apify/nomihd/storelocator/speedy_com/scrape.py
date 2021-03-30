# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html

website = "speedy.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.speedy.com/ca-qc/en/shop-locator"
    stores_req = session.get(search_url, headers=headers)
    stores = stores_req.text.split("shop_info.push(")
    for index in range(1, len(stores)):
        page_url = (
            "https://www.speedy.com"
            + stores[index].split('url:"')[1].strip().split('",')[0].strip()
        )
        log.info(page_url)
        locator_domain = website
        location_name = (
            stores[index].split('shopname:"')[1].strip().split('",')[0].strip()
        )

        street_address = (
            stores[index].split('address: "')[1].strip().split('",')[0].strip()
        )
        city = stores[index].split('city: "')[1].strip().split('",')[0].strip()
        state = "<MISSING>"
        zip = (
            stores[index]
            .split('zip: "')[1]
            .strip()
            .split('",')[0]
            .strip()
            .replace("+", " ")
            .strip()
        )

        country_code = "CA"

        store_number = "<MISSING>"
        location_type = "<MISSING>"

        phone = stores[index].split('info:"')[1].strip().split('",')[0].strip()
        hours_of_operation = ""
        store_req = session.get(page_url, headers=headers)
        store_sel = lxml.html.fromstring(store_req.text)
        hours = store_sel.xpath(
            '//div[@class="table_info"]/div[@class="address-col2"]/div[1]/div'
        )
        hours_list = []
        for hour in hours:
            day = "".join(hour.xpath("div[1]//text()")).strip()
            time = "".join(hour.xpath("div[2]/div/div/span/text()")).strip()
            hours_list.append(day + time)

        hours_of_operation = (
            "; ".join(hours_list)
            .strip()
            .encode("ascii", "replace")
            .decode("utf-8")
            .replace("?", "-")
            .strip()
        )
        latitude = stores[index].split('lat:"')[1].strip().split('",')[0].strip()
        longitude = stores[index].split('lng:"')[1].strip().split('",')[0].strip()

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

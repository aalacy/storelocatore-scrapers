# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html

website = "roysrestaurant.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.roysrestaurant.com/locations/"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    stores = stores_sel.xpath(
        '//div[@class="large-4 four push-4 push-four columns"]/p/a/@href'
    )

    for store_url in stores:
        page_url = "https://www.roysrestaurant.com" + store_url
        log.info(page_url)
        store_req = session.get(page_url, headers=headers)
        store_sel = lxml.html.fromstring(store_req.text)

        locator_domain = website
        location_name = "".join(
            store_sel.xpath('//div[@class="header-info large-6 six columns"]/h1/text()')
        ).strip()

        raw_info = store_sel.xpath('//div[@id="address_contact"]/address/text()')
        raw_list = []
        for raw in raw_info:
            if len("".join(raw).strip()) > 0:
                raw_list.append("".join(raw).strip())

        street_address = ", ".join(raw_list[:-2])
        city_state_zip = raw_list[-2]
        city = city_state_zip.split(",")[0].strip()
        state = city_state_zip.split(",")[1].strip().split(" ")[0].strip()
        zip = city_state_zip.split(",")[1].strip().split(" ")[1].strip()

        country_code = "US"

        store_number = "<MISSING>"
        phone = raw_list[-1].strip()
        location_type = "<MISSING>"
        if (
            "temporarily closed"
            in "".join(
                store_sel.xpath(
                    '//div[@class="header-info large-6 six columns"]/p/text()'
                )
            ).strip()
        ):
            location_type = "temporarily closed"

        hours_list = []
        hours = store_sel.xpath('//div[@id="hours"]/div[1]/p')
        for index in range(0, len(hours), 2):
            label = "".join(hours[index].xpath("strong/text()")).strip()
            if len(label) > 0:
                time = "".join(hours[index + 1].xpath("text()")).strip()
                hours_list.append(label + time)

        hours_of_operation = (
            "; ".join(hours_list)
            .strip()
            .encode("ascii", "replace")
            .decode("utf-8")
            .replace("?", "-")
            .strip()
        )

        latitude = "<MISSING>"
        longitude = "<MISSING>"

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

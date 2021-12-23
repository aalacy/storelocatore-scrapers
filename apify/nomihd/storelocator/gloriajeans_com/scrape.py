# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
import us
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgselenium import SgChrome
import time
import ssl
from sgpostal import sgpostal as parser

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification

website = "gloriajeans.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    # Your scraper here
    with SgChrome() as driver:
        driver.get("https://www.gloriajeans.com/pages/store-locator")
        time.sleep(60)
        stores_sel = lxml.html.fromstring(driver.page_source)
        stores = stores_sel.xpath('//div[@class="item thumbnail"]')
        for store in stores:
            page_url = "".join(
                store.xpath(
                    './/div[@class="item-content"]/a[contains(@class,"linkdetailstore")]/@href'
                )
            ).strip()
            locator_domain = website
            location_name = "".join(
                store.xpath('.//div[@class="item-content"]/label/strong/text()')
            ).strip()
            if location_name == "":
                location_name = "<MISSING>"

            address = "".join(
                store.xpath(
                    'div/div[@class="item-content"]/div[@class="address"]//text()'
                )
            ).strip()
            formatted_addr = parser.parse_address_usa(address)
            street_address = formatted_addr.street_address_1
            if formatted_addr.street_address_2:
                street_address = street_address + ", " + formatted_addr.street_address_2

            city = formatted_addr.city
            if city:
                city = city.split(",")[0].strip()
            state = address.split(",")[-3].strip()
            zip = address.split(",")[-2].strip()

            country_code = ""
            if "USA" in address or "United States" in address:
                country_code = "US"

            if city:
                street_address = address.title().split(f"{city},")[0].strip()

            if city == state:
                if "Center" in street_address:
                    city = street_address.split("Center")[1].strip(", ").strip()
                    street_address = street_address.split(f"{city},")[0].strip()
                else:
                    city = street_address.split(" ")[-1].strip(", ").strip()
                    street_address = street_address.split(f"{city},")[0].strip()
            street_address = street_address.strip(",")

            phone = "".join(
                store.xpath(
                    'div/div[@class="item-content"]//a[contains(@class,"phone-no")]/text()'
                )
            ).strip()

            location_type = "<MISSING>"

            if country_code == "":
                if us.states.lookup(state):
                    country_code = "US"

            store_number = "<MISSING>"

            hours_of_operation = "<MISSING>"
            latitude = "<MISSING>"
            longitude = "<MISSING>"

            if len(page_url) > 0:
                page_url = "https://www.gloriajeans.com" + page_url
                if (
                    page_url
                    == "https://www.gloriajeans.com/apps/store-locator/chicago-ridge-mall.html"
                ):
                    state = "Illinois"
                log.info(page_url)
                store_req = session.get(page_url, headers=headers)
                store_sel = lxml.html.fromstring(store_req.text)
                latitude = store_req.text.split("lat:")[1].strip().split(",")[0].strip()
                longitude = (
                    store_req.text.split("lng:")[1].strip().split("}")[0].strip()
                )

                hours = store_sel.xpath('//table[@class="work-time table"]/tr')
                hours_list = []
                for hour in hours:
                    day = "".join(hour.xpath('th[@class="dayname"]/text()')).strip()
                    timee = "".join(hour.xpath("td/text()")).strip()
                    hours_list.append(day + ":" + timee)

                hours_of_operation = "; ".join(hours_list).strip()

            else:
                page_url = "<MISSING>"

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
        deduper=SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.STREET_ADDRESS,
                }
            )
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()

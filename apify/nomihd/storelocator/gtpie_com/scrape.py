# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
import lxml.html
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter

website = "gtpie.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    # Your scraper here

    search_url = "https://gtpie.com/locations/"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)

    stores = stores_sel.xpath('//div[@class="col-md-4 location-item"]')
    for store in stores:
        page_url = "".join(store.xpath("div/h4/a/@href")).strip()
        location_type = "<MISSING>"
        locator_domain = website
        location_name = "".join(store.xpath("div/h4/a/text()")).strip()

        raw_info = store.xpath("div/text()")
        add_list = []
        for add in raw_info:
            if len("".join(add).strip()) > 0 and "|" not in "".join(add).strip():
                add_list.append("".join(add).strip())

        street_address = ", ".join(add_list[:-1])
        city_state_zip = add_list[-1].strip()
        city = city_state_zip.split(",")[0].strip()
        state = city_state_zip.split(",")[1].strip().split(" ")[0].strip()
        zip = city_state_zip.split(",")[1].strip().split(" ")[1].strip()
        country_code = "US"

        phone = "".join(
            store.xpath(
                './/li[@class="contact-field field_phone"]/span[@class="contact-field-data"]//text()'
            )
        ).strip()

        hours_list = []
        days = []
        time = []
        all_span = store.xpath(
            './/li[@class="contact-field field_hours"]/span[@class="contact-field-data"]/span'
        )
        for temp in all_span:
            if "day-col" == "".join(temp.xpath("@class")).strip():
                days.append("".join(temp.xpath("text()")).strip())
            else:
                time.append("".join(temp.xpath("text()")).strip())

        for index in range(0, len(days)):
            hours_list.append(days[index].strip() + time[index].strip())

        hours_of_operation = (
            "; ".join(hours_list)
            .strip()
            .encode("ascii", "replace")
            .decode("utf-8")
            .replace("?", "-")
            .strip()
        )
        store_number = (
            "".join(store.xpath("@id")).strip().replace("location-item-", "").strip()
        )

        latitude = "".join(store.xpath("@data-lat"))
        longitude = "".join(store.xpath("@data-long"))

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

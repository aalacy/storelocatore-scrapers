# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
import lxml.html
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json

website = "northmart.ca"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    # Your scraper here

    search_url = "https://www.northmart.ca/our-stores/locator"
    stores_req = session.get(search_url, headers=headers)
    stores = json.loads(
        stores_req.text.split("var locations = ")[1].strip().split("}];")[0].strip()
        + "}]"
    )
    stores_sel = lxml.html.fromstring(stores_req.text)
    stores_html = stores_sel.xpath(
        '//div[@class="locations"]/div[contains(@class,"location")]'
    )

    done_locations = []
    for store in stores:
        page_url = search_url
        location_type = "<MISSING>"
        locator_domain = website
        store_sel = lxml.html.fromstring(store["details"])
        location_name = "".join(store_sel.xpath("//h4/span/text()")).strip()

        address = store_sel.xpath('//p[@class="address"]/strong/text()')
        add_list = []
        for add in address:
            if len("".join(add).strip()) > 0:
                add_list.append("".join(add).strip())

        street_address = ", ".join(add_list[:-2]).strip()
        city_state = add_list[-2].strip()
        city = (
            city_state.split(",")[0]
            .strip()
            .replace("- Quickstop", "")
            .strip()
            .replace("(Burger King)", "")
            .strip()
        )
        state = city_state.split(",")[-1].strip()
        zip = add_list[-1].strip()
        country_code = "CA"
        phone = ""
        raw_text = store_sel.xpath('p[@class="address"]/text()')
        for temp in raw_text:
            if "phone" in "".join(temp).strip().lower():
                phone = "".join(temp).strip().lower().replace("phone:", "").strip()
                if " " in phone:
                    phone = phone.split(" ")[0].strip()

        hours_of_operation = "<MISSING>"
        store_number = store["pid"]
        done_locations.append(store_number)
        latitude = store["lat"]
        longitude = store["lng"]

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

    for store in stores_html:
        store_number = "".join(store.xpath("@data-id")).strip()
        if store_number not in done_locations:
            page_url = search_url
            location_type = "<MISSING>"
            locator_domain = website
            location_name = "".join(
                store.xpath('div[@class="location-contact"]/h4/span/text()')
            ).strip()

            address = store.xpath(
                'div[@class="location-contact"]/p[@class="address"]/strong/text()'
            )
            add_list = []
            for add in address:
                if len("".join(add).strip()) > 0:
                    add_list.append("".join(add).strip())

            street_address = ", ".join(add_list[:-2]).strip()
            city_state = add_list[-2].strip()
            city = (
                city_state.split(",")[0]
                .strip()
                .replace("- Quickstop", "")
                .strip()
                .replace("(Burger King)", "")
                .strip()
            )
            state = city_state.split(",")[-1].strip()
            zip = add_list[-1].strip()
            country_code = "CA"
            phone = ""
            raw_text = store.xpath(
                'div[@class="location-contact"]/p[@class="address"]/text()'
            )
            for temp in raw_text:
                if "phone" in "".join(temp).strip().lower():
                    phone = "".join(temp).strip().lower().replace("phone:", "").strip()
                    if " " in phone and "(" not in phone:
                        phone = phone.split(" ")[0].strip()

            hours_of_operation = "<MISSING>"
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

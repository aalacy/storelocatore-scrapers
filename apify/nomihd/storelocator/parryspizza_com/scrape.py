# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html

website = "parryspizza.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    # Your scraper here

    search_url = "https://parryspizza.com/locations/"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    stores = (
        stores_req.text.split("var locations_data = [")[1]
        .strip()
        .split("];")[0]
        .strip()
        .split("id:")
    )

    stores_list = stores_sel.xpath('//ul[@class="all-locations-list"]/li')
    store_dict = {}
    for stor in stores_list:
        ID = "".join(stor.xpath("@id")).strip().replace("loc-", "").strip()
        addr_dict = {}
        addr_dict["streetAddress"] = "".join(
            stor.xpath(
                'div[@property="address"]/span[@property="streetAddress"]/text()'
            )
        ).strip()
        addr_dict["addressLocality"] = "".join(
            stor.xpath(
                'div[@property="address"]/span[@property="addressLocality"]/text()'
            )
        ).strip()
        addr_dict["addressRegion"] = "".join(
            stor.xpath(
                'div[@property="address"]/span[@property="addressRegion"]/text()'
            )
        ).strip()
        addr_dict["postalCode"] = "".join(
            stor.xpath('div[@property="address"]/span[@property="postalCode"]/text()')
        ).strip()

        store_dict[ID] = addr_dict

    for index in range(1, len(stores)):
        store_data = stores[index]
        ID = store_data.split(",")[0].strip()
        page_url = (
            store_data.split("permalink:")[1]
            .strip()
            .split(",")[0]
            .strip()
            .replace("'", "")
            .strip()
        )
        location_type = "<MISSING>"
        location_name = (
            store_data.split("name:")[1]
            .strip()
            .split(",")[0]
            .strip()
            .replace("'", "")
            .strip()
            .replace("&#8211;", "-")
            .encode("ascii", "replace")
            .decode("utf-8")
            .replace("?", "-")
            .strip()
        )
        if "Coming Soon" in location_name:
            location_type = "Coming Soon"

        locator_domain = website

        address = store_dict[ID]
        street_address = address["streetAddress"]
        city = address["addressLocality"]
        state = address["addressRegion"]
        zip = address["postalCode"]
        country_code = "US"

        phone = (
            store_data.split("phone_number:")[1]
            .strip()
            .split(",")[0]
            .strip()
            .replace("'", "")
            .strip()
        )

        hours_of_operation = (
            store_data.split("hours:")[1]
            .strip()
            .split(",")[0]
            .strip()
            .replace("'", "")
            .strip()
            .replace("&ndash;", "-")
            .strip()
            .replace("<br>", ";")
            .strip()
            .encode("ascii", "replace")
            .decode("utf-8")
            .replace("?", "-")
            .strip()
        )

        store_number = "<MISSING>"

        latitude = store_data.split("lat:")[1].strip().split(",")[0].strip()
        longitude = store_data.split("lng:")[1].strip().split("}")[0].strip()

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

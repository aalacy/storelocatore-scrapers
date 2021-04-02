# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape import sgpostal as parser
import json

website = "tradefairny.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "sec-ch-ua": '"Google Chrome";v="89", "Chromium";v="89", ";Not A Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36",
    "Referer": "https://tradefairny.com/",
}


def fetch_data():
    # Your scraper here
    search_url = "http://tradefairny.com/store-locations"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    stores = stores_sel.xpath('//section[@data-aid="CONTACT_INFO_CONTAINER_REND"]')

    coord_list = stores_req.text.split('JSON.parse("{\\"lat\\"')

    for index in range(0, len(stores)):
        page_url = search_url
        locator_domain = website
        location_name = "".join(
            stores[index].xpath('.//*[@data-aid="CONTACT_INFO_BIZ_NAME_REND"]/text()')
        ).strip()

        raw_address = "".join(
            stores[index].xpath('.//p[@data-aid="CONTACT_INFO_ADDRESS_REND"]/text()')
        ).strip()

        formatted_addr = parser.parse_address_usa(raw_address)
        street_address = formatted_addr.street_address_1
        if formatted_addr.street_address_2:
            street_address = street_address + ", " + formatted_addr.street_address_2

        city = formatted_addr.city
        if city == "Lic":
            street_address = street_address + " " + city
            city = "<MISSING>"

        state = formatted_addr.state
        zip = formatted_addr.postcode
        country_code = "US"

        phone = "".join(
            stores[index].xpath('.//a[@data-aid="CONTACT_INFO_PHONE_REND"][1]/text()')
        ).strip()
        hours_of_operation = "OPEN 24/7"

        store_number = "<MISSING>"
        if "#" in location_name:
            store_number = location_name.split("#")[1].strip()

        location_type = "<MISSING>"

        json_text = '{"lat"' + coord_list[index + 1].split('"),JSON.parse')[
            0
        ].strip().replace('\\"', '"')
        coord_json = json.loads(json_text)
        latitude = coord_json["lat"]
        longitude = coord_json["lon"]

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
            raw_address=raw_address,
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

# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json
import lxml.html
from sgpostal import sgpostal as parser


website = "restaurantlabelleprovince.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "accept": "application/json, text/plain, */*",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36",
}


def fetch_data():
    # Your scraper here
    search_url = "https://restaurantlabelleprovince.com/succursales/"
    search_res = session.get(search_url, headers=headers)
    search_sel = lxml.html.fromstring(search_res.text)
    json_text = (
        "".join(search_sel.xpath("//div/@data-points"))
        .strip()
        .replace("&quot;", '"')
        .strip()
    )
    restaurants_list = json.loads(json_text)

    for restaurant in restaurants_list:

        page_url = search_url
        locator_domain = website
        location_name = restaurant["title"]
        log.info(location_name)
        raw_address = search_sel.xpath(
            f'//td/strong[text()="{location_name}"]/parent::node()/text()'
        )

        phone = "<MISSING>"
        if len(raw_address) <= 0:
            if "(Henri-Bourassa)" in location_name:
                location_name = location_name.split("(")[0].strip()

            if "St-Basile" == location_name:
                location_name = "St-Basile Le Grand"

            if "Saint-Eustache" == location_name:
                location_name = "St-Eustache"

            raw_address = search_sel.xpath(
                f'//td/strong[text()="{location_name}"]/parent::node()/text()'
            )

        if len(raw_address) <= 0:
            log.info(location_name)
            continue

        if (
            raw_address[-1]
            .strip()
            .replace("(", "")
            .replace(")", "")
            .replace("-", "")
            .strip()
            .replace(" ", "")
            .strip()
            .encode("ascii", "replace")
            .decode("utf-8")
            .replace("?", "")
            .strip()
            .isdigit()  # checking if it's phonenumber or zip
        ):
            raw_address = ", ".join(raw_address[:-1]).strip().replace(",,", ",").strip()

            phone = search_sel.xpath(
                f'//td/strong[text()="{location_name}"]/parent::node()/text()'
            )

            if phone:
                phone = phone[-1].strip()
        else:
            raw_address = (
                ", ".join(raw_address)
                .strip()
                .replace(",,", ",")
                .strip()
                .replace(", ,", ",")
                .strip()
            )

        if raw_address[0] == ",":
            raw_address = "".join(raw_address[1:]).strip()

        formatted_addr = parser.parse_address_intl(raw_address)
        street_address = formatted_addr.street_address_1
        if formatted_addr.street_address_2:
            street_address = street_address + ", " + formatted_addr.street_address_2

        city = formatted_addr.city
        if city is None:
            city = location_name
        state = formatted_addr.state
        zip = raw_address.split(",")[-1].strip()
        if len(zip) != 7:
            zip = formatted_addr.postcode

        street_address = street_address.replace(zip, "").strip()
        street_address = street_address.replace(zip.split(" ")[0], "").strip()

        country_code = "CA"

        store_number = "<MISSING>"

        location_type = "<MISSING>"

        hours_of_operation = "<MISSING>"

        latitude = restaurant["coordinates"]["latitude"]
        longitude = restaurant["coordinates"]["longitude"]

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

    # hardcoding missing location
    location_name = "Saint-Michel"
    raw_address = ", ".join(
        search_sel.xpath(f'//td/strong[text()="{location_name}"]/parent::node()/text()')
    ).strip()

    formatted_addr = parser.parse_address_intl(raw_address)
    street_address = formatted_addr.street_address_1
    if formatted_addr.street_address_2:
        street_address = street_address + ", " + formatted_addr.street_address_2

    city = formatted_addr.city
    if city is None:
        city = location_name
    state = formatted_addr.state
    zip = raw_address.split(",")[-1].strip()
    if len(zip) != 7:
        zip = formatted_addr.postcode

    street_address = street_address.replace(zip, "").strip()
    street_address = street_address.replace(zip.split(" ")[0], "").strip()

    yield SgRecord(
        locator_domain=website,
        page_url=search_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        state=state,
        zip_postal=zip,
        country_code="CA",
        store_number="<MISSING>",
        phone="<MISSING>",
        location_type="<MISSING>",
        latitude="<MISSING>",
        longitude="<MISSING>",
        hours_of_operation="<MISSING>",
        raw_address=raw_address,
    )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()

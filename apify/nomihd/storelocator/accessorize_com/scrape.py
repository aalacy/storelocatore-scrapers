# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json
from sgpostal import sgpostal as parser

website = "accessorize.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "authority": "www.accessorize.com",
    "cache-control": "max-age=0",
    "sec-ch-ua": '"Chromium";v="88", "Google Chrome";v="88", ";Not A Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.104 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "none",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here

    session.get("https://www.accessorize.com/")
    search_url = "https://www.accessorize.com/us/stores?country=GB"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    stores = stores_sel.xpath(
        '//div[@data-component="stores/storeDetails"]/@data-component-store'
    )
    for store in stores:
        store_data = json.loads(
            store.replace("&quot;", '"')
            .replace("&lt;", "<")
            .replace("&gt;", ">")
            .strip()
        )

        locator_domain = website
        latitude = store_data["latitude"]
        longitude = store_data["longitude"]
        store_number = store_data["ID"]
        location_name = store_data["name"]
        location_type = "<MISSING>"
        street_address = store_data["address1"]
        city = store_data["city"]
        if city is not None:
            city = city.strip()
        state = "<MISSING>"
        if "stateCode" in store_data:
            state = store_data["stateCode"].strip()
        zip = store_data["postalCode"]
        country_code = store_data["countryCode"]
        phone = store_data["phoneFormatted"]
        page_url = "<MISSING>"

        hours_sel = lxml.html.fromstring(store_data["workingHours"])
        hours = hours_sel.xpath(".//text()")
        hours_list = []
        for hour in hours:
            if len("".join(hour).strip()) > 0:
                if "Opening hours:" not in hour:
                    hours_list.append("".join(hour).strip())

        hours_of_operation = "; ".join(hours_list).strip()
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

    """ US Stores """
    search_url = "https://www.accessorize.com/us/stores"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    stores = (
        stores_sel.xpath('//table[@class="table b-stores-disabled__table"]')[-1]
        .xpath("tbody")[-1]
        .xpath("tr")
    )
    for store in stores:
        page_url = search_url
        locator_domain = website
        location_name = "".join(store.xpath("td[2]/text()")).strip()
        address = "".join(store.xpath("td[3]/text()")).strip()
        street_address = ", ".join(address.split(",")[:-3]).strip()
        city = address.split(",")[-3]
        state = address.split(",")[-2].strip().split(" ")[0].strip()
        zip = address.split(",")[-2].strip().split(" ")[-1].strip()
        country_code = "US"
        location_type = "<MISSING>"
        store_number = "<MISSING>"
        hours_of_operation = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        phone = "<MISSING>"
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

    """ INTERNATIONAL Stores """
    search_url = "https://www.accessorize.com/us/stores"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    sections = stores_sel.xpath('//table[@class="table b-stores-disabled__table"]')[
        -1
    ].xpath("tbody")[:-1]
    countries = stores_sel.xpath('//table[@class="table b-stores-disabled__table"]')[
        -1
    ].xpath("thead")[:-1]

    for index in range(0, len(countries)):
        stores = sections[index].xpath("tr")
        for store in stores:
            page_url = search_url
            locator_domain = website
            location_name = "".join(store.xpath("td[2]/text()")).strip()
            raw_address = (
                "".join(store.xpath("td[3]/text()")).strip().replace("\n", ", ").strip()
            )
            formatted_addr = parser.parse_address_intl(raw_address)
            street_address = formatted_addr.street_address_1
            if street_address:
                if formatted_addr.street_address_2:
                    street_address = (
                        street_address + ", " + formatted_addr.street_address_2
                    )
            else:
                if formatted_addr.street_address_2:
                    street_address = formatted_addr.street_address_2

            city = formatted_addr.city
            state = formatted_addr.state
            zip = formatted_addr.postcode

            country_code = "".join(countries[index].xpath(".//th/text()")).strip()

            if not zip and country_code == "India":
                try:
                    zip = raw_address.split(",")[-1].strip().split("-")[-1].strip()
                    if not zip.isdigit() and len(zip) != 6:
                        zip = "<MISSING>"
                except:
                    pass

            if not city and country_code == "India":
                try:
                    city = raw_address.split(",")[-1].strip().split("-")[0].strip()
                except:
                    pass

            if not city:
                if "Str. " in street_address:
                    city = street_address.split("Str. ")[1].strip()
                    if "&" in city or "road" in city.lower():
                        city = "<MISSING>"
                    else:
                        street_address = street_address.split("Str. ")[0].strip()

            location_type = "<MISSING>"
            store_number = "<MISSING>"
            hours_of_operation = "<MISSING>"
            latitude = "<MISSING>"
            longitude = "<MISSING>"
            phone = "<MISSING>"
            if street_address:
                street_address = street_address.replace(", First Floor The", "").strip()

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
    with SgWriter(
        deduper=SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.LOCATION_NAME,
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.CITY,
                    SgRecord.Headers.STATE,
                    SgRecord.Headers.ZIP,
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

# -*- coding: utf-8 -*-
from sgrequests import SgRequests, SgRequestError
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgpostal import sgpostal as parser
import json
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


website = "milanopizzeria.ca"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "authority": "order.milanopizzeria.ca",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="90", "Google Chrome";v="90"',
    "sec-ch-ua-mobile": "?0",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "none",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "accept-language": "en-US,en;q=0.9,ar;q=0.8",
}


def fetch_data():
    # Your scraper here
    search_url = "https://order.milanopizzeria.ca/index.php/search/all"
    search_res = session.get(search_url, headers=headers)

    search_sel = lxml.html.fromstring(search_res.text)

    store_list = list(search_sel.xpath('//div[contains(@class,"restaurant")]'))

    for store in store_list:

        page_url = search_url
        locator_domain = website
        location_name = "".join(store.xpath(".//h3/text()"))

        full_address = list(
            filter(
                str,
                [x.strip() for x in store.xpath(".//p//text()")],
            )
        )

        store_url = "".join(
            store.xpath(
                './/a[not(contains(@href,"menu")) and not(contains(@href,"order."))]/@href'
            )
        )

        raw_address = "<MISSING>"
        hours_of_operation = "<MISSING>"

        if len(full_address) == 2:  # if phone number present
            raw_address = full_address[0]
            formatted_addr = parser.parse_address_intl(raw_address)
            street_address = formatted_addr.street_address_1
            if formatted_addr.street_address_2:
                street_address = street_address + ", " + formatted_addr.street_address_2

            city = formatted_addr.city
            state = formatted_addr.state
            zip = formatted_addr.postcode

            if zip:
                street_address = full_address[0].split(",")[0].strip()

            phone = full_address[1]
            store_number = "<MISSING>"
            latitude, longitude = "<MISSING>", "<MISSING>"

        else:
            street_address, city, state, zip, country_code = (
                "<MISSING>",
                "<MISSING>",
                "<MISSING>",
                "<MISSING>",
                "<MISSING>",
            )
            phone = "<MISSING>"
            store_number = "<MISSING>"
            latitude, longitude = "<MISSING>", "<MISSING>"

        if store_url:
            store_url = (
                store_url.strip().replace("smithfalls.", "smithsfalls.") + "/?p=contact"
            )
            page_url = store_url

            log.info(store_url)

            store_res = session.get(store_url.strip(), headers=headers)
            if isinstance(store_res, SgRequestError):
                continue
            store_sel = lxml.html.fromstring(store_res.text)
            if "var locations =" in store_res.text:
                store_json_str = (
                    store_res.text.split("var locations =")[1]
                    .split("}];")[0]
                    .strip()
                    .strip("[ ")
                    .strip()
                    + "}"
                )
                store_json = json.loads(store_json_str)

                street_address = store_json["address"]
                city = store_json["city"]
                state = store_json["province"].upper()
                zip = store_json["zip"]
                store_number = store_json["id"]
                phone = store_json["phone"].split(";")[0].strip()
                latitude, longitude = store_json["latitude"], store_json["longitude"]

                hours = store_sel.xpath('//li[contains(@id,"li_open_")]')
                hours_list = []
                for hour in hours:
                    day = (
                        "".join(hour.xpath("@id"))
                        .strip()
                        .replace("li_open_", "")
                        .strip()
                    )
                    time = "".join(hour.xpath('.//li/span[@class="st"]/text()')).strip()
                    hours_list.append(day + ":" + time)

                hours_of_operation = "; ".join(hours_list).strip()
        country_code = "CA"

        location_type = "<MISSING>"

        if street_address != "<MISSING>":
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
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PageUrlId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()

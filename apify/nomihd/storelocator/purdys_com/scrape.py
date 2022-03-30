# -*- coding: utf-8 -*-
from sgrequests import SgRequests, SgRequestError
from sglogging import sglog
import lxml.html
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json
from sgpostal import sgpostal as parser

website = "purdys.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "authority": "www.purdys.com",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="99", "Google Chrome";v="99"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.84 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "referer": "https://www.purdys.com/",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here

    stores_req = session.get("https://www.purdys.com/shops", headers=headers)
    jsonLocations = json.loads(
        stores_req.text.split("jsonLocations: ")[1]
        .strip()
        .split("imageLocations")[0]
        .strip()[:-1]
    )
    stores = jsonLocations["items"]
    for index, store in enumerate(stores):
        latitude = store["lat"]
        longitude = store["lng"]
        location_type = "<MISSING>"
        locator_domain = website
        store_number = "<MISSING>"

        popup_sel = lxml.html.fromstring(store["popup_html"])
        page_url = "".join(
            popup_sel.xpath("//a[@class='amlocator-link']/@href")
        ).strip()
        log.info(page_url)
        store_req = session.get(page_url, headers=headers)
        if isinstance(store_req, SgRequestError):
            page_url = "https://www.purdys.com/shops"
            location_name = "".join(
                popup_sel.xpath('//div[@class="amlocator-title"]//text()')
            ).strip()

            add_list = list(
                filter(
                    str,
                    [
                        x.strip()
                        for x in popup_sel.xpath(
                            "//div[@class='amlocator-info-popup']/text()"
                        )
                    ],
                )
            )

            street_address = ""
            city = ""
            state = ""
            zip = ""

            for add in add_list:
                if "City" in add:
                    city = add.replace("City:", "").strip()
                if "Postal Code:" in add:
                    zip = add.replace("Postal Code:", "").strip()
                if "Address" in add:
                    street_address = add.replace("Address:", "").strip()
                if "State" in add:
                    state = add.replace("State:", "").strip()

            raw_address = ""
            if street_address:
                raw_address = street_address
            if city:
                raw_address = raw_address + ", " + city
            if state:
                raw_address = raw_address + ", " + state
            if zip:
                raw_address = raw_address + ", " + zip

            country_code = "CA"

            phone = "<MISSING>"

            hours_of_operation = "<MISSING>"
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
            break
        else:
            store_sel = lxml.html.fromstring(store_req.text)
            location_name = "".join(
                store_sel.xpath("//h1[@class='page-title']//text()")
            ).strip()

            raw_address = "".join(
                store_sel.xpath("//span[@class='amlocator-text -address']/text()")
            ).strip()
            formatted_addr = parser.parse_address_intl(raw_address)
            street_address = formatted_addr.street_address_1
            if formatted_addr.street_address_2:
                street_address = street_address + ", " + formatted_addr.street_address_2

            city = formatted_addr.city
            state = formatted_addr.state
            zip = formatted_addr.postcode

            country_code = "CA"

            phone = "".join(
                store_sel.xpath('//div[./i[@class="fa fa-phone-square"]]//text()')
            ).strip()

            hours_list = []
            hours = store_sel.xpath('//div[@class="amlocator-schedule-table"]/div')
            for hour in hours:
                day = "".join(hour.xpath("span[1]/text()")).strip()
                time = "".join(hour.xpath("span[2]/text()")).strip()
                hours_list.append(day + ":" + time)

            hours_of_operation = "; ".join(hours_list).strip()
            if hours_of_operation:
                if hours_of_operation.count("Gesloten") == 7:
                    continue

            if len(hours_list) <= 0:
                hours_of_operation = "".join(popup_sel.xpath(".//text()")).strip()
                if "Hours of Operation" in hours_of_operation:
                    hours_of_operation = hours_of_operation.split("Hours of Operation")[
                        1
                    ].strip()
                else:
                    hours_of_operation = "<MISSING>"

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

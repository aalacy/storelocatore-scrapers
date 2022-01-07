# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal import sgpostal as parser

website = "hihostels.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "authority": "groups.hihostels.com",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
    "accept": "*/*",
    "x-requested-with": "XMLHttpRequest",
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here
    with SgRequests() as session:
        page_no = 1
        while True:

            params = (
                ("s", "namelowtohi"),
                ("page", str(page_no)),
            )
            stores_req = session.get(
                "https://groups.hihostels.com/search/hostels/load-more/grid",
                headers=headers,
                params=params,
            )
            store_json = stores_req.json()
            stores_sel = lxml.html.fromstring(store_json["content"])
            stores = stores_sel.xpath(
                '//p[@class="mobile-title hostel_search_title_not_eco"]/a/@href'
            )
            for store_url in stores:
                page_url = "https://groups.hihostels.com" + store_url
                log.info(page_url)
                store_req = session.get(page_url, headers=headers)
                store_sel = lxml.html.fromstring(store_req.text)
                locator_domain = website

                store_number = "<MISSING>"

                location_type = "<MISSING>"
                location_name = "".join(
                    store_sel.xpath('//h1[contains(@class,"hostel-header")]//text()')
                ).strip()

                temp_address = store_sel.xpath('//p[@class="full-address"]/text()')

                add_list = []
                for temp in temp_address:
                    if (
                        len(
                            "".join(temp)
                            .strip()
                            .replace("\r\n", "")
                            .strip()
                            .replace("\n", "")
                            .strip()
                        )
                        > 0
                    ):
                        add_list.append(
                            "".join(temp)
                            .strip()
                            .replace("\r\n", "")
                            .strip()
                            .replace("\n", "")
                            .strip()
                        )

                full_address = ", ".join(add_list).strip().split(",")
                full_add_list = []
                for add in full_address:
                    if len("".join(add).strip()) > 0:
                        full_add_list.append("".join(add).strip())

                raw_address = ", ".join(full_add_list).strip()
                formatted_addr = parser.parse_address_intl(raw_address)
                street_address = formatted_addr.street_address_1
                if formatted_addr.street_address_2:
                    street_address = (
                        street_address + ", " + formatted_addr.street_address_2
                    )

                city = formatted_addr.city
                state = formatted_addr.state
                zip = formatted_addr.postcode
                country_code = formatted_addr.country

                phone = "".join(
                    store_sel.xpath(
                        '//div[@class="acc-inner"]/p[./span[text()="Tel."]]/text()'
                    )
                ).strip()

                hours = store_sel.xpath(
                    '//div[@id="opening-times-section"]//div[@class="acc-inner"]/p/span/text()'
                )
                if len(hours) > 0:
                    hours_of_operation = (
                        hours[-1].strip().replace("Check-in:", "").strip()
                    )
                else:
                    hours_of_operation = "<MISSING>"

                latitude, longitude = (
                    "".join(store_sel.xpath('//input[@id="lat"]/@value')).strip(),
                    "".join(store_sel.xpath('//input[@id="lon"]/@value')).strip(),
                )

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
            if store_json["loadMore"] is True:
                page_no = page_no + 1
                log.info(page_no)
            else:
                break


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

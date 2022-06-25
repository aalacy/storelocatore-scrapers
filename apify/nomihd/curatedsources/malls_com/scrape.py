# -*- coding: utf-8 -*-
from sgrequests import SgRequests, SgRequestError
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal import sgpostal as parser
import json

website = "malls.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "authority": "www.malls.com",
    "content-length": "0",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
    "accept": "application/json, text/javascript, */*; q=0.01",
    "x-requested-with": "XMLHttpRequest",
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
    "sec-ch-ua-platform": '"Windows"',
    "origin": "https://www.malls.com",
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "referer": "https://www.malls.com/malls/",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here

    search_url = "https://www.malls.com/ajax/GetMaps.php"

    with SgRequests() as session:
        search_res = session.post(search_url, headers=headers)

        stores = json.loads(search_res.text)["active"]

        for store in stores:
            locator_domain = website
            store_sel = lxml.html.fromstring(store["text"])
            page_url = (
                "https://www.malls.com"
                + "".join(store_sel.xpath('//div[@class="r"]/a/@href')).strip()
            )
            log.info(page_url)
            store_req = session.get(page_url, headers=headers)

            city = ""
            phone = "<MISSING>"
            if not isinstance(store_req, SgRequestError):
                page_sel = lxml.html.fromstring(store_req.text)
                city = "".join(
                    page_sel.xpath('//b[contains(text(),"ADDRESS IN")]/a[2]/text()')
                ).strip()
                phone = "".join(
                    page_sel.xpath(
                        '//div[@class="info"][./div[text()="PHONE:"]]/strong/text()'
                    )
                ).strip()

            location_name = "".join(
                store_sel.xpath('//div[@class="r"]/a/text()')
            ).strip()
            location_type = "<MISSING>"

            raw_address = "".join(store_sel.xpath('.//div[@class="ad"]/text()')).strip()

            formatted_addr = parser.parse_address_intl(raw_address)
            street_address = formatted_addr.street_address_1
            if formatted_addr.street_address_2:
                street_address = street_address + ", " + formatted_addr.street_address_2

            if len(city) <= 0:
                city = formatted_addr.city

            state = formatted_addr.state
            zip = formatted_addr.postcode
            country_code = page_url.split("malls.com/")[1].strip().split("/")[0].strip()

            hours_of_operation = "<MISSING>"

            store_number = "<MISSING>"
            latitude, longitude = store["x"], store["y"]

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

# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import lxml.html

website = "quicknclean.net"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "authority": "quicknclean.net",
    "sec-ch-ua": '"Chromium";v="94", "Google Chrome";v="94", ";Not A Brand";v="99"',
    "accept": "*/*",
    "x-requested-with": "XMLHttpRequest",
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "referer": "https://quicknclean.net/all-locations/",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here
    with SgRequests(dont_retry_status_codes=([404])) as session:
        stores_req = session.get(
            "https://quicknclean.net/wp-json/wpgmza/v1/markers/base64eJyrVkrLzClJLVKyUqqOUcpNLIjPTIlRsopRMopR0gEJFGeUgsSKgYLRsbVKtQCWBhBO",
            headers=headers,
        )
        stores = json.loads(stores_req.text)

        stores_html_req = session.get(
            "https://quicknclean.net/all-locations/", headers=headers
        )

        stores_html_sel = lxml.html.fromstring(stores_html_req.text)

        url_dict = {}
        stores_section = stores_html_sel.xpath(
            '//div[@class="wpgmza-grid-item-content"]'
        )
        for sec in stores_section:
            url_dict[
                "".join(sec.xpath('.//p[@class="address-label"]/text()'))
                .strip()
                .replace(", USA", "")
                .strip()
            ] = "".join(
                sec.xpath('.//a[./span[contains(text(),"Learn More")]]/@href')
            ).strip()

        for store in stores:

            page_url = "<MISSING>"
            locator_domain = website

            raw_address = store["address"].replace(", USA", "").strip().split(",")
            if ",".join(raw_address) in url_dict:
                page_url = url_dict[",".join(raw_address)]

            street_address = ", ".join(raw_address[:-2]).strip()
            city = raw_address[-2].strip()
            state = raw_address[-1].strip().split(" ")[0].strip()
            zip = raw_address[-1].strip().split(" ")[-1].strip()
            if zip.isalpha():
                zip = "<MISSING>"

            country_code = "US"

            location_name = f"{city}, {state}"

            store_number = store["id"]

            location_type = "<MISSING>"
            desc = store["description"]
            phone = ""
            try:
                phone = (
                    desc.split("Phone:")[1]
                    .strip()
                    .split(">")[1]
                    .strip()
                    .split("</strong")[0]
                    .strip()
                )
            except:
                pass

            hours_of_operation = ""
            try:
                hours_of_operation = (
                    desc.split("<p>Hours")[1]
                    .strip()
                    .split(">")[1]
                    .strip()
                    .split("</strong")[0]
                    .strip()
                )
            except:
                pass

            latitude, longitude = (
                store["lat"],
                store["lng"],
            )
            raw_address = "<MISSING>"

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
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.StoreNumberId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()

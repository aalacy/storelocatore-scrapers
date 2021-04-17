# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
import json
from sgscrape import sgpostal as parser


website = "rebath.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "authority": "www.rebath.com",
    "sec-ch-ua": '"Google Chrome";v="89", "Chromium";v="89", ";Not A Brand";v="99"',
    "accept": "text/html, */*; q=0.01",
    "x-requested-with": "XMLHttpRequest",
    "sec-ch-ua-mobile": "?0",
    "x-wp-nonce": "6de23de848",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36",
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    "origin": "https://www.rebath.com",
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "referer": "https://www.rebath.com/rebath-locations/",
    "accept-language": "en-US,en;q=0.9,ar;q=0.8",
}

data = {"filter": "", "page": "1", "ppp": "9999"}


def fetch_data():
    # Your scraper here

    api_url = "https://www.rebath.com/wp-json/locations/v1/locations_list"
    api_res = session.post(api_url, headers=headers, data=data)
    json_res = json.loads(api_res.text)

    locations_hxml_str = json_res["location_data"]["locations_html"]

    search_sel = lxml.html.fromstring(locations_hxml_str)

    stores_list = search_sel.xpath('//div[@class="post-list"]//article')

    for store in stores_list:

        page_url = "https:" + "".join(store.xpath(".//h4/a/@href")).strip()
        locator_domain = website

        location_name = "".join(store.xpath("./@data-title")).strip()

        raw_address = (
            "".join(store.xpath("./@data-address"))
            .replace("<br/>", " ")
            .replace("<br />", " ")
            .strip()
        )
        formatted_addr = parser.parse_address_intl(raw_address)
        street_address = formatted_addr.street_address_1
        if formatted_addr.street_address_2:
            street_address = street_address + ", " + formatted_addr.street_address_2

        city = location_name.split(" ")[-1].strip()
        state = location_name.split(" ")[0].replace("(", "").replace(")", "").strip()
        zip = formatted_addr.postcode

        country = "US"
        country_code = country

        store_number = "<MISSING>"

        phone = "".join(store.xpath("./@data-phone")).strip()

        location_type = "<MISSING>"

        hours_of_operation = "<MISSING>"

        latitude = "".join(store.xpath("./@data-lat")).strip()
        longitude = "".join(store.xpath("./@data-long")).strip()

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

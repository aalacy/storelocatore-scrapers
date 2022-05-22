# -*- coding: utf-8 -*-
from sgrequests import SgRequests, SgRequestError
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import us

website = "dsdistribution.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "authority": "www.dsdistribution.com",
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


def split_fulladdress(address_info):
    street_address = " ".join(address_info[0:-1]).strip(" ,.")

    city_state_zip = (
        address_info[-1].replace(",", " ").replace(".", " ").replace("  ", " ").strip()
    )

    city = " ".join(city_state_zip.split(" ")[:-2]).strip()
    state = city_state_zip.split(" ")[-2].strip()
    zip = city_state_zip.split(" ")[-1].strip()

    if not city or us.states.lookup(zip):
        city = city + " " + state
        state = zip
        zip = "<MISSING>"

    if city and state:
        if not us.states.lookup(state):
            city = city + " " + state
            state = "<MISSING>"

    country_code = "US"
    return street_address, city, state, zip, country_code


def fetch_data():
    # Your scraper here
    api_url = "https://www.dsdistribution.com/wp-json/wpgmza/v1/marker-listing/base64eJyrVirIKHDOSSwuVrJSCg9w941yjInxTSzKTi3yySwuycxLj4lxSizOTAbxlHSUiksSi0qUrAx0lHJS89JLMpSsdA11lHITC+IzU4AmGCrVAgCU-BsU"
    api_res = session.get(api_url, headers=headers)

    json_res = json.loads(api_res.text)

    stores_list = json_res["meta"]

    for store in stores_list:

        page_url = store["link"]
        store_number = store["id"]
        location_type = "<MISSING>"
        hours_of_operation = "<MISSING>"
        latitude = store["lat"]
        longitude = store["lng"]
        locator_domain = website
        phone = "<MISSING>"

        log.info(page_url)
        store_res = session.get(page_url, headers=headers)
        if not isinstance(store_res, SgRequestError):
            store_sel = lxml.html.fromstring(store_res.text)
            location_name = "".join(store_sel.xpath("//title/text()")).strip()
            full_address = list(
                filter(
                    str,
                    [
                        x.strip()
                        for x in store_sel.xpath(
                            '//div[@class="col"]//*[self::h2 or self::h3]/text()'
                        )
                    ],
                )
            )
            street_address, city, state, zip, country_code = split_fulladdress(
                full_address
            )

            phone = "".join(
                store_sel.xpath('//div[contains(@class,"col-last")]//h4/text()')
            ).strip()

        else:
            location_name = store["title"]  # title and address is same
            raw_address = location_name.split(",")
            street_address = raw_address[0].strip()
            city = raw_address[1].strip()
            state = raw_address[-1].strip().split(" ")[0].strip()
            zip = raw_address[-1].strip().split(" ")[-1].strip()
            country_code = "US"

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

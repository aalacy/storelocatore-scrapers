# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
import us
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json
from bs4 import BeautifulSoup as BS

website = "4wheelparts.com"
domain = "https://www.4wheelparts.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    # Your scraper here

    search_url = "https://www.4wheelparts.com/stores/find-a-store"
    with SgRequests(dont_retry_status_codes=([404])) as session:
        states_req = session.get(search_url, headers=headers)
        states_sel = lxml.html.fromstring(states_req.text)
        states = states_sel.xpath(
            '//div[@class="panel panel-default m-b10"]/div/a/@href'
        )
        for state_url in states:
            stores_req = session.get(domain + state_url, headers=headers)
            stores_sel = lxml.html.fromstring(stores_req.text)
            stores = stores_sel.xpath('//h4[@class="normal m0"]/a/@href')
            for store_url in stores:
                page_url = domain + store_url
                log.info(page_url)
                store_req = session.get(page_url, headers=headers)
                store_sel = lxml.html.fromstring(store_req.text)

                json_without_html = BS(
                    "".join(
                        store_sel.xpath('//script[@type="application/ld+json"]/text()')
                    ).strip(),
                    "html.parser",
                ).get_text()
                json_str = (
                    (
                        json_without_html.replace(': "\r\n', ': "')
                        .replace(': "\n', ': "')
                        .replace("\t\t\t\t\t\t", "")
                        .strip()
                        .split('"description":')[0]
                        .strip()
                        .strip()
                        + "}]"
                    )
                    .replace(",}]", "}]")
                    .strip()
                )
                store_json = json.loads(json_str)[0]

                locator_domain = website
                location_name = store_json["name"]

                street_address = store_json["address"]["streetAddress"]
                city = store_json["address"]["addressLocality"]
                state = store_json["address"]["addressRegion"]
                zip = store_json["address"]["postalCode"]

                country_code = "<MISSING>"
                if us.states.lookup(state):
                    country_code = "US"

                store_number = "<MISSING>"
                if "#" in location_name:
                    store_number = location_name.split("#")[1].strip()
                    location_name = location_name.split("#")[0].strip()

                phone = store_json["address"]["telephone"]
                location_type = "<MISSING>"
                hours_of_operation = (
                    store_json["openingHours"]
                    .strip()
                    .replace("(Local Time)", "")
                    .strip()
                    .replace("p.m.", "p.m;")
                    .replace("Closed", "Closed; ")
                )
                try:
                    if hours_of_operation[-1] == ";":
                        hours_of_operation = "".join(hours_of_operation[:-1]).strip()
                except:
                    pass

                latitude = store_json["geo"]["latitude"]
                longitude = store_json["geo"]["longitude"]
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

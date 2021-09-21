# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
import us
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "securcareselfstorage.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36",
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
    base = "https://www.securcareselfstorage.com"
    search_url = "https://www.securcareselfstorage.com/storage"

    with SgRequests(dont_retry_status_codes=set([404])) as session:
        search_res = session.get(search_url, headers=headers)

        search_sel = lxml.html.fromstring(search_res.text)

        states = search_sel.xpath('//ul[@id="state-list"]//a')

        for state in states:

            state_url = "".join(state.xpath("./@href")).strip()
            state_url = base + state_url
            log.info(state_url)

            state_res = session.get(state_url, headers=headers)

            state_sel = lxml.html.fromstring(state_res.text)

            locator_domain = website

            stores = state_sel.xpath('//div[contains(@id,"facility")]')

            for store in stores:
                page_url = "".join(
                    store.xpath('./p[@class="facility-name"]/a/@href')
                ).strip()
                page_url = base + page_url
                if "istorage.com" in page_url:
                    continue
                log.info(page_url)

                store_res = session.get(page_url, headers=headers)

                store_sel = lxml.html.fromstring(store_res.text)
                location_name = "".join(
                    store.xpath('./p[@class="facility-name"]/a//text()')[:1]
                ).strip()

                full_address = list(
                    filter(
                        str,
                        [
                            x.strip()
                            for x in store.xpath(
                                './/p[@class="facility-address"]//text()'
                            )
                        ],
                    )
                )

                street_address, city, state, zip, country_code = split_fulladdress(
                    full_address
                )
                raw_address = "<MISSING>"
                store_number = (
                    store_res.text.split("siteId:")[0]
                    .split("var facility = {")[-1]
                    .split("id:")[1]
                    .split(",")[0]
                    .strip()
                )

                phone = "".join(
                    store.xpath('.//a[contains(@href,"tel:")]//text()')
                ).strip()

                location_type = "<MISSING>"

                hours = list(
                    filter(
                        str,
                        [
                            x.strip()
                            for x in store_sel.xpath(
                                '//div[contains(@class,"tab-pane")]//div[contains(@class,"office-hours")]//td//text()'
                            )
                        ],
                    )
                )
                hours_of_operation = (
                    "; ".join(hours)
                    .split("Holiday Hour")[0]
                    .replace("Fri;", "Fri:")
                    .replace("Sun;", "Sun:")
                    .replace("Sat;", "Sat:")
                    .strip(" ;")
                    .strip()
                )
                map_info = (
                    store_res.text.split("function initGoogleMap() ")[1]
                    .split("var facility = {")[1]
                    .split("};")[0]
                )

                latitude, longitude = (
                    map_info.split("latitude:")[1].split(",")[0].strip(),
                    map_info.split("longitude:")[1].strip(),
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

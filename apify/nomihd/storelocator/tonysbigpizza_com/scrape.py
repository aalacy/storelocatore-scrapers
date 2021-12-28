# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import us
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "tonysbigpizza.com"
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

    search_url = "https://tonysbigpizza.com/"

    with SgRequests(
        dont_retry_status_codes=set([404]), retries_with_fresh_proxy_ip=20
    ) as session:
        search_res = session.get(search_url, headers=headers)
        search_sel = lxml.html.fromstring(search_res.text)

        stores = search_sel.xpath('//ul[@class="list-location"]/li/a')

        for store in stores:

            page_url = "".join(store.xpath(".//@href")).strip()
            page_res = session.get(page_url, headers=headers)
            store_sel = lxml.html.fromstring(page_res.text)

            locator_domain = website

            location_name = "".join(store.xpath(".//text()")).strip()
            full_address = list(
                filter(
                    str,
                    [
                        x.strip()
                        for x in store_sel.xpath(
                            '//div[contains(@class,"location-container match")]/div[p]/p[not(a)]//text()'
                        )
                    ],
                )
            )
            street_address, city, state, zip, country_code = split_fulladdress(
                full_address
            )

            store_number = "<MISSING>"

            phone = "".join(
                store_sel.xpath('//p/a[contains(@href,"tel:")]//text()')
            ).strip()

            location_type = "<MISSING>"

            hours = list(
                filter(
                    str,
                    [
                        x.strip()
                        for x in store_sel.xpath(
                            '//div[contains(@class,"hours-container match")]/div[p]/p[not(a)]//text()'
                        )
                    ],
                )
            )
            hours_of_operation = "; ".join(hours)
            map_link = "".join(
                store_sel.xpath('//a[contains(@href,"/maps/dir/")]/@href')
            )
            latitude = "<MISSING>"
            longitude = "<MISSING>"
            try:
                latitude = map_link.split("/")[-1].strip().split(",")[0].strip()
            except:
                pass
            try:
                longitude = map_link.split("/")[-1].strip().split(",")[1].strip()
            except:
                pass
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

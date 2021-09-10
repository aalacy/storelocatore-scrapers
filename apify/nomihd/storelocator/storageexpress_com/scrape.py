# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
import us
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "storageexpress.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "authority": "www.storageexpress.com",
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

    if us.states.lookup(state):
        country_code = "US"

    return street_address, city, state, zip, country_code


def get_latlng(map_link):
    if "z/data" in map_link:
        lat_lng = map_link.split("@")[1].split("z/data")[0]
        latitude = lat_lng.split(",")[0].strip()
        longitude = lat_lng.split(",")[1].strip()
    elif "ll=" in map_link:
        lat_lng = map_link.split("ll=")[1].split("&")[0]
        latitude = lat_lng.split(",")[0]
        longitude = lat_lng.split(",")[1]
    elif "!2d" in map_link and "!3d" in map_link:
        latitude = map_link.split("!3d")[1].strip().split("!")[0].strip()
        longitude = map_link.split("!2d")[1].strip().split("!")[0].strip()
    elif "staticmap?" in map_link:
        latitude = map_link.split("C")[1].split(",")[0].strip()
        longitude = map_link.split("C")[1].split(",")[1].split("&")[0].strip()
    else:
        latitude = "<MISSING>"
        longitude = "<MISSING>"
    return latitude, longitude


def fetch_data():
    # Your scraper here
    search_url = "https://www.storageexpress.com/storage-units/?facilitySearch="
    search_res = session.get(search_url, headers=headers)

    search_sel = lxml.html.fromstring(search_res.text)
    states = search_sel.xpath('//div[@aria-labelledby="locationFinder"]//a')

    for state in states:

        state_url = "".join(state.xpath("./@href"))
        log.info(state_url)
        state_res = session.get(state_url, headers=headers)
        state_sel = lxml.html.fromstring(state_res.text)

        store_list = state_sel.xpath('//div[@aria-labelledby="list"]//div[@data-state]')
        for store in store_list:

            page_url = store.xpath(".//p[a]/a[1]/@href")[0].strip()

            locator_domain = website

            log.info(page_url)
            store_res = session.get(page_url, headers=headers)
            store_sel = lxml.html.fromstring(store_res.text)

            store_info = list(
                filter(
                    str,
                    [x.strip() for x in store.xpath(".//p[a]//text()")],
                )
            )

            raw_address = "<MISSING>"

            full_address = store_info[1:-1]
            street_address, city, state, zip, country_code = split_fulladdress(
                full_address
            )

            location_name = store_info[0].strip()

            phone = store_info[-1].strip()
            store_number = (
                store_res.text.split("'storeID':")[1].split("',")[0].strip("' ").strip()
            )

            location_type = "<MISSING>"

            hours_of_operation = (
                " ".join(
                    store_sel.xpath('//span[contains(@class,"fa-clock")]/..//text()')
                )
                .replace("Gate Access", "")
                .strip()
            )
            map_link = "".join(
                store_sel.xpath('//div[contains(@class,"facility-map")]//img/@data-src')
            ).strip()

            latitude, longitude = get_latlng(map_link)

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

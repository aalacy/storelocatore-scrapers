# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgpostal import sgpostal as parser
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "gant.com.au"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "authority": "gant.com.au",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "none",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "accept-language": "en-US,en;q=0.9,ar;q=0.8",
}


def fetch_data():
    # Your scraper here
    search_url = "https://gant.com.au/pages/stores"

    with SgRequests() as session:
        search_res = session.get(search_url, headers=headers)

        stores = search_res.text.split("store = {};")

        for store in stores[1:]:

            locator_domain = website

            store_info = store.split("storesBlock.push(store)")[0]

            location_name = (
                store_info.split("store.name =")[1].split(";")[0].strip('" ').strip()
            )

            location_type = "<MISSING>"

            raw_address = (
                store_info.split("store.address =")[1]
                .split(";")[0]
                .strip('" ')
                .strip()
                .replace("\\/", "/")
                .strip()
            )

            formatted_addr = parser.parse_address_intl(raw_address)
            street_address = formatted_addr.street_address_1
            if formatted_addr.street_address_2:
                street_address = street_address + ", " + formatted_addr.street_address_2

            if street_address is not None:
                street_address = street_address.replace("Ste", "Suite")
            city = " ".join(raw_address.split(",")[-1].strip().split(" ")[:-2]).strip()
            if not city:
                city = raw_address.split(",")[-2].strip()

            city = city.replace("Brisbane Airport", "Brisbane").strip()
            if "VIC" in city:
                city = location_name.replace("DFO", "").strip()

            state = formatted_addr.state
            state = (
                store_info.split("store.state =")[1].split(";")[0].strip('" ').strip()
            )

            zip = formatted_addr.postcode

            country_code = "AU"

            phone = (
                store_info.split("store.phone =")[1].split(";")[0].strip('" ').strip()
            )

            page_url = search_url
            hours = (
                store_info.split("store.hours =")[1].split(";")[0].strip('" ').strip()
            )
            hours_of_operation = "; ".join(hours.split("\\n"))

            store_number = "<MISSING>"
            map_info = (
                store_info.split("store.coords ")[1].split(";")[0].strip('" ').strip()
            )
            latitude, longitude = (
                map_info.split('lat: parseFloat("')[1].split('")')[0],
                map_info.split('lng: parseFloat("')[1].split('")')[0],
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
        deduper=SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()

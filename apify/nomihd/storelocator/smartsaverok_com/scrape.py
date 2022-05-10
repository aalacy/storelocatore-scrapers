# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


website = "smartsaverok.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "authority": "grocery.closerdesign.net",
    "sec-ch-ua": '"Chromium";v="94", "Google Chrome";v="94", ";Not A Brand";v="99"',
    "accept": "application/json, text/plain, */*",
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36",
    "sec-ch-ua-platform": '"Windows"',
    "origin": "https://smartsaverok.com",
    "sec-fetch-site": "cross-site",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "referer": "https://smartsaverok.com/",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def split_fulladdress(address_info):
    street_address = " ".join(address_info[0:-1]).strip(" ,.")

    city_state_zip = (
        address_info[-1].replace(",", " ").replace(".", " ").replace("  ", " ").strip()
    )

    city = " ".join(city_state_zip.split(" ")[:-2]).strip()
    state = city_state_zip.split(" ")[-2].strip()
    zip = city_state_zip.split(" ")[-1].strip()
    country_code = "US"
    return street_address, city, state, zip, country_code


def fetch_data():
    # Your scraper here
    search_url = "https://smartsaverok.com/locations"
    with SgRequests() as session:
        search_res = session.get(
            "https://grocery.closerdesign.net/stores/3", headers=headers
        )

        store_list = search_res.json()

        for store in store_list:

            page_url = search_url
            locator_domain = website

            location_name = store["name"]

            full_address = [store["address"], store["address2"]]

            street_address, city, state, zip, country_code = split_fulladdress(
                full_address
            )

            store_number = store["store_code"]
            phone = store["phone"]

            location_type = "<MISSING>"

            hours = store["store_hours"]
            hours_of_operation = (
                "".join(hours).replace(", until further notice", "").strip(" ,").strip()
            )
            latitude = store["latitude"]
            longitude = store["longitude"]

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
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PhoneNumberId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
